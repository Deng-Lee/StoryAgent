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

    def test_questions_prompt_matches_legacy_prompt_without_warning(self) -> None:
        variables = {
            "selected_topics": "Career transitions\nMentorship",
            "questions_and_notes": "[1] What was your first job in robotics?",
            "follow_up_questions": (
                "<follow_up_question>\n"
                "  <content>What made you stay in robotics after college?</content>\n"
                "</follow_up_question>"
            ),
            "event_stream": "<event>Recall found early-career memories.</event>",
            "similar_questions_warning": "",
            "warning_output_format": "",
            "tool_descriptions": (
                "<add_interview_question>...</add_interview_question>\n"
                "<recall>...</recall>"
            ),
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="session_coordinator",
            task="questions",
            module_names=get_runtime_module_names("questions"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = get_prompt("questions").format(**variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )

    def test_questions_prompt_matches_legacy_prompt_with_warning(self) -> None:
        variables = {
            "selected_topics": "Career transitions",
            "questions_and_notes": "[2] How did your manager support you?",
            "follow_up_questions": (
                "<follow_up_question>\n"
                "  <content>What changed after you started mentoring others?</content>\n"
                "</follow_up_question>"
            ),
            "event_stream": "<event>Recall found mentoring-related memories.</event>",
            "similar_questions_warning": (
                "<similar_questions_warning>\n"
                "Possible overlap with historical questions.\n"
                "</similar_questions_warning>"
            ),
            "warning_output_format": "<proceed>true</proceed>",
            "tool_descriptions": (
                "<add_interview_question>...</add_interview_question>\n"
                "<recall>...</recall>"
            ),
        }

        bundle = self.runtime.build_prompt_bundle(
            agent_name="session_coordinator",
            task="questions",
            module_names=get_runtime_module_names("questions"),
            include_shared=False,
        )

        runtime_prompt = self.runtime.render_prompt(bundle, variables)
        legacy_prompt = get_prompt("questions").format(**variables)

        self.assertEqual(
            normalize_prompt_text(runtime_prompt),
            normalize_prompt_text(legacy_prompt),
        )


if __name__ == "__main__":
    unittest.main()
