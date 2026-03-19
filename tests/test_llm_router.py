import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from utils.llm.engines import invoke_engine_response, normalize_engine_response
from utils.llm.router import model_supports_native_tools, select_tool_call_protocol
from utils.llm.types import AgentResponse, ToolSpec


@dataclass
class FakeMessage:
    content: str
    tool_calls: list[dict] = field(default_factory=list)
    response_metadata: dict = field(default_factory=dict)


class FakeEngine:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def invoke(self, prompt, **kwargs):
        self.calls.append({"prompt": prompt, "kwargs": kwargs})
        return self.response


class LLMRouterTests(unittest.TestCase):
    def test_model_supports_native_tools_for_gpt4o_family(self) -> None:
        self.assertTrue(model_supports_native_tools("gpt-4o"))
        self.assertTrue(model_supports_native_tools("gpt-4o-mini"))
        self.assertFalse(model_supports_native_tools("gemini-1.5-pro"))

    def test_select_tool_call_protocol_prefers_native_for_interviewer(self) -> None:
        route = select_tool_call_protocol(
            model_name="gpt-4o",
            agent_name="Interviewer",
            has_tools=True,
        )
        self.assertEqual(route.protocol, "native")

    def test_select_tool_call_protocol_uses_xml_for_non_enabled_agents(self) -> None:
        route = select_tool_call_protocol(
            model_name="gpt-4o",
            agent_name="SessionScribe",
            has_tools=True,
        )
        self.assertEqual(route.protocol, "xml")
        self.assertIn("not enabled", route.reason)

    def test_select_tool_call_protocol_uses_xml_when_forced(self) -> None:
        route = select_tool_call_protocol(
            model_name="gpt-4o",
            agent_name="Interviewer",
            has_tools=True,
            force_xml=True,
        )
        self.assertEqual(route.protocol, "xml")
        self.assertEqual(route.reason, "force_xml enabled")

    def test_normalize_engine_response_supports_plain_text(self) -> None:
        response = normalize_engine_response("hello", protocol="xml")
        self.assertEqual(response.text, "hello")
        self.assertEqual(response.tool_calls, [])
        self.assertEqual(response.protocol, "xml")

    def test_normalize_engine_response_supports_native_tool_calls(self) -> None:
        raw_response = FakeMessage(
            content="I'll search first.",
            tool_calls=[
                {
                    "id": "call_1",
                    "function": {
                        "name": "recall",
                        "arguments": '{"query":"summer vacation","reasoning":"Need context"}',
                    },
                }
            ],
            response_metadata={"provider": "fake"},
        )

        response = normalize_engine_response(raw_response, protocol="native")

        self.assertEqual(response.text, "I'll search first.")
        self.assertEqual(len(response.tool_calls), 1)
        self.assertEqual(response.tool_calls[0].name, "recall")
        self.assertEqual(
            response.tool_calls[0].arguments,
            {"query": "summer vacation", "reasoning": "Need context"},
        )
        self.assertEqual(response.response_metadata["provider"], "fake")

    def test_invoke_engine_response_serializes_tool_specs_for_native_protocol(self) -> None:
        fake_engine = FakeEngine(FakeMessage(content="", tool_calls=[]))
        tools = [
            ToolSpec(
                name="respond_to_user",
                description="Send a response to the user.",
                json_schema={
                    "type": "object",
                    "properties": {"response": {"type": "string"}},
                    "required": ["response"],
                },
                required_fields=["response"],
            )
        ]

        response = invoke_engine_response(
            fake_engine,
            "Say hello",
            tools=tools,
            protocol="native",
        )

        self.assertIsInstance(response, AgentResponse)
        self.assertIn("tools", fake_engine.calls[0]["kwargs"])
        self.assertEqual(
            fake_engine.calls[0]["kwargs"]["tools"][0]["function"]["name"],
            "respond_to_user",
        )

    def test_invoke_engine_response_omits_tool_specs_for_xml_protocol(self) -> None:
        fake_engine = FakeEngine("plain text")

        response = invoke_engine_response(
            fake_engine,
            "Say hello",
            protocol="xml",
        )

        self.assertEqual(response.text, "plain text")
        self.assertNotIn("tools", fake_engine.calls[0]["kwargs"])


if __name__ == "__main__":
    unittest.main()
