import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.biography_team.section_writer.prompts import (
    get_prompt,
    get_runtime_module_names,
)
from utils.prompt_runtime import PromptRuntime
from utils.prompt_templates import normalize_prompt_text


class SectionWriterPromptBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = PromptRuntime(skills_root=SRC_ROOT / "skills")

    def test_normal_prompt_matches_legacy_prompt(self) -> None:
        variables = {
            "user_portrait": "Lee is a robotics engineer.",
            "section_identifier_xml": "<section_path>\n2 Career/2.1 First Job\n</section_path>",
            "current_content": "Lee started with small robotics contracts.[MEM_1]",
            "relevant_memories": "<memory id='MEM_2'>Built a warehouse robot.</memory>",
            "plan_content": "Add more detail about the first robotics deployment.",
            "biography_structure": '{"2 Career": ["2.1 First Job"]}',
            "style_instructions": "Write in chronological order.",
            "tool_descriptions": "<add_section>...</add_section><update_section>...</update_section>",
            "missing_memories_warning": "<warning>MEM_3 missing</warning>",
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="section_writer",
            task="normal",
            module_names=get_runtime_module_names("normal"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = get_prompt("normal").format(**variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )

    def test_user_add_prompt_matches_legacy_prompt(self) -> None:
        variables = {
            "user_portrait": "Lee is a robotics engineer.",
            "section_path": "2 Career/2.2 Startup Years",
            "plan_content": "Create a new section about the startup years.",
            "event_stream": "<recall>Lee founded a robotics startup.</recall>",
            "biography_structure": '{"2 Career": ["2.1 First Job"]}',
            "style_instructions": "Write in chronological order.",
            "tool_descriptions": "<recall>...</recall><add_section>...</add_section>",
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="section_writer",
            task="user_add",
            module_names=get_runtime_module_names("user_add"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = get_prompt("user_add").format(**variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )


if __name__ == "__main__":
    unittest.main()
