# Question ID Constraints
- Question IDs must follow a hierarchical format (e.g., 1.2, 1.2.3)
- Maximum depth allowed is 4 levels (e.g., 1.2.3.4)
- If a question would exceed 4 levels, create it at the same level as its sibling instead
  Example: If parent is 1.2.3.4, new question should be 1.2.3.5 (not 1.2.3.4.1)

Follow the output format below to return your response:

<output_format>
<thinking>
Your reasoning process on reflecting on the available information and deciding on the action to take.
{warning_output_format}
</thinking>


<tool_calls>
    <!-- Option 1: Use recall tool to gather more information -->
    <recall>
        <reasoning>...</reasoning>
        <query>...</query>
    </recall>
    ...

    <!-- Option 2: Propose follow-up questions; leave empty tags if not proposing any -->
    <!-- MAX LEVELS is 4! JUST CREATE QUESTIONS AT THE SAME LEVEL AS THEIR SIBLINGS IF THEY EXCEED THIS -->
    <add_interview_question>
        <topic>Topic name</topic>
        <parent_id>ID of the parent question</parent_id>
        <parent_text>Full text of the parent question</parent_text>
        <question_id>ID in proper parent-child format. NEVER include a level 5 question id like '1.1.1.1.1'</question_id>
        <question>[FACT-GATHERING] or [DEEPER] or [TANGENTIAL] Your question here</question>
    </add_interview_question>
    ...
</tool_calls>
</output_format>

Reminder:
- If you decide not to propose any follow-up questions, just return <tool_calls></tool_calls> with empty tags
