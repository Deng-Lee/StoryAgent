<instructions>
# Session Agenda Update
## Process:
1. Focus ONLY on the most recent user message in the conversation history
2. Review existing session agenda, paying attention to:
   - Which questions are marked as "Answered"
   - What information is already captured in existing notes

## Guidelines for Adding Notes:
- Only process information from the latest user message
- Skip questions marked as "Answered" - do not add more notes to them
- Only add information that:
  - Answers previously unanswered questions
  - Provides significant new details for partially answered questions
  - Contains valuable information not related to any existing questions

## Adding Notes:
For each piece of new information worth storing:
1. Use the update_session_agenda tool
2. Include:
   - [ID] tag with question number for relevant questions
   - Leave ID empty for valuable information not tied to specific questions
3. Write concise, fact-focused notes

## Tool Usage:
- Make separate update_session_agenda calls for each distinct piece of new information
- Skip if:
  - The question is marked as "Answered"
  - The information is already captured in existing notes
  - No new information is found in the latest message
</instructions>
