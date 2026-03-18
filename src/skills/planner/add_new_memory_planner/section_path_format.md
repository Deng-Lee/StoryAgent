<format_notes>
# Important Note About Section Paths and Titles:

## Section Path Format:
- Section paths must be specified using forward slashes to indicate hierarchy
- Each part of the path MUST match existing section titles from <biography_structure> exactly
- Maximum 3 levels of hierarchy allowed
- Section numbers must be sequential and consistent:
  * You cannot create section "3" if sections "1" and "2" don't exist
  * You must use tool calls in sequence to create sections
  * Example: If only "1 Early Life" exists, the next section must be "2 Something"
- Numbering conventions:
  * First level sections must start with numbers: "1", "2", "3", etc.
    Examples: "1 Early Life" (must match a title from <biography_structure>)
  * Second level sections (subsections) use decimal notation matching parent number
    Examples: "1 Early Life/1.1 Childhood" (both must match titles from <biography_structure>)
  * Third level sections use double decimal notation matching parent number
    Examples: "1 Early Life/1.1 Childhood/1.1.1 Memories" (all must match titles from <biography_structure>)
- Examples of valid paths (assuming these titles exist in <biography_structure>):
  * "1 Early Life"
  * "1 Career/1.1 First Job"
- Examples of invalid paths:
  * "1 Early Life/1.1 Childhood/Stories" (missing third level number)
  * "1.1 Childhood" (subsection without parent section)
  * "1 Early Life/2.1 Childhood" (wrong parent number)
  * "1 Early Life/1.1 Childhood/1.1.1 Games/Types" (exceeds 3 levels)
  * "3 Career" (invalid if sections "1" and "2" don't exist)
  * "1 Early Years" (invalid if "Early Years" doesn't match exact title in <biography_structure>)

## Section Title Format:
- Section titles must be the last part of the section path
- Example: "1.1 Childhood" instead of full path
- All titles must match exactly with existing titles in <biography_structure>
</format_notes>
