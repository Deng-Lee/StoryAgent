import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.biography_team.session_coordinator.prompts import get_prompt, get_runtime_module_names
from utils.prompt_runtime import PromptRuntime
from utils.prompt_templates import normalize_prompt_text


class SessionCoordinatorPromptBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = PromptRuntime(skills_root=SRC_ROOT / "skills")

    def test_summary_prompt_matches_legacy_prompt(self) -> None:
        variables = {
            "new_memories": (
                "<memory>\n"
                "  <content>Lee described how college robotics work shaped their career.</content>\n"
                "</memory>\n\n"
                "<memory>\n"
                "  <content>Lee also said they now mentor younger engineers.</content>\n"
                "</memory>"
            ),
            "user_portrait": "<field>Robotics engineer with a mentoring focus.</field>",
            "tool_descriptions": (
                "<update_last_meeting_summary>...</update_last_meeting_summary>\n"
                "<update_user_portrait>...</update_user_portrait>"
            ),
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="session_coordinator",
            task="summary",
            module_names=get_runtime_module_names("summary"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = get_prompt("summary").format(**variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )


if __name__ == "__main__":
    unittest.main()
