import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.interviewer.prompts import get_prompt, get_runtime_module_names
from utils.llm.prompt_utils import format_prompt
from utils.prompt_runtime import PromptRuntime
from utils.prompt_templates import normalize_prompt_text


class InterviewerPromptBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = PromptRuntime(skills_root=SRC_ROOT / "skills")

    def test_normal_prompt_matches_legacy_prompt(self) -> None:
        variables = {
            "user_portrait": "User portrait",
            "last_meeting_summary": "Last meeting summary",
            "chat_history": "Interviewer: Hello\nUser: Hi",
            "current_events": "User: I remember summer vacations.",
            "questions_and_notes": "1. Favorite childhood place?",
            "tool_descriptions": "<respond_to_user>...</respond_to_user>",
            "recent_interviewer_messages": "How did that feel?",
            "conversation_starter": "",
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="interviewer",
            mode="normal",
            task="respond",
            module_names=get_runtime_module_names("normal"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = format_prompt(get_prompt("normal"), variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )

    def test_baseline_prompt_matches_legacy_prompt(self) -> None:
        variables = {
            "user_portrait": "User portrait",
            "last_meeting_summary": "Last meeting summary",
            "chat_history": "Interviewer: Hello\nUser: Hi",
            "current_events": "User: I remember summer vacations.",
            "tool_descriptions": "<respond_to_user>...</respond_to_user>",
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="interviewer",
            mode="baseline",
            task="respond",
            module_names=get_runtime_module_names("baseline"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = format_prompt(get_prompt("baseline"), variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )


if __name__ == "__main__":
    unittest.main()
