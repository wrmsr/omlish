import dataclasses as dc
import inspect
import typing as ta

from ... import lang
from .exceptions import CheckException
from .fields import field_init
from .fields import field_type
from .internals import FieldType
from .internals import HAS_DEFAULT_FACTORY
from .internals import POST_INIT_NAME
from .internals import Params
from .metadata import Check
from .metadata import Init
from .metadata import Metadata
from .params import Params12
from .utils import Namespace
from .utils import create_fn


MISSING = dc.MISSING


def fields_in_init_order(fields: ta.Sequence[dc.Field]) -> tuple[ta.Sequence[dc.Field], ta.Sequence[dc.Field]]:
    return (
        tuple(f for f in fields if f.init and not f.kw_only),
        tuple(f for f in fields if f.init and f.kw_only),
    )


class InitFields(ta.NamedTuple):
    all: ta.Sequence[dc.Field]
    std: ta.Sequence[dc.Field]
    kw_only: ta.Sequence[dc.Field]


def get_init_fields(fields: ta.Iterable[dc.Field]) -> InitFields:
    all_init_fields = [f for f in fields if field_type(f) in (FieldType.INSTANCE, FieldType.INIT)]
    std_init_fields, kw_only_init_fields = fields_in_init_order(all_init_fields)
    return InitFields(
        all=all_init_fields,
        std=std_init_fields,
        kw_only=kw_only_init_fields,
    )


def init_param(f: dc.Field) -> str:
    if f.default is MISSING and f.default_factory is MISSING:
        default = ''
    elif f.default is not MISSING:
        default = f' = __dataclass_dflt_{f.name}__'
    elif f.default_factory is not MISSING:
        default = ' = __dataclass_HAS_DEFAULT_FACTORY__'
    return f'{f.name}: __dataclass_type_{f.name}__{default}'  # noqa


class InitBuilder:

    def __init__(
            self,
            params: Params,
            params12: Params12,
            merged_metadata: Metadata,
            fields: ta.Mapping[str, dc.Field],
            has_post_init: bool,
            self_name: str,
            globals: Namespace,
    ) -> None:
        super().__init__()

        self._params = params
        self._params12 = params12
        self._merged_metadata = merged_metadata
        self._fields = fields
        self._has_post_init = has_post_init
        self._self_name = self_name
        self._globals = globals

    @lang.cached_nullary
    def build(self) -> ta.Callable:
        ifs = get_init_fields(self._fields.values())

        seen_default = None
        for f in ifs.std:
            if f.init:
                if not (f.default is MISSING and f.default_factory is MISSING):
                    seen_default = f
                elif seen_default:
                    raise TypeError(f'non-default argument {f.name!r} follows default argument {seen_default.name!r}')

        locals = {f'__dataclass_type_{f.name}__': f.type for f in ifs.all}
        locals.update({
            '__dataclass_HAS_DEFAULT_FACTORY__': HAS_DEFAULT_FACTORY,
            '__dataclass_builtins_object__': object,
            '__dataclass_CheckException__': CheckException,
        })

        body_lines: list[str] = []
        for f in ifs.all:
            f_lines = field_init(
                f,
                self._params.frozen,
                locals,
                self._self_name,
                self._params12.slots,
            )

            if f_lines:
                body_lines.extend(f_lines)

        if self._has_post_init:
            params_str = ','.join(f.name for f in ifs.all if field_type(f) is FieldType.INIT)
            body_lines.append(f'{self._self_name}.{POST_INIT_NAME}({params_str})')

        for i, fn in enumerate(self._merged_metadata.get(Check, [])):
            if isinstance(fn, staticmethod):
                fn = fn.__func__
            cn = f'__dataclass_check_{i}__'
            locals[cn] = fn
            csig = inspect.signature(fn)
            cas = ', '.join(p.name for p in csig.parameters.values())
            body_lines.append(f'if not {cn}({cas}): raise __dataclass_CheckException__')

        for i, fn in enumerate(self._merged_metadata.get(Init, [])):
            cn = f'__dataclass_init_{i}__'
            locals[cn] = fn
            body_lines.append(f'{cn}({self._self_name})')

        if not body_lines:
            body_lines = ['pass']

        _init_params = [init_param(f) for f in ifs.std]
        if ifs.kw_only:
            _init_params += ['*']
            _init_params += [init_param(f) for f in ifs.kw_only]

        return create_fn(
            '__init__',
            [self._self_name] + _init_params,
            body_lines,
            locals=locals,
            globals=self._globals,
            return_type=lang.just(None),
        )
