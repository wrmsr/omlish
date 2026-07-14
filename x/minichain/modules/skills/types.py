import operator
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.truthy_repr)
@msh.update_object_options(field_naming=msh.Naming.KEBAB, field_defaults=msh.FieldOptions(omit_if=operator.not_))
class SkillHeader:
    # Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.
    name: str

    # Max 1024 characters. Non-empty. Describes what the skill does and when to use it.
    description: str

    # License name or reference to a bundled license file.
    license: str | None = None

    # Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.).
    compatibility: str | None = None

    # Arbitrary key-value mapping for additional metadata.
    metadata: ta.Mapping[str, ta.Any] | None = None

    # Space-delimited list of pre-approved tools the skill may use. (Experimental)
    allowed_tools: str | None = None


@dc.dataclass(frozen=True)
class Skill:
    header: SkillHeader
    body: str

    @property
    def name(self) -> str:
        return self.header.name

    @property
    def description(self) -> str:
        return self.header.description
