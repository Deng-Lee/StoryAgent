<output_format>

Your output should include the tools you need to call according to the following format.
- Wrap the tool calls in <tool_calls> tags as shown below
- No other text should be included in the output like thinking, reasoning, query, response, etc.
<tool_calls>
  # Option 1: If you need to gather information from the user:
  <recall>
      <reasoning>...</reasoning>
      <query>...</query>
  </recall>

  # Option 2: If you need to respond to the user:
  <respond_to_user>
      <response>value</response>
  </respond_to_user>
</tool_calls>

</output_format>
