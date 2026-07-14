import typing as ta

from omlish import dataclasses as dc

from ..configs import ModuleConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class SkillsConfig(ModuleConfig):
    skill_paths: ta.Sequence[str] | None = None

    @dc.validate
    def _validate_skill_paths(self) -> bool:
        return (sp := self.skill_paths) is None or not isinstance(sp, str)
