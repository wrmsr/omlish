"""
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc

from .....backends.google.protocol import types as pt
from ....content.prepare import ContentStrPreparer
from ....content.prepare import default_content_str_preparer
from ....tools.types import EnumToolDtype
from ....tools.types import MappingToolDtype
from ....tools.types import NullableToolDtype
from ....tools.types import ObjectToolDtype
from ....tools.types import PrimitiveToolDtype
from ....tools.types import SequenceToolDtype
from ....tools.types import ToolDtype
from ....tools.types import ToolSpec
from ....tools.types import TupleToolDtype
from ....tools.types import UnionToolDtype


##


def _shallow_dc_asdict_not_none(o: ta.Any) -> dict[str, ta.Any]:
    return {k: v for k, v in dc.shallow_asdict(o).items() if v is not None}


PT_TYPE_BY_PRIMITIVE_TYPE: ta.Mapping[str, pt.Type] = {
    'string': 'STRING',
    'number': 'NUMBER',
    'integer': 'INTEGER',
    'boolean': 'BOOLEAN',
    'array': 'ARRAY',
    'null': 'NULL',
}


class ToolSchemaRenderer:
    def __init__(
            self,
            *,
            content_str_preparer: ContentStrPreparer | None = None,
    ) -> None:
        super().__init__()

        if content_str_preparer is None:
            content_str_preparer = default_content_str_preparer()
        self._content_str_preparer = content_str_preparer

    def render_type(self, t: ToolDtype) -> pt.Schema:
        if isinstance(t, PrimitiveToolDtype):
            return pt.Schema(type=PT_TYPE_BY_PRIMITIVE_TYPE[t.type])

        if isinstance(t, UnionToolDtype):
            return pt.Schema(
                any_of=[self.render_type(a) for a in t.args],
            )

        if isinstance(t, NullableToolDtype):
            return pt.Schema(**{
                **_shallow_dc_asdict_not_none(self.render_type(t.type)),
                **dict(nullable=True),
            })

        if isinstance(t, SequenceToolDtype):
            return pt.Schema(
                type='ARRAY',
                items=self.render_type(t.element),
            )

        if isinstance(t, MappingToolDtype):
            # FIXME: t.key
            # return {
            #     'type': 'object',
            #     'additionalProperties': self.render_type(t.value),
            # }
            raise NotImplementedError

        if isinstance(t, TupleToolDtype):
            # return {
            #     'type': 'array',
            #     'prefixItems': [self.render_type(e) for e in t.elements],
            # }
            raise NotImplementedError

        if isinstance(t, EnumToolDtype):
            return pt.Schema(**{
                **_shallow_dc_asdict_not_none(self.render_type(t.type)),
                **dict(enum=list(t.values)),
            })

        if isinstance(t, ObjectToolDtype):
            return pt.Schema(
                type='OBJECT',
                properties={
                    k: self.render_type(v)
                    for k, v in t.fields.items()
                },
            )

        raise TypeError(t)

    def render_tool_params(self, ts: ToolSpec) -> pt.Schema:
        pr_dct: dict[str, pt.Schema] | None = None
        req_lst: list[str] | None = None
        if ts.params is not None:
            pr_dct = {}
            req_lst = []
            for p in ts.params or []:
                pr_dct[check.non_empty_str(p.name)] = pt.Schema(**{
                    **(dict(description=self._content_str_preparer.prepare_str(p.desc)) if p.desc is not None else {}),
                    **(_shallow_dc_asdict_not_none(self.render_type(p.type)) if p.type is not None else {}),
                })
                if p.required:
                    req_lst.append(check.non_empty_str(p.name))

        return pt.Schema(
            type='OBJECT',
            **(dict(properties=pr_dct) if pr_dct is not None else {}),  # type: ignore[arg-type]
            **(dict(required=req_lst) if req_lst is not None else {}),  # type: ignore[arg-type]
        )

    def render_tool(self, ts: ToolSpec) -> pt.FunctionDeclaration:
        ret_dct = {
            **(dict(description=self._content_str_preparer.prepare_str(ts.returns_desc)) if ts.returns_desc is not None else {}),  # noqa
            **(_shallow_dc_asdict_not_none(self.render_type(ts.returns_type)) if ts.returns_type is not None else {}),
        }

        return pt.FunctionDeclaration(
            name=check.non_empty_str(ts.name),
            description=self._content_str_preparer.prepare_str(ts.desc) if ts.desc is not None else None,  # type: ignore[arg-type]  # noqa
            behavior='BLOCKING',
            parameters=self.render_tool_params(ts) if ts.params else None,
            response=(pt.Schema(**ret_dct) if ret_dct else None),
        )


##


def build_tool_spec_schema(ts: ToolSpec) -> pt.FunctionDeclaration:
    return ToolSchemaRenderer().render_tool(ts)


def build_tool_spec_params_schema(ts: ToolSpec) -> pt.Schema:
    return ToolSchemaRenderer().render_tool_params(ts)
