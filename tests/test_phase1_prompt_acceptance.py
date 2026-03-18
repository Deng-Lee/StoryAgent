import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.interviewer.prompts import (
    get_prompt as get_interviewer_prompt,
    get_runtime_module_names as get_interviewer_runtime_module_names,
)
from agents.session_scribe.prompts import (
    get_prompt as get_session_scribe_prompt,
    get_runtime_module_names as get_session_scribe_runtime_module_names,
)
from agents.biography_team.planner.prompts import (
    get_prompt as get_planner_prompt,
    get_runtime_module_names as get_planner_runtime_module_names,
)
from agents.biography_team.section_writer.prompts import (
    get_prompt as get_section_writer_prompt,
    get_runtime_module_names as get_section_writer_runtime_module_names,
)
from agents.biography_team.session_coordinator.prompts import (
    get_prompt as get_session_coordinator_prompt,
    get_runtime_module_names as get_session_coordinator_runtime_module_names,
)
from content.biography.biography_styles import FIRST_PERSON_INSTRUCTIONS
from utils.llm.prompt_utils import format_prompt
from utils.prompt_runtime import PromptRuntime
from utils.prompt_templates import normalize_prompt_text


@dataclass(frozen=True)
class PromptAcceptanceCase:
    name: str
    agent_name: str
    task: str
    module_names: tuple[str, ...]
    variables: Dict[str, object]
    legacy_renderer: Callable[[Dict[str, object]], str]
    mode: Optional[str] = None


