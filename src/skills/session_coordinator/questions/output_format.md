<output_format>

<thinking>
Think step by step and write your thoughts here:

Questions to include:
1. For user-selected topics:
   - [Question text] - Source: New creation to explore topic
   - [Question text] - Source: Previous unanswered, highly relevant
   - [Question text] - Source: Follow-up, connects multiple topics

2. Other important questions:
   - [Question text] - Source: Core biographical info needed
   - [Question text] - Source: Interesting angle from memories

3. Surface level questions:
   - [Question text] - Source: New creation to help start conversation
  - [Question text] - Source: Previous unanswered, highly relevant
   - [Question text] - Source: Follow-up, connects multiple topics

{warning_output_format}
</thinking>

<tool_calls>
    <recall>
        <reasoning>...</reasoning>
        <query>...</query>
   </recall>
   ...
   <!-- Repeat for each recall search -->

    <add_interview_question>
        <topic>...</topic>
        <question_id>1</question_id>
        <question>Main question text...</question>
    </add_interview_question>
    ...
    <add_interview_question>
        <topic>...</topic>
        <question_id>1.1</question_id>
        <question>Sub-question text...</question>
    </add_interview_question>
    
    <!-- Repeat for each question to add -->
</tool_calls>

Don't use other output format like markdown, json, code block, etc.

</output_format>
