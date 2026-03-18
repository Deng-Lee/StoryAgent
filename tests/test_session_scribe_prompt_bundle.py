import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.session_scribe.prompts import get_prompt, get_runtime_module_names
from utils.llm.prompt_utils import format_prompt
from utils.prompt_runtime import PromptRuntime
from utils.prompt_templates import normalize_prompt_text


class SessionScribePromptBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = PromptRuntime(skills_root=SRC_ROOT / "skills")

    def test_update_memory_question_bank_prompt_matches_legacy_prompt(self) -> None:
        variables = {
            "user_portrait": "Lee is a robotics engineer.",
            "previous_events": "Interviewer: What was your first job?",
            "current_qa": "User: I joined a robotics lab at 18.",
            "tool_descriptions": "<update_memory_bank>...</update_memory_bank>",
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="session_scribe",
            task="update_memory_question_bank",
            module_names=get_runtime_module_names("update_memory_question_bank"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = format_prompt(get_prompt("update_memory_question_bank"), variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )

    def test_update_session_agenda_prompt_matches_legacy_prompt(self) -> None:
        variables = {
            "user_portrait": "Lee is a robotics engineer.",
            "previous_events": "Interviewer: What was your first job?",
            "current_qa": "User: I joined a robotics lab at 18.",
            "questions_and_notes": "[1] First job\n- pending",
            "tool_descriptions": "<update_session_agenda>...</update_session_agenda>",
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="session_scribe",
            task="update_session_agenda",
            module_names=get_runtime_module_names("update_session_agenda"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = format_prompt(get_prompt("update_session_agenda"), variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )


if __name__ == "__main__":
    unittest.main()