def build_phase1_cases() -> list[PromptAcceptanceCase]:
    return [
        PromptAcceptanceCase(
            name="interviewer.normal",
            agent_name="interviewer",
            mode="normal",
            task="respond",
            module_names=get_interviewer_runtime_module_names("normal"),
            variables={
                "user_portrait": "User portrait",
                "last_meeting_summary": "Last meeting summary",
                "chat_history": "Interviewer: Hello\nUser: Hi",
                "current_events": "User: I remember summer vacations.",
                "questions_and_notes": "1. Favorite childhood place?",
                "tool_descriptions": "<respond_to_user>...</respond_to_user>",
                "recent_interviewer_messages": "How did that feel?",
                "conversation_starter": "",
            },
            legacy_renderer=lambda variables: format_prompt(get_interviewer_prompt("normal"), variables),
        ),
        PromptAcceptanceCase(
            name="interviewer.baseline",
            agent_name="interviewer",
            mode="baseline",
            task="respond",
            module_names=get_interviewer_runtime_module_names("baseline"),
            variables={
                "user_portrait": "User portrait",
                "last_meeting_summary": "Last meeting summary",
                "chat_history": "Interviewer: Hello\nUser: Hi",
                "current_events": "User: I remember summer vacations.",
                "tool_descriptions": "<respond_to_user>...</respond_to_user>",
            },
            legacy_renderer=lambda variables: format_prompt(get_interviewer_prompt("baseline"), variables),
        ),
        PromptAcceptanceCase(
            name="session_scribe.update_memory_question_bank",
            agent_name="session_scribe",
            task="update_memory_question_bank",
            module_names=get_session_scribe_runtime_module_names("update_memory_question_bank"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "previous_events": "Interviewer: What was your first job?",
                "current_qa": "User: I joined a robotics lab at 18.",
                "tool_descriptions": "<update_memory_bank>...</update_memory_bank>",
            },
            legacy_renderer=lambda variables: format_prompt(
                get_session_scribe_prompt("update_memory_question_bank"),
                variables,
            ),
        ),
        PromptAcceptanceCase(
            name="session_scribe.update_session_agenda",
            agent_name="session_scribe",
            task="update_session_agenda",
            module_names=get_session_scribe_runtime_module_names("update_session_agenda"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "previous_events": "Interviewer: What was your first job?",
                "current_qa": "User: I joined a robotics lab at 18.",
                "questions_and_notes": "[1] First job\n- pending",
                "tool_descriptions": "<update_session_agenda>...</update_session_agenda>",
            },
            legacy_renderer=lambda variables: format_prompt(
                get_session_scribe_prompt("update_session_agenda"),
                variables,
            ),
        ),
        PromptAcceptanceCase(
            name="session_scribe.consider_and_propose_followups",
            agent_name="session_scribe",
            task="consider_and_propose_followups",
            module_names=get_session_scribe_runtime_module_names("consider_and_propose_followups"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "event_stream": "User: I loved working in that lab.",
                "questions_and_notes": "[1] Robotics work\n- pending",
                "similar_questions_warning": "<warning>similar questions found</warning>",
                "warning_output_format": "<proceed>true</proceed>",
                "tool_descriptions": "<recall>...</recall><add_interview_question>...</add_interview_question>",
            },
            legacy_renderer=lambda variables: format_prompt(
                get_session_scribe_prompt("consider_and_propose_followups"),
                variables,
            ),
        ),
        PromptAcceptanceCase(
            name="planner.add_new_memory_planner",
            agent_name="planner",
            task="add_new_memory_planner",
            module_names=get_planner_runtime_module_names("add_new_memory_planner"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "biography_structure": '{"1 Early Life": []}',
                "biography_content": "# Biography",
                "style_instructions": "Write in chronological order.",
                "new_information": "<memory>Built robots in college</memory>",
                "conversation_summary": "The user discussed their college robotics lab.",
                "missing_memories_warning": "<warning>MEM_1 missing</warning>",
                "tool_descriptions": "<add_plan>...</add_plan><propose_follow_up>...</propose_follow_up>",
            },
            legacy_renderer=lambda variables: get_planner_prompt("add_new_memory_planner").format(**variables),
        ),
        PromptAcceptanceCase(
            name="planner.user_add_planner",
            agent_name="planner",
            task="user_add_planner",
            module_names=get_planner_runtime_module_names("user_add_planner"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "biography_structure": '{"1 Early Life": []}',
                "biography_content": "# Biography",
                "style_instructions": "Write in chronological order.",
                "section_path": "2 Career/2.1 First Job",
                "section_prompt": "Add a section about the user's first job in robotics.",
                "tool_descriptions": "<add_plan>...</add_plan>",
            },
            legacy_renderer=lambda variables: get_planner_prompt("user_add_planner").format(**variables),
        ),
        PromptAcceptanceCase(
            name="planner.user_comment_planner",
            agent_name="planner",
            task="user_comment_planner",
            module_names=get_planner_runtime_module_names("user_comment_planner"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "biography_structure": '{"1 Early Life": []}',
                "biography_content": "# Biography",
                "style_instructions": "Write in chronological order.",
                "section_title": "2 Career",
                "selected_text": "Lee built robotics systems for industrial clients.",
                "user_comment": "Make this sound more personal and concrete.",
                "tool_descriptions": "<add_plan>...</add_plan>",
            },
            legacy_renderer=lambda variables: get_planner_prompt("user_comment_planner").format(**variables),
        ),
        PromptAcceptanceCase(
            name="section_writer.normal",
            agent_name="section_writer",
            task="normal",
            module_names=get_section_writer_runtime_module_names("normal"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "section_identifier_xml": "<section_path>\n2 Career/2.1 First Job\n</section_path>",
                "current_content": "Lee started with small robotics contracts.[MEM_1]",
                "relevant_memories": "<memory id='MEM_2'>Built a warehouse robot.</memory>",
                "plan_content": "Add more detail about the first robotics deployment.",
                "biography_structure": '{"2 Career": ["2.1 First Job"]}',
                "style_instructions": "Write in chronological order.",
                "tool_descriptions": "<add_section>...</add_section><update_section>...</update_section>",
                "missing_memories_warning": "<warning>MEM_3 missing</warning>",
            },
            legacy_renderer=lambda variables: get_section_writer_prompt("normal").format(**variables),
        ),
        PromptAcceptanceCase(
            name="section_writer.user_add",
            agent_name="section_writer",
            task="user_add",
            module_names=get_section_writer_runtime_module_names("user_add"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "section_path": "2 Career/2.2 Startup Years",
                "plan_content": "Create a new section about the startup years.",
                "event_stream": "<recall>Lee founded a robotics startup.</recall>",
                "biography_structure": '{"2 Career": ["2.1 First Job"]}',
                "style_instructions": "Write in chronological order.",
                "tool_descriptions": "<recall>...</recall><add_section>...</add_section>",
            },
            legacy_renderer=lambda variables: get_section_writer_prompt("user_add").format(**variables),
        ),
        PromptAcceptanceCase(
            name="section_writer.user_update",
            agent_name="section_writer",
            task="user_update",
            module_names=get_section_writer_runtime_module_names("user_update"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "section_title": "2 Career",
                "current_content": "Lee built robotics systems for industrial clients.[MEM_1]",
                "plan_content": "Rewrite this section to sound more personal and concrete.",
                "event_stream": "<recall>Lee described the first client deployment in detail.</recall>",
                "biography_structure": '{"2 Career": ["2.1 First Job"]}',
                "style_instructions": "Write in chronological order.",
                "tool_descriptions": "<recall>...</recall><update_section>...</update_section>",
            },
            legacy_renderer=lambda variables: get_section_writer_prompt("user_update").format(**variables),
        ),
        PromptAcceptanceCase(
            name="section_writer.baseline",
            agent_name="section_writer",
            task="baseline",
            module_names=get_section_writer_runtime_module_names("baseline"),
            variables={
                "user_portrait": "Lee is a robotics engineer.",
                "new_information": "<memory id='MEM_2'>Built a warehouse robot.</memory>",
                "current_biography": "# Biography\n\nExisting content.",
                "biography_structure": '{"2 Career": ["2.1 First Job"]}',
                "tool_descriptions": "<add_section>...</add_section><update_section>...</update_section>",
                "error_warning": "<warning>tool call failed</warning>",
                "first_person_instructions": FIRST_PERSON_INSTRUCTIONS,
            },
            legacy_renderer=lambda variables: get_section_writer_prompt("baseline").format(**variables),
        ),
        PromptAcceptanceCase(
            name="session_coordinator.summary",
            agent_name="session_coordinator",
            task="summary",
            module_names=get_session_coordinator_runtime_module_names("summary"),
            variables={
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
            },
            legacy_renderer=lambda variables: get_session_coordinator_prompt("summary").format(**variables),
        ),
        PromptAcceptanceCase(
            name="session_coordinator.questions",
            agent_name="session_coordinator",
            task="questions",
            module_names=get_session_coordinator_runtime_module_names("questions"),
            variables={
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
            },
            legacy_renderer=lambda variables: get_session_coordinator_prompt("questions").format(**variables),
        ),
        PromptAcceptanceCase(
            name="session_coordinator.topic_extraction",
            agent_name="session_coordinator",
            task="topic_extraction",
            module_names=get_session_coordinator_runtime_module_names("topic_extraction"),
            variables={
                "memories_text": (
                    "<memory>\n"
                    "  <content>Lee talked about early robotics competitions.</content>\n"
                    "</memory>\n\n"
                    "<memory>\n"
                    "  <content>Lee also reflected on mentoring younger engineers.</content>\n"
                    "</memory>"
                )
            },
            legacy_renderer=lambda variables: get_session_coordinator_prompt("topic_extraction").format(**variables),
        ),
    ]


