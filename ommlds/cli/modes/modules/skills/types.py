import typing as ta

from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
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
