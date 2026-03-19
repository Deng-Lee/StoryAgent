<output_format>

Use native function calling for your next action.

- Do not emit XML such as `<tool_calls>` or tool tags in the text response.
- If you need more context, call `recall` with a concrete `reasoning` and `query`.
- If you are ready to continue the interview, call `respond_to_user` with the exact response text.
- Do not output extra wrapper text, markdown, or explanations outside the tool call arguments.

</output_format>
