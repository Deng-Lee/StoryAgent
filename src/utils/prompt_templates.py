from __future__ import annotations

import re
from typing import Any, Mapping, Sequence


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def safe_format_template(template: str, variables: Mapping[str, Any]) -> str:
    """Render a template without failing on missing variables."""
    if template is None:
        return ""

    return str(template).format_map(_SafeFormatDict(variables))


def normalize_prompt_text(text: str) -> str:
    """Trim noisy whitespace while keeping paragraph breaks intact."""
    if not text:
        return ""

    normalized = text.replace("\r\n", "\n")
    normalized = re.sub(r"[ \t]+\n", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def join_sections(sections: Sequence[str]) -> str:
    """Join non-empty prompt sections with stable spacing."""
    non_empty = [normalize_prompt_text(section) for section in sections if normalize_prompt_text(section)]
    return "\n\n".join(non_empty)
