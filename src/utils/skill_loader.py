from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional


DEFAULT_MODULE_NAMES = (
    "persona",
    "policy",
    "tool_rules",
    "output_contract",
    "examples",
)


def get_default_skills_root() -> Path:
    return Path(__file__).resolve().parents[1] / "skills"


def load_skill_text(path: Path | str) -> Optional[str]:
    skill_path = Path(path)
    if not skill_path.exists() or not skill_path.is_file():
        return None
    return skill_path.read_text(encoding="utf-8").strip()


def _load_named_modules(base_dir: Path, module_names: Iterable[str]) -> Dict[str, str]:
    modules: Dict[str, str] = {}
    if not base_dir.exists():
        return modules

    for module_name in module_names:
        content = load_skill_text(base_dir / f"{module_name}.md")
        if content:
            modules[module_name] = content
    return modules


def load_shared_modules(
    skills_root: Path | str | None = None,
    module_names: Optional[Iterable[str]] = None,
) -> Dict[str, str]:
    root = Path(skills_root) if skills_root else get_default_skills_root()
    names = tuple(module_names) if module_names is not None else tuple(
        path.stem for path in sorted((root / "shared").glob("*.md"))
    )
    return _load_named_modules(root / "shared", names)


def load_skill_pack(
    agent_name: str,
    mode: Optional[str] = None,
    task: Optional[str] = None,
    skills_root: Path | str | None = None,
    module_names: Optional[Iterable[str]] = None,
) -> Dict[str, str]:
    root = Path(skills_root) if skills_root else get_default_skills_root()
    agent_root = root / agent_name
    names = tuple(module_names) if module_names is not None else DEFAULT_MODULE_NAMES

    candidate_dirs = []
    if mode and task:
        candidate_dirs.append(agent_root / mode / task)
    if task:
        candidate_dirs.append(agent_root / task)
    if mode:
        candidate_dirs.append(agent_root / mode)
    candidate_dirs.append(agent_root / "common")
    candidate_dirs.append(agent_root)

    modules: Dict[str, str] = {}
    for candidate_dir in reversed(candidate_dirs):
        modules.update(_load_named_modules(candidate_dir, names))

    return modules
