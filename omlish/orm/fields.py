import typing as ta

from .. import check
from .. import lang
from .. import reflect as rfl
from .. import typedvalues as tv
from .keys import Key
from .options import FieldOption
from .refs import Ref


if ta.TYPE_CHECKING:
    from .mappers import Mapper


##


@ta.final
class FinalFieldOption(FieldOption, tv.UniqueTypedValue, lang.Final):
    pass


##


class Field(lang.Sealed):
    def __init__(
            self,
            *,
            _name: str,
            _store_name: str,
            _rty: rfl.Type,
            _backref_binding: ta.Any | None = None,
            _options: ta.Sequence[FieldOption] | None = None,
    ) -> None:
        super().__init__()

        self._name = check.non_empty_str(_name)
        self._store_name = check.non_empty_str(_store_name)
        self._rty = check.isinstance(_rty, rfl.Type)
        self._backref_binding = _backref_binding
        self._options = tv.TypedValues(*(_options or []))

        self._is_final = FinalFieldOption in self._options

    @classmethod
    def _default_store_name(cls, name: str) -> str:
        return name

    def __repr__(self) -> str:
        return ''.join([
            f'{type(self).__name__}(',
            ', '.join([
                repr(self._name),
                repr(self._rty),
            ]),
            ')',
        ])

    @property
    def name(self) -> str:
        return self._name

    @property
    def store_name(self) -> str:
        return self._store_name

    @property
    def rty(self) -> rfl.Type:
        return self._rty

    @property
    def unwrapped_rty(self) -> rfl.Type:
        return self._rty

    @property
    def backref_binding(self) -> ta.Any | None:
        return self._backref_binding

    @property
    def options(self) -> tv.TypedValues[FieldOption]:
        return self._options

    #

    @property
    def is_final(self) -> bool:
        return self._is_final

    #

    _mapper: 'Mapper'

    def _set_mapper(self, r: 'Mapper') -> None:
        try:
            self._mapper  # noqa
        except AttributeError:
            pass
        else:
            raise RuntimeError('mapper already set')
        self._mapper = r

    @property
    def mapper(self) -> 'Mapper':
        return self._mapper


@ta.final
class KeyField(Field, lang.Final):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        gty = check.isinstance(self._rty, rfl.Generic)
        check.is_(gty.cls, Key)
        self._key_cls = check.isinstance(check.single(gty.args), type)

    @property
    def key_cls(self) -> type:
        return self._key_cls

    @property
    def unwrapped_rty(self) -> rfl.Type:
        return self._key_cls


@ta.final
class RefField(Field, lang.Final):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        if isinstance(rty := self._rty, rfl.Union):
            check.state(rty.is_optional)
            rty = rty.without_none()
            self._optional = True
        else:
            self._optional = False

        gty = check.isinstance(rty, rfl.Generic)
        check.is_(gty.cls, Ref)
        ort, krt = gty.args
        self._ref_obj_cls = check.isinstance(ort, type)
        self._ref_key_cls = check.isinstance(krt, type)

        uw_rty = krt
        if self._optional:
            uw_rty = rfl.Union(frozenset([uw_rty, type(None)]))
        self._unwrapped_rty = uw_rty

    @property
    def is_optional(self) -> bool:
        return self._optional

    @property
    def ref_obj_cls(self) -> type:
        return self._ref_obj_cls

    @property
    def ref_key_cls(self) -> type:
        return self._ref_key_cls

    @property
    def unwrapped_rty(self) -> rfl.Type:
        return self._unwrapped_rty
