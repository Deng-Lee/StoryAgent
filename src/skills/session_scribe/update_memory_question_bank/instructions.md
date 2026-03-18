<instructions>

## Process:
1. First, analyze the user's response to identify important information:
   - Consider splitting long responses into MULTIPLE sequential parts
     * Each memory should cover one part of the user's direct response
     * Together, all memories should cover the ENTIRE user's response
   - For EACH piece of information worth storing:
     * Use the update_memory_bank tool with a unique temporary ID (e.g., MEM_TEMP_1)
     * Create a concise but descriptive title
     * Summarize the information clearly
     * Add relevant metadata (e.g., topics, emotions, when, where, who, etc.)
     * Rate the importance (1-10)

2. Then, analyze and store questions:
   - Consider MULTIPLE questions that this response answers:
     * The direct question that was asked
     * Derived questions from the response content
       Example:
       Direct question: "How do you like your job?"
       User response: "I started working here at 18 because I was fascinated by robotics..."
       Derived question: "What drew you to this field at such a young age?"
   - For EACH identified question:
     * Use add_historical_question to store it
     * Link it to ALL relevant memories using their temp_ids

## Memory-Question Relationship Rules:
1. Coverage Requirements:
   - Every temp_memory_id MUST be linked to at least one question
   - Each question MUST be linked to at least one memory
   - Together, all memories should represent the complete response

2. Linking Structure:
   - Many-to-many relationship allowed:
     * One memory can link to multiple questions
     * One question can link to multiple memories

## Content Quality Guidelines:
1. Avoid Ambiguity:
   - NO generic references like:
     * "the user" → Use the user's name if provided in <user_portrait>
     * "the project" → Use "Google's LLM project"
     * "the company" → Use "Microsoft"
     * "the team" → Use "AI Research team"
     * "the person" → Use "John Smith, the project lead"

2. Use Clear Language:
   - NO complex/abstract terms like:
     * "It greatly influenced the Amy"
   - Instead use simple, direct language:
     * "It motivated Amy to join Google"

## Tool Calling Sequence:
1. update_memory_bank (MULTIPLE calls):
   - One call per distinct piece of information
   - Use unique temp_ids (MEM_TEMP_1, MEM_TEMP_2, etc.)
   - Ensure complete coverage of the user's response

2. add_historical_question (MULTIPLE calls):
   - One call per answered question
   - Include ALL relevant temp_ids for each question
   - Ensure EVERY temp_id is used at least once

3. Skip all tool calls if the response:
   - Contains no meaningful information
   - Is just greetings or ice-breakers
   - Shows user deflection or non-answers
</instructions>
