<output_format>
<thinking>
1. Analyze Response Content:
   - Is this response worth storing? (Skip if just greetings/deflections)
   - How should I split this response into meaningful segments?
     * Look for natural breaks in topics, experiences, or time periods
     * Each split should be a complete, coherent thought
     * Example splits:
       Split 1: "I work at Google as a senior engineer..." → about current role
       Split 2: "Our team is developing a new AI model..." → about specific project
     * Verify: Does this cover the ENTIRE response while maintaining context?

2. Derived Questions Analysis:
   For each meaningful segment:
   - Split 1 (about current role):
     * What specific questions could we ask about their role at [specific company name]?
     * What aspects of their work at [specific company name] could be explored further?
   - Split 2 (about specific project):
     * What questions could we ask about this [specific project name/type]?
     * What technical or personal aspects could be explored?
   ...etc

3. Coverage Check:
   - Content Coverage:
     * Have I captured all key experiences/events?
     * Have I maintained specific details (names, places, dates)?
     * Have I preserved important context?
   - Question Coverage:
     * Is each memory linked to relevant questions?
     * Are the derived questions specific enough?
     * Do questions build on concrete details from the response?
</thinking>

<tool_calls>
    <!-- First call update_memory_bank for each piece of information -->
    <update_memory_bank>
        <temp_id>MEM_TEMP_1</temp_id>
        <title>Concise descriptive title</title>
        <text>Clear summary of the information</text>
        <metadata>{{"key 1": "value 1", "key 2": "value 2", ...}}</metadata>
        <importance_score>1-10</importance_score>
    </update_memory_bank>
    ...

    <!-- Then call add_historical_question for each answered question -->
    <add_historical_question>
        <content>The exact question that was asked</content>
        <temp_memory_ids>['MEM_TEMP_1', 'MEM_TEMP_2', ...]</temp_memory_ids>
    </add_historical_question>
    ...
</tool_calls>
</output_format>
