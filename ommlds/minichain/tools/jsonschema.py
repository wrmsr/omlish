"""
TODO:
 - '$schema': 'http://json-schema.org/draft-07/schema#'
"""
from omlish import check

from ..content.prepare import ContentStrPreparer
from ..content.prepare import default_content_str_preparer
from .types import EnumToolDtype
from .types import MappingToolDtype
from .types import NullableToolDtype
from .types import ObjectToolDtype
from .types import PrimitiveToolDtype
from .types import SequenceToolDtype
from .types import ToolDtype
from .types import ToolSpec
from .types import TupleToolDtype
from .types import UnionToolDtype


##


class ToolJsonschemaRenderer:
    def __init__(
            self,
            *,
            content_str_preparer: ContentStrPreparer | None = None,
    ) -> None:
        super().__init__()

        if content_str_preparer is None:
            content_str_preparer = default_content_str_preparer()
        self._content_str_preparer = content_str_preparer

    def render_type(self, t: ToolDtype) -> dict:
        if isinstance(t, PrimitiveToolDtype):
            return {'type': t.type}

        if isinstance(t, UnionToolDtype):
            return {
                'anyOf': [self.render_type(a) for a in t.args],
            }

        if isinstance(t, NullableToolDtype):
            return {
                **self.render_type(t.type),
                'nullable': True,
            }

        if isinstance(t, SequenceToolDtype):
            return {
                'type': 'array',
                'items': self.render_type(t.element),
            }

        if isinstance(t, MappingToolDtype):
            # FIXME: t.key
            return {
                'type': 'object',
                'additionalProperties': self.render_type(t.value),
            }

        if isinstance(t, TupleToolDtype):
            return {
                'type': 'array',
                'prefixItems': [self.render_type(e) for e in t.elements],
            }

        if isinstance(t, EnumToolDtype):
            return {
                **self.render_type(t.type),
                'enum': list(t.values),
            }

        if isinstance(t, ObjectToolDtype):
            return {
                'type': 'object',
                'properties': {
                    k: self.render_type(v)
                    for k, v in t.fields.items()
                },
            }

        raise TypeError(t)

    def render_tool_params(self, ts: ToolSpec) -> dict:
        pr_dct: dict[str, dict] = {}
        req_lst: list[str] | None = None
        if ts.params:
            req_lst = []
            for p in ts.params:
                pr_dct[check.non_empty_str(p.name)] = {
                    **({'description': self._content_str_preparer.prepare_str(p.desc)} if p.desc is not None else {}),
                    **(self.render_type(p.type) if p.type is not None else {}),
                }
                if p.required:
                    req_lst.append(check.non_empty_str(p.name))

        return {
            'type': 'object',
            'properties': pr_dct,
            **({'required': req_lst} if req_lst is not None else {}),
            # By default any additional properties are allowed.
            # https://json-schema.org/understanding-json-schema/reference/object#additionalproperties
            **({'additionalProperties': False} if not ts.allow_additional_params else {}),
        }

    def render_tool(self, ts: ToolSpec) -> dict:
        pa_dct = self.render_tool_params(ts)

        ret_dct = {
            **({'description': self._content_str_preparer.prepare_str(ts.returns_desc)} if ts.returns_desc is not None else {}),  # noqa
            **({'type': self.render_type(ts.returns_type)} if ts.returns_type is not None else {}),
        }

        return {
            'name': ts.name,
            **({'description': self._content_str_preparer.prepare_str(ts.desc)} if ts.desc is not None else {}),
            **({'parameters': pa_dct} if pa_dct else {}),
            **({'return': ret_dct} if ret_dct else {}),
        }


##


def build_tool_spec_json_schema(ts: ToolSpec) -> dict:
    return ToolJsonschemaRenderer().render_tool(ts)


def build_tool_spec_params_json_schema(ts: ToolSpec) -> dict:
    return ToolJsonschemaRenderer().render_tool_params(ts)
