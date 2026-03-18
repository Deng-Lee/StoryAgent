import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.biography_team.planner.prompts import get_prompt, get_runtime_module_names
from utils.prompt_runtime import PromptRuntime
from utils.prompt_templates import normalize_prompt_text


class PlannerPromptBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = PromptRuntime(skills_root=SRC_ROOT / "skills")

    def test_add_new_memory_planner_prompt_matches_legacy_prompt(self) -> None:
        variables = {
            "user_portrait": "Lee is a robotics engineer.",
            "biography_structure": '{"1 Early Life": []}',
            "biography_content": "# Biography",
            "style_instructions": "Write in chronological order.",
            "new_information": "<memory>Built robots in college</memory>",
            "conversation_summary": "The user discussed their college robotics lab.",
            "missing_memories_warning": "<warning>MEM_1 missing</warning>",
            "tool_descriptions": "<add_plan>...</add_plan><propose_follow_up>...</propose_follow_up>",
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="planner",
            task="add_new_memory_planner",
            module_names=get_runtime_module_names("add_new_memory_planner"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = get_prompt("add_new_memory_planner").format(**variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )

    def test_user_add_planner_prompt_matches_legacy_prompt(self) -> None:
        variables = {
            "user_portrait": "Lee is a robotics engineer.",
            "biography_structure": '{"1 Early Life": []}',
            "biography_content": "# Biography",
            "style_instructions": "Write in chronological order.",
            "section_path": "2 Career/2.1 First Job",
            "section_prompt": "Add a section about the user's first job in robotics.",
            "tool_descriptions": "<add_plan>...</add_plan>",
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="planner",
            task="user_add_planner",
            module_names=get_runtime_module_names("user_add_planner"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = get_prompt("user_add_planner").format(**variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )


if __name__ == "__main__":
    unittest.main()
