import dataclasses as dc
import inspect
import typing as ta

from ... import lang
from .exceptions import ValidationError
from .fields import field_init
from .fields import field_type
from .fields import has_default
from .fields import raise_field_validation_error
from .internals import HAS_DEFAULT_FACTORY
from .internals import POST_INIT_NAME
from .internals import FieldType
from .metadata import Init
from .metadata import Validate
from .processing import Processor
from .reflect import ClassInfo
from .utils import Namespace
from .utils import create_fn
from .utils import set_new_attribute


MISSING = dc.MISSING


##


def raise_validation_error(
        obj: ta.Any,
        fn: ta.Callable,
) -> ta.NoReturn:
    raise ValidationError(obj, fn)


##


class InitFields(ta.NamedTuple):
    all: ta.Sequence[dc.Field]
    ordered: ta.Sequence[dc.Field]
    std: ta.Sequence[dc.Field]
    kw_only: ta.Sequence[dc.Field]


def get_init_fields(fields: ta.Iterable[dc.Field], *, reorder: bool = False) -> InitFields:
    all_init_fields = [f for f in fields if field_type(f) in (FieldType.INSTANCE, FieldType.INIT)]
    ordered_init_fields = list(all_init_fields)
    if reorder:
        ordered_init_fields.sort(key=lambda f: (has_default(f), not f.kw_only))
    std_init_fields, kw_only_init_fields = (
        tuple(f1 for f1 in ordered_init_fields if f1.init and not f1.kw_only),
        tuple(f1 for f1 in ordered_init_fields if f1.init and f1.kw_only),
    )
    return InitFields(
        all=all_init_fields,
        ordered=ordered_init_fields,
        std=std_init_fields,
        kw_only=kw_only_init_fields,
    )


def init_param(f: dc.Field) -> str:
    if not has_default(f):
        default = ''
    elif f.default is not MISSING:
        default = f' = __dataclass_dflt_{f.name}__'
    elif f.default_factory is not MISSING:
        default = ' = __dataclass_HAS_DEFAULT_FACTORY__'
    return f'{f.name}: __dataclass_type_{f.name}__{default}'  # noqa


##


class InitBuilder:
    def __init__(
            self,
            info: ClassInfo,
            fields: ta.Mapping[str, dc.Field],
            has_post_init: bool,
            self_name: str,
            globals: Namespace,  # noqa
    ) -> None:
        super().__init__()

        self._info = info
        self._fields = fields
        self._has_post_init = has_post_init
        self._self_name = self_name
        self._globals = globals

    @lang.cached_function
    def build(self) -> ta.Callable:
        ifs = get_init_fields(self._fields.values(), reorder=self._info.params_extras.reorder)

        seen_default = None
        for f in ifs.std:
            if f.init:
                if has_default(f):
                    seen_default = f
                elif seen_default:
                    raise TypeError(f'non-default argument {f.name!r} follows default argument {seen_default.name!r}')

        locals: dict[str, ta.Any] = {}  # noqa

        if self._info.params_extras.generic_init:
            get_fty = lambda f: self._info.generic_replaced_field_annotations[f.name]
        else:
            get_fty = lambda f: f.type
        locals.update({f'__dataclass_type_{f.name}__': get_fty(f) for f in ifs.all})

        locals.update({
            '__dataclass_HAS_DEFAULT_FACTORY__': HAS_DEFAULT_FACTORY,
            '__dataclass_builtins_object__': object,
            '__dataclass_builtins_isinstance__': isinstance,
            '__dataclass_builtins_TypeError__': TypeError,
            '__dataclass_raise_validation_error__': raise_validation_error,
            '__dataclass_raise_field_validation_error__': raise_field_validation_error,
        })

        body_lines: list[str] = []
        for f in ifs.all:
            f_lines = field_init(
                f,
                self._info.params.frozen,
                locals,
                self._self_name,
                self._info.params.slots,
                self._info.params_extras.override,
            )

            if f_lines:
                body_lines.extend(f_lines)

        if self._has_post_init:
            params_str = ','.join(f.name for f in ifs.all if field_type(f) is FieldType.INIT)
            body_lines.append(f'{self._self_name}.{POST_INIT_NAME}({params_str})')

        for i, fn in enumerate(self._info.merged_metadata.get(Validate, [])):
            if isinstance(fn, staticmethod):
                fn = fn.__func__
            cn = f'__dataclass_validate_{i}__'
            locals[cn] = fn
            csig = inspect.signature(fn)
            cas = ', '.join(p.name for p in csig.parameters.values())
            body_lines.append(f'if not {cn}({cas}): __dataclass_raise_validation_error__({self._self_name}, {cn})')

        inits = self._info.merged_metadata.get(Init, [])
        mro_dct = lang.mro_dict(self._info.cls)
        mro_v_ids = set(map(id, mro_dct.values()))
        props_by_fget_id = {id(v.fget): v for v in mro_dct.values() if isinstance(v, property) and v.fget is not None}
        for i, obj in enumerate(inits):
            if (obj_id := id(obj)) not in mro_v_ids and obj_id in props_by_fget_id:
                obj = props_by_fget_id[obj_id].__get__
            elif isinstance(obj, property):
                obj = obj.__get__
            cn = f'__dataclass_init_{i}__'
            locals[cn] = obj
            body_lines.append(f'{cn}({self._self_name})')

        if not body_lines:
            body_lines = ['pass']

        _init_params = [init_param(f) for f in ifs.std]
        if ifs.kw_only:
            _init_params += ['*']
            _init_params += [init_param(f) for f in ifs.kw_only]

        return create_fn(
            '__init__',
            [self._self_name, *_init_params],
            body_lines,
            locals=locals,
            globals=self._globals,
            return_type=lang.just(None),
        )


class InitProcessor(Processor):
    def _process(self) -> None:
        if not self._info.params.init:
            return

        has_post_init = hasattr(self._cls, POST_INIT_NAME)
        self_name = '__dataclass_self__' if 'self' in self._info.fields else 'self'

        init = InitBuilder(
            ClassInfo(self._cls),
            self._info.fields,
            has_post_init,
            self_name,
            self._info.globals,
        ).build()
        set_new_attribute(
            self._cls,
            '__init__',
            init,
        )
