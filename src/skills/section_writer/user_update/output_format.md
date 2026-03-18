<output_format>
Choose one of the following:

1. To gather information:
Don't gather information if it is already provided in the <event_stream> tags.

<tool_calls>
    <recall>
        <reasoning>...</reasoning>
        <query>...</query>
    </recall>
</tool_calls>

2. To update the section:
Since the section title is already provided by the user, you can directly update the section by specifying the TITLE and content as below:

<tool_calls>
    <update_section>
        <title>{section_title}</title>
        <content>...</content>
    </update_section>
</tool_calls>
</output_format>
