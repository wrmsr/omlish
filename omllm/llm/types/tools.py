"""Tool definitions advertised to providers. `parameters` is a plain JSON Schema mapping."""
import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True, kw_only=True)
class Tool:
    name: str
    description: str
    parameters: ta.Mapping[str, ta.Any]
