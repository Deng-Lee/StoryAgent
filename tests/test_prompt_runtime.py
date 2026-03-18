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
            agent_name="planner",
            mode="normal",
            task="draft",
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
