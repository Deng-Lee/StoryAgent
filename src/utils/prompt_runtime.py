from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

from utils.prompt_templates import join_sections, safe_format_template
from utils.skill_loader import (
    DEFAULT_MODULE_NAMES,
    get_default_skills_root,
    load_shared_modules,
    load_skill_pack,
)


DEFAULT_SHARED_MODULES = (
    "safety",
    "response_style",
    "tool_calling_xml",
)


@dataclass(frozen=True)
class PromptModule:
    name: str
    content: str
    source_path: str
    required: bool = True


@dataclass
class PromptBundle:
    agent_name: str
    mode: Optional[str] = None
    task: Optional[str] = None
    modules: List[PromptModule] = field(default_factory=list)
    fallback_used: bool = False
    fallback_reason: Optional[str] = None


class PromptRuntime:
    def __init__(self, skills_root: Path | str | None = None):
        self.skills_root = Path(skills_root) if skills_root else get_default_skills_root()

    def build_prompt_bundle(
        self,
        agent_name: str,
        mode: Optional[str] = None,
        task: Optional[str] = None,
        module_names: Optional[Iterable[str]] = None,
        include_shared: bool = True,
        shared_module_names: Optional[Iterable[str]] = None,
    ) -> PromptBundle:
        modules: List[PromptModule] = []
        requested_module_names = tuple(module_names) if module_names is not None else DEFAULT_MODULE_NAMES
        requested_shared_modules = tuple(shared_module_names) if shared_module_names is not None else DEFAULT_SHARED_MODULES

        if include_shared:
            shared_modules = load_shared_modules(
                skills_root=self.skills_root,
                module_names=requested_shared_modules,
            )
            for module_name in requested_shared_modules:
                content = shared_modules.get(module_name)
                if content:
                    modules.append(
                        PromptModule(
                            name=f"shared.{module_name}",
                            content=content,
                            source_path=str(self.skills_root / "shared" / f"{module_name}.md"),
                            required=False,
                        )
                    )

        agent_modules = load_skill_pack(
            agent_name=agent_name,
            mode=mode,
            task=task,
            skills_root=self.skills_root,
            module_names=requested_module_names,
        )
        for module_name in requested_module_names:
            content = agent_modules.get(module_name)
            if content:
                modules.append(
                    PromptModule(
                        name=module_name,
                        content=content,
                        source_path=self._resolve_agent_source_path(
                            agent_name=agent_name,
                            mode=mode,
                            task=task,
                            module_name=module_name,
                        ),
                    )
                )

        fallback_used = not any(module.name in requested_module_names for module in modules)
        fallback_reason = None
        if fallback_used:
            fallback_reason = (
                f"No agent skill modules found for agent={agent_name}, mode={mode}, task={task}"
            )

        return PromptBundle(
            agent_name=agent_name,
            mode=mode,
            task=task,
            modules=modules,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
        )

    def render_prompt(
        self,
        bundle: PromptBundle,
        variables: Dict[str, object],
        legacy_renderer: Optional[Callable[[], str]] = None,
    ) -> str:
        if bundle.fallback_used and legacy_renderer is not None:
            return legacy_renderer()

        try:
            prompt_template = join_sections([module.content for module in bundle.modules])
            if not prompt_template and legacy_renderer is not None:
                return legacy_renderer()
            return safe_format_template(prompt_template, variables)
        except Exception:
            if legacy_renderer is not None:
                return legacy_renderer()
            raise

    def _resolve_agent_source_path(
        self,
        agent_name: str,
        mode: Optional[str],
        task: Optional[str],
        module_name: str,
    ) -> str:
        candidate_dirs = []
        agent_root = self.skills_root / agent_name
        if mode and task:
            candidate_dirs.append(agent_root / mode / task)
        if task:
            candidate_dirs.append(agent_root / task)
        if mode:
            candidate_dirs.append(agent_root / mode)
        candidate_dirs.append(agent_root / "common")
        candidate_dirs.append(agent_root)

        for candidate_dir in candidate_dirs:
            candidate_file = candidate_dir / f"{module_name}.md"
            if candidate_file.exists():
                return str(candidate_file)
        return str(agent_root / f"{module_name}.md")


def build_prompt_bundle(
    agent_name: str,
    mode: Optional[str] = None,
    task: Optional[str] = None,
    skills_root: Path | str | None = None,
    module_names: Optional[Iterable[str]] = None,
    include_shared: bool = True,
    shared_module_names: Optional[Iterable[str]] = None,
) -> PromptBundle:
    return PromptRuntime(skills_root=skills_root).build_prompt_bundle(
        agent_name=agent_name,
        mode=mode,
        task=task,
        module_names=module_names,
        include_shared=include_shared,
        shared_module_names=shared_module_names,
    )


def render_prompt(
    bundle: PromptBundle,
    variables: Dict[str, object],
    legacy_renderer: Optional[Callable[[], str]] = None,
) -> str:
    runtime = PromptRuntime()
    return runtime.render_prompt(
        bundle=bundle,
        variables=variables,
        legacy_renderer=legacy_renderer,
    )
