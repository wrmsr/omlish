"""
TODO:
 - return bool not raise, don't throw/catch in unions
  - *this is check vs validate*
  - prob doable generically
 - **generalize traversal out of dataclasses.. monoids :|**
"""
import collections.abc
import dataclasses as dc
import typing as ta

from .. import check
from .. import dispatch
from .. import lang
from .. import reflect
from .types import FieldValidation
from .types import FieldValidator
from .virtual import Virtual


Field = dc.Field


DEFAULT_FIELD_VALIDATION_DISPATCHER: dispatch.Dispatcher[FieldValidation] = dispatch.CachingDispatcher(
    # dispatch.ErasingDispatcher(),
    dispatch.GenericDispatcher(),
)


def build_default_field_validation(fld: Field, type=dc.MISSING) -> FieldValidator:
    impl, manifest = DEFAULT_FIELD_VALIDATION_DISPATCHER.dispatch(
        type if type is not dc.MISSING else (fld.type or object))
    return dispatch.inject_manifest(impl, manifest)(fld)


@DEFAULT_FIELD_VALIDATION_DISPATCHER.registering(object, *lang.BUILTIN_SCALAR_ITERABLE_TYPES)
def default_field_validation(fld: Field, *, manifest: dispatch.Manifest) -> FieldValidator:
    cls = manifest.spec.erased_cls

    def inner(value):
        if not isinstance(value, cls):
            raise TypeError(f'Invalid type for field {fld.name}', value)
    return inner


@DEFAULT_FIELD_VALIDATION_DISPATCHER.registering(ta.Union)
def union_field_validation(fld: Field, *, manifest: dispatch.Manifest) -> FieldValidator:
    uvs = [build_default_field_validation(fld, type=a) for a in manifest.spec.args]

    def inner(value):
        for uv in uvs:
            try:
                uv(value)
            except TypeError:
                pass
            else:
                return
        raise TypeError(f'Invalid type for field {fld.name}', value)
    return inner


@DEFAULT_FIELD_VALIDATION_DISPATCHER.registering(collections.abc.Iterable)
def iterable_default_field_validation(fld: Field, *, manifest: dispatch.Manifest) -> FieldValidator:
    cls = manifest.spec.erased_cls
    if isinstance(manifest.spec, reflect.NonGenericTypeSpec):
        return default_field_validation(fld, manifest=manifest)

    elif isinstance(manifest.spec, reflect.ParameterizedGenericTypeSpec):
        [e] = manifest.spec.args
        ev = build_default_field_validation(fld, e)

        def inner(value):
            check.isinstance(value, cls, f'Invalid type for field {fld.name}')
            for e in value:
                ev(e)
        return inner

    else:
        raise TypeError(manifest.spec)


@DEFAULT_FIELD_VALIDATION_DISPATCHER.registering(collections.abc.Mapping)
def mapping_default_field_validation(fld: Field, *, manifest: dispatch.Manifest) -> FieldValidator:
    cls = manifest.spec.erased_cls
    if isinstance(manifest.spec, reflect.NonGenericTypeSpec):
        return default_field_validation(fld, manifest=manifest)

    elif isinstance(manifest.spec, reflect.ParameterizedGenericTypeSpec):
        k, v = manifest.spec.args
        kv = build_default_field_validation(fld, k)
        vv = build_default_field_validation(fld, v)

        def inner(value):
            check.isinstance(value, cls, f'Invalid type for field {fld.name}')
            for k, v in value.items():
                kv(k)
                vv(v)
        return inner

    else:
        raise TypeError(manifest.spec)


@DEFAULT_FIELD_VALIDATION_DISPATCHER.registering(Virtual)
def dataclass_default_field_validation(fld: Field, *, manifest: dispatch.Manifest) -> FieldValidator:
    # FIXME: recurse?
    return default_field_validation(fld, manifest=manifest)


@DEFAULT_FIELD_VALIDATION_DISPATCHER.registering(lang.Redacted)
def redacted_default_field_validation(fld: Field, *, manifest: dispatch.Manifest) -> FieldValidator:
    cls = manifest.spec.erased_cls
    if isinstance(manifest.spec, reflect.NonGenericTypeSpec):
        return default_field_validation(fld, manifest=manifest)

    elif isinstance(manifest.spec, reflect.ParameterizedGenericTypeSpec):
        [v] = manifest.spec.args
        vv = build_default_field_validation(fld, v)

        def inner(value):
            check.isinstance(value, cls, f'Invalid type for field {fld.name}')
            vv(value.value)
        return inner

    else:
        raise TypeError(manifest.spec)
