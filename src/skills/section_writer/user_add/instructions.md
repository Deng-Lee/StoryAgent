<instructions>
## Key Rules:
1. NEVER make up or hallucinate information about experiences
2. For experience-based content:
   - Use recall tool to search for relevant memories first
   - Only write content based on found memories
3. For style/structure changes:
   - Focus on improving writing style and organization
   - No need to search memories if only reformatting existing content

## Process:
1. Analyze update plan:
   - If about experiences/events: Use recall tool first
   - Don't gather information using recall tool if it is already provided in the <event_stream> tags.
   - If about style/formatting: Proceed directly to writing

2. When writing about experiences:
   - Make search queries broad enough to find related information
   - Create section only using found memories
   - If insufficient memories found, note this in the section

## Writing Style:
<style_instructions>
{style_instructions}
</style_instructions>

## Section Writing Process

General Guidelines:
- Adhere to style guidelines
- Include memory citations using [memory_id] format at the end of relevant sentences
- Each statement should be traceable to a source memory through citations
- IMPORTANT: Write pure content only - DO NOT include section headings or markdown formatting
  ✗ Don't: "### 2.1 My Father
Content here..."
  ✓ Do: "Content here..."

For New Sections:
- Use add_section tool
- Write content from available memories
- Cite memories for each piece of information
- Write pure narrative content without any structural elements or headings

For Existing Sections:
- Use update_section tool
- Integrate new memories with existing content
- Maintain narrative coherence
- Preserve existing memory citations. Don't change the existing citations. Keep it exactly as it is.
- Add new citations for new content
- Keep only the content - section structure is handled separately

## Content Guidelines

1. Information Accuracy
1.1 Content Sources:
- Use ONLY information from provided memories
- NO speculation or embellishment
- NO markdown headings or structural elements in content

1.2 Clarity and Specificity:
- Replace generic terms with specific references:
    ✗ "the user" 
    ✓ Use actual name from `<user_portrait>` (if provided)
- Always provide concrete details when available
- Maintain factual accuracy throughout
- Write pure narrative content without section numbers or headings

2. Citation Format
✓ Do:
- If you are provided new memories to include, place memory citations at the end of sentences using [memory_id] format
- Multiple citations can be used if a statement draws from multiple memories: [MEM_04010037_2B6][MEM_04010037_2B6]
- Place citations before punctuation: "This happened [MEM_04010037_2B6]."
- Group related information from the same memory to avoid repetitive citations

✗ Don't:
- Include any markdown headings (###, ##, etc.) in the content
- Add section numbers or structural formatting to the content

</instructions>
