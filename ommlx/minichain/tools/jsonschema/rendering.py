from .types import Enum
from .types import Function
from .types import Mapping
from .types import Nullable
from .types import Primitive
from .types import Sequence
from .types import Tuple
from .types import Type
from .types import Union


##


class Renderer:
    def render_type(self, t: Type) -> dict:
        if isinstance(t, Primitive):
            return {'type': t.type}

        if isinstance(t, Union):
            return {
                'anyOf': [self.render_type(a) for a in t.args],
            }

        if isinstance(t, Nullable):
            return {
                **self.render_type(t.type),
                'nullable': True,
            }

        if isinstance(t, Sequence):
            return {
                'type': 'array',
                'items': self.render_type(t.element),
            }

        if isinstance(t, Mapping):
            # FIXME: t.key
            return {
                'type': 'object',
                'additionalProperties': self.render_type(t.value),
            }

        if isinstance(t, Tuple):
            return {
                'type': 'array',
                'prefixItems': [self.render_type(e) for e in t.elements],
            }

        if isinstance(t, Enum):
            return {
                **self.render_type(t.type),
                'enum': list(t.values),
            }

        raise TypeError(t)

    def render_function(self, fn: Function) -> dict:
        pr_dct: dict[str, dict] = {}
        req_lst: list[str] = []
        for p in fn.params or []:
            pr_dct[p.name] = {
                'name': p.name,
                **({'description': p.description} if p.description is not None else {}),
                **(self.render_type(p.type) if p.type is not None else {}),
            }
            if p.required:
                req_lst.append(p.name)

        pa_dct = {
            'type': 'object',
            **({'properties': pr_dct} if pr_dct else {}),
            **({'required': req_lst} if req_lst else {}),
        }

        ret_dct = {
            **({'description': fn.returns_description} if fn.returns_description is not None else {}),
            **({'type': self.render_type(fn.returns_type)} if fn.returns_type is not None else {}),
        }

        fn_dct = {
            'name': fn.name,
            **({'description': fn.description} if fn.description is not None else {}),
            **({'parameters': pa_dct} if pa_dct else {}),
            **({'return': ret_dct} if ret_dct else {}),
        }

        return {
            'type': 'function',
            'function': fn_dct,
        }
