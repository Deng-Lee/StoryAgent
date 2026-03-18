<output_format>

If you identify information worth storing, use the following format:
<tool_calls>
    <update_session_agenda>
        <question_id>...</question_id>
        <note>...</note>
    </update_session_agenda>
    ...
</tool_calls>

Reminder:
- You can make multiple tool calls at once if there are multiple pieces of information worth storing.
- If there's no information worth storing, don't make any tool calls; i.e. return <tool_calls></tool_calls>.

</output_format>
