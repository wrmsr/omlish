from .types import EnumToolDtype
from .types import MappingToolDtype
from .types import NullableToolDtype
from .types import PrimitiveToolDtype
from .types import SequenceToolDtype
from .types import ToolDtype
from .types import ToolSpec
from .types import TupleToolDtype
from .types import UnionToolDtype


##


class ToolJsonschemaRenderer:
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

        raise TypeError(t)

    def render_tool(self, fn: ToolSpec) -> dict:
        pr_dct: dict[str, dict] | None = None
        req_lst: list[str] | None = None
        if fn.params is not None:
            pr_dct = {}
            req_lst = []
            for p in fn.params or []:
                pr_dct[p.name] = {
                    **({'description': p.desc} if p.desc is not None else {}),
                    **(self.render_type(p.type) if p.type is not None else {}),
                }
                if p.required:
                    req_lst.append(p.name)

        pa_dct = {
            'type': 'object',
            **({'properties': pr_dct} if pr_dct is not None else {}),
            **({'required': req_lst} if req_lst is not None else {}),
            # By default any additional properties are allowed.
            # https://json-schema.org/understanding-json-schema/reference/object#additionalproperties
            **({'additionalProperties': False} if not fn.allow_additional_params else {}),
        }

        ret_dct = {
            **({'description': fn.returns_desc} if fn.returns_desc is not None else {}),
            **({'type': self.render_type(fn.returns_type)} if fn.returns_type is not None else {}),
        }

        return {
            'name': fn.name,
            **({'description': fn.desc} if fn.desc is not None else {}),
            **({'parameters': pa_dct} if pa_dct else {}),
            **({'return': ret_dct} if ret_dct else {}),
        }


##


def build_tool_spec_json_schema(ts: ToolSpec) -> dict:
    return ToolJsonschemaRenderer().render_tool(ts)