class Phase1PromptAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skills_root = SRC_ROOT / "skills"
        self.cases = build_phase1_cases()

    def test_phase1_cases_cover_all_migrated_prompt_paths(self) -> None:
        self.assertEqual(len(self.cases), 15)

    def test_all_migrated_prompt_paths_render_from_real_skills(self) -> None:
        runtime = PromptRuntime(skills_root=self.skills_root)

        for case in self.cases:
            with self.subTest(case=case.name):
                bundle = runtime.build_prompt_bundle(
                    agent_name=case.agent_name,
                    mode=case.mode,
                    task=case.task,
                    module_names=case.module_names,
                    include_shared=False,
                )

                self.assertFalse(bundle.fallback_used)
                self.assertGreater(len(bundle.modules), 0)

                runtime_prompt = runtime.render_prompt(bundle, case.variables)
                legacy_prompt = case.legacy_renderer(case.variables)

                self.assertEqual(
                    normalize_prompt_text(runtime_prompt),
                    normalize_prompt_text(legacy_prompt),
                )

    def test_all_migrated_prompt_paths_fallback_to_legacy_when_skills_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runtime = PromptRuntime(skills_root=Path(tmpdir))

            for case in self.cases:
                with self.subTest(case=case.name):
                    bundle = runtime.build_prompt_bundle(
                        agent_name=case.agent_name,
                        mode=case.mode,
                        task=case.task,
                        module_names=case.module_names,
                        include_shared=False,
                    )
                    legacy_prompt = case.legacy_renderer(case.variables)
                    runtime_prompt = runtime.render_prompt(
                        bundle,
                        case.variables,
                        legacy_renderer=lambda prompt=legacy_prompt: prompt,
                    )

                    self.assertTrue(bundle.fallback_used)
                    self.assertEqual(runtime_prompt, legacy_prompt)


if __name__ == "__main__":
    unittest.main()
