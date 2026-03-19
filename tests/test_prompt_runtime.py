import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from utils.prompt_runtime import PromptRuntime, build_prompt_bundle
from utils.prompt_templates import join_sections, safe_format_template
from utils.skill_loader import load_shared_modules, load_skill_pack, load_skill_text


class PromptRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skills_root = SRC_ROOT / "skills"
        self.runtime = PromptRuntime(skills_root=self.skills_root)

    def test_safe_format_template_preserves_missing_values(self) -> None:
        rendered = safe_format_template(
            "Hello {name} from {city}",
            {"name": "Lee"},
        )
        self.assertEqual(rendered, "Hello Lee from {city}")

    def test_join_sections_skips_empty_sections(self) -> None:
        joined = join_sections(["alpha\n\n", "", "beta"])
        self.assertEqual(joined, "alpha\n\nbeta")

    def test_load_skill_text_returns_none_for_missing_file(self) -> None:
        missing = load_skill_text(self.skills_root / "shared" / "does_not_exist.md")
        self.assertIsNone(missing)

    def test_load_shared_modules_uses_real_skill_files(self) -> None:
        modules = load_shared_modules(self.skills_root)
        self.assertIn("safety", modules)
        self.assertIn("response_style", modules)
        self.assertIn("tool_calling_xml", modules)

    def test_load_skill_pack_prefers_mode_directory(self) -> None:
        modules = load_skill_pack(
            agent_name="interviewer",
            mode="normal",
            task="respond",
            skills_root=self.skills_root,
        )
        self.assertIn("persona", modules)
        self.assertIn("policy", modules)
        self.assertIn("tool_rules", modules)
        self.assertIn("output_contract", modules)

    def test_load_skill_pack_uses_common_modules_as_fallback(self) -> None:
        modules = load_skill_pack(
            agent_name="planner",
            task="user_add_planner",
            skills_root=self.skills_root,
            module_names=("persona", "context", "instructions", "output_format"),
        )
        self.assertIn("persona", modules)
        self.assertIn("context", modules)
        self.assertIn("instructions", modules)
        self.assertIn("output_format", modules)
        self.assertIn("analyze user's request", modules["persona"])

    def test_load_skill_pack_prefers_task_specific_modules_over_common(self) -> None:
        modules = load_skill_pack(
            agent_name="planner",
            task="user_comment_planner",
            skills_root=self.skills_root,
            module_names=("persona", "context", "instructions", "output_format"),
        )
        self.assertIn("section_title", modules["context"])
        self.assertNotIn("section_path", modules["context"])

    def test_load_skill_pack_merges_task_specific_and_common_modules(self) -> None:
        modules = load_skill_pack(
            agent_name="session_scribe",
            task="update_session_agenda",
            skills_root=self.skills_root,
            module_names=(
                "context",
                "event_stream",
                "questions_and_notes",
                "tool_descriptions",
                "instructions",
                "output_format",
            ),
        )
        self.assertIn("process ONLY the most recent user message", modules["context"])
        self.assertIn("Here is the stream of previous events for context", modules["event_stream"])
        self.assertIn("questions and notes in the session agenda", modules["questions_and_notes"])
        self.assertIn("manage session agenda", modules["tool_descriptions"])
        self.assertIn("Session Agenda Update", modules["instructions"])
        self.assertIn("<update_session_agenda>", modules["output_format"])

    def test_load_skill_pack_uses_session_coordinator_common_tool_descriptions(self) -> None:
        modules = load_skill_pack(
            agent_name="session_coordinator",
            task="summary",
            skills_root=self.skills_root,
            module_names=(
                "persona",
                "input_context",
                "tool_descriptions",
                "instructions",
                "output_format",
            ),
        )
        self.assertIn("session agenda manager", modules["persona"])
        self.assertIn("Available tools you can use", modules["tool_descriptions"])
        self.assertIn("<new_memories>", modules["input_context"])

    def test_load_skill_pack_merges_interviewer_mode_specific_and_common_modules(self) -> None:
        modules = load_skill_pack(
            agent_name="interviewer",
            mode="normal",
            task="respond",
            skills_root=self.skills_root,
            module_names=(
                "context",
                "user_portrait",
                "last_meeting_summary",
                "chat_history",
                "questions_and_notes",
                "tool_descriptions",
                "instructions",
                "output_format",
            ),
        )
        self.assertIn("friendly and casual conversation partner", modules["context"])
        self.assertIn("general information that you know about the user", modules["user_portrait"])
        self.assertIn("summary of the last interview session", modules["last_meeting_summary"])
        self.assertIn("Current Conversation", modules["chat_history"])
        self.assertIn("questions_and_notes", modules["questions_and_notes"])
        self.assertIn("memory bank", modules["tool_descriptions"])
        self.assertIn("<recent_interviewer_messages>", modules["instructions"])

    def test_load_skill_pack_merges_section_writer_instruction_prefix_and_common_tail(self) -> None:
        modules = load_skill_pack(
            agent_name="section_writer",
            task="user_update",
            skills_root=self.skills_root,
            module_names=(
                "persona",
                "user_portrait",
                "input_context",
                "instructions_intro",
                "instructions_shared",
                "available_tools",
                "output_format",
            ),
        )
        self.assertIn("Analyze user feedback in update plan", modules["instructions_intro"])
        self.assertIn("## Section Writing Process", modules["instructions_shared"])
        self.assertIn("## Writing Style:", modules["instructions_shared"])

    def test_build_prompt_bundle_orders_shared_before_agent_modules(self) -> None:
        bundle = build_prompt_bundle(
            agent_name="interviewer",
            mode="normal",
            task="respond",
            skills_root=self.skills_root,
        )

        self.assertFalse(bundle.fallback_used)
        self.assertEqual(
            [module.name for module in bundle.modules],
            [
                "shared.safety",
                "shared.response_style",
                "shared.tool_calling_xml",
                "persona",
                "policy",
                "tool_rules",
                "output_contract",
            ],
        )

    def test_render_prompt_substitutes_real_skill_variables(self) -> None:
        bundle = self.runtime.build_prompt_bundle(
            agent_name="interviewer",
            mode="normal",
            task="respond",
        )

        prompt = self.runtime.render_prompt(
            bundle,
            {
                "user_portrait": "Lee likes discussing concrete memories.",
                "chat_history": "User: I remember my first apartment.",
                "tool_descriptions": "<respond_to_user>...</respond_to_user>",
            },
        )

        self.assertIn("Lee likes discussing concrete memories.", prompt)
        self.assertIn("User: I remember my first apartment.", prompt)
        self.assertIn("<respond_to_user>...</respond_to_user>", prompt)
        self.assertIn("<tool_protocol>", prompt)

    def test_render_prompt_falls_back_to_legacy_renderer_when_agent_skill_missing(self) -> None:
        bundle = self.runtime.build_prompt_bundle(
            agent_name="does_not_exist",
        )

        prompt = self.runtime.render_prompt(
            bundle,
            {},
            legacy_renderer=lambda: "legacy planner prompt",
        )

        self.assertTrue(bundle.fallback_used)
        self.assertEqual(prompt, "legacy planner prompt")


if __name__ == "__main__":
    unittest.main()
