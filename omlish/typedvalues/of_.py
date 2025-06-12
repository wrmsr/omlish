import typing as ta

from .. import lang
from .collection import TypedValues
from .consumer import TypedValuesConsumer
from .values import TypedValue


TypedValueT = ta.TypeVar('TypedValueT', bound=TypedValue)


##


class _TypedValuesOf(lang.BindableClass[TypedValueT]):  # noqa
    @classmethod
    def collect(
            cls,
            *tvs: TypedValueT,
            override: bool = False,
            check_type: bool | type | tuple[type, ...] | None = None,
    ) -> TypedValues[TypedValueT]:  # noqa
        if isinstance(check_type, bool):
            if check_type:
                if cls._bound is None:
                    raise TypeError('TypedValues.of unbound, cannot use check_type=True')
                check_type = cls._bound
            else:
                check_type = None

        return TypedValues(
            *tvs,
            override=override,
            check_type=check_type,
        )

    @classmethod
    def consume(
            cls,
            *tvs: TypedValueT,
            override: bool = False,
            check_type: bool | type | tuple[type, ...] | None = None,
    ) -> TypedValuesConsumer[TypedValueT]:
        return cls.collect(
            *tvs,
            override=override,
            check_type=check_type,
        ).consume()


of = _TypedValuesOf
