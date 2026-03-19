import sys
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.interviewer.interviewer import Interviewer
from content.memory_bank.memory_bank_base import MemoryBankBase
from interview_session.session_models import Message, MessageType
from utils.llm.types import AgentResponse, ToolCall


class FakeMemoryBank(MemoryBankBase):
    def add_memory(
        self,
        title: str,
        text: str,
        importance_score: int,
        source_interview_response: str,
        metadata=None,
        question_ids=None,
    ):
        raise NotImplementedError

    def search_memories(self, query: str):
        return []

    def _save_implementation_specific(self, path: str) -> None:
        return None

    def _load_implementation_specific(self, user_id: str, base_path=None) -> None:
        return None


class FakeSessionAgenda:
    session_id = 1

    def get_user_portrait_str(self):
        return "Lee is a robotics engineer."

    def get_last_meeting_summary_str(self):
        return "Lee discussed early robotics work."

    def get_questions_and_notes_str(self, hide_answered=None):
        return "[1] What was your first robotics project?"


class FakeInterviewSession:
    def __init__(self):
        self.memory_bank = FakeMemoryBank()
        self.session_agenda = FakeSessionAgenda()
        self.session_id = "2"
        self.chat_history = []

    def add_message_to_chat_history(self, role: str, content: str = ""):
        self.chat_history.append({"role": role, "content": content})


class FakeEngine:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def invoke(self, prompt, **kwargs):
        self.calls.append({"prompt": prompt, "kwargs": kwargs})
        if not self.responses:
            raise RuntimeError("No fake responses left")
        return self.responses.pop(0)


class InterviewerFunctionCallingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.get_engine_patcher = patch("agents.base_agent.get_engine", return_value=object())
        self.logger_patcher = patch("agents.base_agent.SessionLogger.log_to_file", return_value=None)
        self.interviewer_logger_patcher = patch("agents.interviewer.interviewer.SessionLogger.log_to_file", return_value=None)
        self.get_engine_patcher.start()
        self.logger_patcher.start()
        self.interviewer_logger_patcher.start()
        self.session = FakeInterviewSession()
        self.interviewer = Interviewer(
            config={"user_id": "lee", "tts": {}, "model_name": "gpt-4o"},
            interview_session=self.session,
        )

    def tearDown(self) -> None:
        self.get_engine_patcher.stop()
        self.logger_patcher.stop()
        self.interviewer_logger_patcher.stop()

    async def test_interviewer_executes_native_recall_then_native_response(self) -> None:
        self.interviewer.engine = FakeEngine([
            AgentResponse(
                protocol="native",
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="recall",
                        arguments={"query": "summer vacation", "reasoning": "Find prior context"},
                        source="native",
                    )
                ],
            ),
            AgentResponse(
                protocol="native",
                tool_calls=[
                    ToolCall(
                        id="call_2",
                        name="respond_to_user",
                        arguments={"response": "What do you remember most about that summer?"},
                        source="native",
                    )
                ],
            ),
        ])

        await self.interviewer.on_message(
            Message(
                id="1",
                type=MessageType.CONVERSATION,
                role="User",
                content="I loved spending summers at the beach.",
                timestamp=datetime.now(),
            )
        )

        self.assertEqual(self.session.chat_history[-1]["role"], "Interviewer")
        self.assertIn("summer", self.session.chat_history[-1]["content"].lower())
        self.assertTrue(
            any(event.tag == "recall" for event in self.interviewer.event_stream),
        )
        self.assertIn("tools", self.interviewer.engine.calls[0]["kwargs"])

    async def test_interviewer_uses_xml_fallback_when_model_not_native_enabled(self) -> None:
        self.interviewer.config["model_name"] = "gemini-1.5-pro"
        self.interviewer.engine = FakeEngine([
            """<tool_calls>
<respond_to_user>
  <response>Tell me more about that memory.</response>
</respond_to_user>
</tool_calls>"""
        ])

        await self.interviewer.on_message(
            Message(
                id="2",
                type=MessageType.CONVERSATION,
                role="User",
                content="I remember my first job clearly.",
                timestamp=datetime.now(),
            )
        )

        self.assertEqual(self.session.chat_history[-1]["content"], "Tell me more about that memory.")
        self.assertNotIn("tools", self.interviewer.engine.calls[0]["kwargs"])

    async def test_interviewer_uses_plain_text_response_when_no_tool_calls_returned(self) -> None:
        self.interviewer.engine = FakeEngine([
            AgentResponse(
                text="Thanks for sharing that. What happened next?",
                protocol="native",
                tool_calls=[],
            )
        ])

        await self.interviewer.on_message(
            Message(
                id="3",
                type=MessageType.CONVERSATION,
                role="User",
                content="I was nervous during that interview.",
                timestamp=datetime.now(),
            )
        )

        self.assertEqual(
            self.session.chat_history[-1]["content"],
            "Thanks for sharing that. What happened next?",
        )
        self.assertFalse(self.interviewer._turn_to_respond)

    def test_interviewer_native_prompt_uses_native_output_format(self) -> None:
        prompt = self.interviewer._get_prompt(protocol="native", selected_tools=["recall", "respond_to_user"])
        self.assertIn("Use native function calling", prompt)
        self.assertNotIn("Wrap the tool calls in <tool_calls>", prompt)


if __name__ == "__main__":
    unittest.main()
