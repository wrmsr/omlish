"""
TODO:
 - metaclass, to forbid __subclasscheck__ / __instancecheck__? Clash with dc.Meta, don't want that lock-in, not
   necessary for functionality, just a helpful misuse prevention.
"""
import abc
import copy
import dataclasses as dc
import typing as ta

from ... import lang
from ...lite.dataclasses import is_immediate_dataclass
from ..impl.api.classes.decorator import dataclass


##


class Static(lang.Abstract):
    """
    Dataclass mixin for dataclasses in which all fields have class-level defaults and are not intended for any
    instance-level overrides - effectively making their subclasses equivalent to instances. For dataclasses which make
    sense as singletons (such as project specs or manifests), for which dynamic instantiation is not the usecase, this
    can enable more natural syntax. Inheritance is permitted - equivalent to a `functools.partial` or composing
    `**kwargs`, as long as there is only ever one unambiguous underlying non-static dataclass to be instantiated.
    """

    __static_dataclass_class__: ta.ClassVar[type]
    __static_dataclass_instance__: ta.ClassVar[ta.Any]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for a in ('__new__', '__init__'):
            if a in cls.__dict__ and not (cls.__dict__[a] == getattr(Static, a)):
                raise TypeError(f'Static base class {cls} must not implement {a}')

        if cls.__init__ is not Static.__init__:
            # This is necessary to make type-checking work (by allowing it to accept zero args). This isn't strictly
            # necessary, but since it's useful to do sometimes it might as well be done everywhere to prevent clashing.
            raise TypeError(f'Static.__init__ should be first in mro of {cls}')

        #

        b_dc_lst = []

        def b_dc_rec(b_cls: type) -> None:  # noqa
            if issubclass(b_cls, Static):
                return
            elif is_immediate_dataclass(b_cls):
                b_dc_lst.append(b_cls)
            elif dc.is_dataclass(b_cls):
                for sb_cls in b_cls.__bases__:
                    b_dc_rec(sb_cls)

        for b_cls in cls.__bases__:
            b_dc_rec(b_cls)

        b_sdc_dc_lst = [
            b_cls.__static_dataclass_class__
            for b_cls in cls.__bases__
            if issubclass(b_cls, Static)
            and b_cls is not Static
        ]

        sdc_dc_set = {*b_dc_lst, *b_sdc_dc_lst}
        if not sdc_dc_set:
            raise TypeError(f'Static dataclass {cls} inherits from no dataclass')

        # Base static dataclasses of various types are allowed as long as there is exactly one final subclass involved.
        # For example, a ModAttrManifest dataclass with an abstract StaticModAttrManifest subclass which sets a default
        # mod_name may be mixed in with a further down use-case specific Manifest subclass.
        sdc_dc_set -= {
            m_cls
            for s_cls in sdc_dc_set
            for m_cls in s_cls.__mro__
            if m_cls is not s_cls
        }

        if len(sdc_dc_set) > 1:
            raise TypeError(f'Static dataclass {cls} inherits from multiple dataclasses: {sdc_dc_set!r}')
        [sdc_cls] = sdc_dc_set

        if '__static_dataclass_class__' in cls.__dict__:
            raise AttributeError
        setattr(cls, '__static_dataclass_class__', sdc_cls)

        #

        expected_fld_order: ta.Sequence[str] | None = None
        is_abstract = (
            lang.is_abstract_class(cls) or
            abc.ABC in cls.__bases__ or
            lang.Abstract in cls.__bases__
        )
        if not is_abstract:
            if is_immediate_dataclass(cls):
                raise TypeError(cls)

            flds_dct = {}
            for b_cls in cls.__mro__:
                if not dc.is_dataclass(b_cls):
                    continue
                b_flds = dc.fields(b_cls)  # noqa
                for fld in b_flds:
                    if fld.name in flds_dct:
                        continue
                    flds_dct[fld.name] = fld

            # Annotations are the authoritative source of field order.
            new_anns = {}

            for fld in flds_dct.values():
                new_fld = copy.copy(fld)

                try:
                    v = cls.__dict__[fld.name]
                except KeyError:
                    if fld.default is dc.MISSING and fld.default_factory is dc.MISSING:
                        raise TypeError(f'Field {fld.name!r} of class {cls} is not set and has no default') from None
                else:
                    if isinstance(v, dc.Field):
                        raise TypeError(f'Static dataclass {cls} may not introduce new fields: {fld.name}: {v}')

                    new_fld.default = dc.MISSING
                    # Use a default_factory to allow unsafe (mutable) values.
                    new_fld.default_factory = (lambda v2: lambda: v2)(v)  # noqa

                # FIXME
                from ..impl.api.fields.metadata import _ExtraFieldParamsMetadata  # noqa
                from ..specs import FieldSpec
                try:
                    x_fs = fld.metadata[FieldSpec]
                except KeyError:
                    pass
                else:
                    n_md = {
                        k: v
                        for k, v in fld.metadata.items()
                        if k not in (FieldSpec, _ExtraFieldParamsMetadata)
                    }
                    n_md[_ExtraFieldParamsMetadata] = {
                        fs_f.name: getattr(x_fs, fs_f.name)
                        for fs_f in dc.fields(FieldSpec)  # noqa
                        if fs_f not in dc.Field.__slots__
                        and fs_f.name not in ('default', 'default_factory')
                    }
                    new_fld.metadata = n_md  # type: ignore[assignment]

                setattr(cls, fld.name, new_fld)
                new_anns[fld.name] = fld.type

            # Non-abstract static dataclasses may not introduce new fields.
            expected_fld_order = list(flds_dct)

            new_anns.update({
                k: v
                for k, v in getattr(cls, '__annotations__', {}).items()
                if k not in new_anns
            })

            # FIXME: 3.14
            cls.__annotations__ = new_anns

        else:
            for b_cls in cls.__bases__:
                if hasattr(b_cls, '__static_dataclass_instance__'):
                    raise TypeError(
                        f'Abstract static dataclass {cls} may not inherit from non-abstract static dataclass {b_cls}',
                    )

        # Explicitly forbid dc transforms that rebuild the class, such as slots.
        if (dc_cls := dataclass(frozen=True)(cls)) is not cls:
            raise TypeError(dc_cls)

        dc_flds = dc.fields(cls)  # type: ignore[arg-type]  # noqa

        if expected_fld_order is not None:
            dc_fld_order = [f.name for f in dc_flds]
            if dc_fld_order != expected_fld_order:
                raise TypeError(
                    f'Static dataclass field order {dc_fld_order!r} != expected field order {expected_fld_order!r}',
                )

        if not is_abstract:
            # This is the only time the Statics are ever actually instantiated, and it's only to produce the kwargs
            # passed to the underlying dataclass.
            tmp_inst = cls()
            inst_kw = dc.asdict(tmp_inst)  # type: ignore[call-overload]  # noqa
            inst = sdc_cls(**inst_kw)

            cls.__static_dataclass_instance__ = inst

            # Make all field values available via static `Class.field` access, even those created via a factory. Note
            # that further inheritance of this non-abstract Static will continue to inherit dc.Field instances
            # (including things like their metadata) via dc.fields() access, which does not reference `cls.__dict__`.
            for fld in dc_flds:
                v = getattr(inst, fld.name)
                setattr(cls, fld.name, v)

            def __new__(new_cls, *new_args, **new_kwargs):  # noqa
                try:
                    return new_cls.__dict__['__static_dataclass_instance__']
                except KeyError:
                    return super().__new__(new_cls)

            cls.__new__ = __new__  # type: ignore

        cls.__init__ = Static.__init__  # type: ignore

    @ta.final
    def __init__(self) -> None:
        # This stub serves to allow `StaticSubclass()` to typecheck by allowing it to accept only zero arguments. Note
        # that this is only the case when `Static` is first in mro.
        raise TypeError('May not instantiate static dataclasses')
