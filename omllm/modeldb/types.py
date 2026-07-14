# ruff: noqa: UP007
"""https://github.com/anomalyco/models.dev/blob/64ea80d416e2fc9d4f205421c92b7a1dfec1f7fb/packages/core/src/schema.ts"""
import typing as ta

from omcore import dataclasses as dc
from omcore import marshal as msh


##


JsonValue: ta.TypeAlias = ta.Union[
    str,
    int,
    float,
    bool,
    None,
    ta.Mapping[str, 'JsonValue'],
    ta.Sequence['JsonValue'],
]

Modality: ta.TypeAlias = ta.Literal[
    'text',
    'audio',
    'image',
    'video',
    'pdf',
]

ProviderShape: ta.TypeAlias = ta.Literal[
    'responses',
    'completions',
]

ModelStatus: ta.TypeAlias = ta.Literal[
    'alpha',
    'beta',
    'deprecated',
]

InterleavedField: ta.TypeAlias = ta.Literal[
    'reasoning_content',
    'reasoning_details',
]

ModelFamily: ta.TypeAlias = str


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class Cost:
    input: float
    output: float
    reasoning: float | None = None
    cache_read: float | None = None
    cache_write: float | None = None
    input_audio: float | None = None
    output_audio: float | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class CostTierTier:
    size: int
    type: ta.Literal['context'] = 'context'

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class CostTier(Cost):
    tier: CostTierTier

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class AuthoredCost(Cost):
    context_over_200k: ta.Any | None = None
    tiers: ta.Sequence[CostTier] | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class OutputCost(Cost):
    context_over_200k: Cost | None = None
    tiers: ta.Sequence[CostTier] | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class Interleaved:
    field: InterleavedField

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class Modalities:
    input: ta.Sequence[Modality]
    output: ta.Sequence[Modality]

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class Limit:
    context: float
    output: float
    input: float | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options('body', **msh.kw_marshal_unmarshal_via(ta.Mapping[str, ta.Any] | None))
class ExperimentalModeProvider:
    body: ta.Mapping[str, JsonValue] | None = None
    headers: ta.Mapping[str, str] | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class ExperimentalMode:
    cost: Cost | None = None
    provider: ExperimentalModeProvider | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class Experimental:
    modes: ta.Mapping[str, ExperimentalMode] | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options('body', **msh.kw_marshal_unmarshal_via(ta.Mapping[str, ta.Any] | None))
@msh.update_object_options(unknown_field='x')
class ModelProvider:
    npm: str | None = None
    api: str | None = None
    shape: ProviderShape | None = None
    body: ta.Mapping[str, JsonValue] | None = None
    headers: ta.Mapping[str, str] | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ModelBase:
    id: str
    name: str
    attachment: bool
    reasoning: bool
    tool_call: bool
    release_date: str
    last_updated: str
    modalities: Modalities
    open_weights: bool
    limit: Limit
    family: ModelFamily | None = None
    interleaved: bool | Interleaved | None = None
    structured_output: bool | None = None
    temperature: bool | None = None
    knowledge: str | None = None
    status: ModelStatus | None = None
    experimental: Experimental | None = None
    provider: ModelProvider | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class Model(ModelBase):
    cost: OutputCost | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class AuthoredModel(ModelBase):
    cost: AuthoredCost | None = None

    x: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_options(unknown_field='x')
class Provider:
    id: str
    env: ta.Sequence[str]
    npm: str
    name: str
    doc: str
    models: ta.Mapping[str, Model]
    api: str | None = None

    x: ta.Mapping[str, ta.Any] | None = None
