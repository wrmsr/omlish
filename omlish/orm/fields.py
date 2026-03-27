import typing as ta

from .. import check
from .. import lang
from .. import reflect as rfl
from .keys import Key
from .refs import Ref


##


class Field(lang.Sealed):
    def __init__(
            self,
            *,
            _name: str,
            _store_name: str,
            _rty: rfl.Type,
    ) -> None:
        super().__init__()

        self._name = check.non_empty_str(_name)
        self._store_name = check.non_empty_str(_store_name)
        self._rty = check.isinstance(_rty, rfl.Type)

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

    @property
    def optional(self) -> bool:
        return self._optional

    @property
    def ref_obj_cls(self) -> type:
        return self._ref_obj_cls

    @property
    def ref_key_cls(self) -> type:
        return self._ref_key_cls
