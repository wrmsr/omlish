import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl


T = ta.TypeVar('T')

TypedValueT = ta.TypeVar('TypedValueT', bound='TypedValue')
TypedValueU = ta.TypeVar('TypedValueU', bound='TypedValue')

UniqueTypedValueU = ta.TypeVar('UniqueTypedValueU', bound='UniqueTypedValue')


##


class TypedValueGeneric(lang.Abstract, ta.Generic[TypedValueT]):
    _typed_value_type: ta.ClassVar[rfl.Type]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if '_typed_value_type' in cls.__dict__:
            return

        g_mro = rfl.ALIAS_UPDATING_GENERIC_SUBSTITUTION.generic_mro(cls)
        g_tvg = check.single(
            gb
            for gb in g_mro
            if isinstance(gb, rfl.Generic) and gb.cls is TypedValueGeneric
        )
        tvt = check.single(g_tvg.args)
        cls._typed_value_type = tvt

