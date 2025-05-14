import typing as ta

from omlish import cached
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


ToolDtype: ta.TypeAlias = str


##


@dc.dataclass(frozen=True)
class ToolParam(lang.Final):
    name: str
    dtype: ToolDtype

    _: dc.KW_ONLY

    desc: str | None = None
    required: bool | None = None


@dc.dataclass(frozen=True)
class ToolSpec(lang.Final):
    name: str
    params: ta.Sequence[ToolParam]

    _: dc.KW_ONLY

    desc: str

    @cached.property
    @dc.init
    def params_by_name(self) -> ta.Mapping[str, ToolParam]:
        return col.make_map_by(lambda p: p.name, self.params, strict=True)


@dc.dataclass(frozen=True)
class ToolExecRequest(lang.Final):
    id: str
    spec: ToolSpec
    args: ta.Mapping[str, ta.Any]

    _: dc.KW_ONLY

    raw_args: str | None = None


##


class ToolParamJsonSchema(ta.TypedDict, total=False):
    type: str
    description: str


class ToolSpecParametersJsonSchema(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal['object']]
    properties: dict[str, ToolParamJsonSchema]
    required: list[str]
    additionalProperties: bool


class ToolSpecJsonSchema(ta.TypedDict, total=False):
    name: ta.Required[str]
    description: str
    parameters: ToolSpecParametersJsonSchema


def build_tool_spec_json_schema(
        ts: ToolSpec,
        *,
        omit_additional_properties_keyword: bool = False,
) -> ToolSpecJsonSchema:
    return dict(
        name=ts.name,

        **lang.truthy_kw(description=ts.desc),  # type: ignore[typeddict-item]

        parameters=dict(
            type='object',

            properties={
                tp.name: dict(
                    type=tp.dtype,

                    **lang.truthy_kw(description=tp.desc),
                )
                for tp in ts.params
            },

            required=[tp.name for tp in ts.params if tp.required],

            **(dict(additionalProperties=False) if not omit_additional_properties_keyword else {}),
        ),
    )
