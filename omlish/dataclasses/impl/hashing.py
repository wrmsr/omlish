import dataclasses as dc
import enum
import typing as ta

from .processing import Processor
from .utils import create_fn
from .utils import set_qualname
from .utils import tuple_str


class HashAction(enum.Enum):
    SET_NONE = enum.auto()
    ADD = enum.auto()
    EXCEPTION = enum.auto()


# See https://bugs.python.org/issue32929#msg312829 for an if-statement version of this table.
HASH_ACTIONS: ta.Mapping[tuple[bool, bool, bool, bool], HashAction | None] = {
    #
    # +-------------------------------------- unsafe_hash?
    # |      +------------------------------- eq?
    # |      |      +------------------------ frozen?
    # |      |      |      +----------------  has-explicit-hash?
    # |      |      |      |
    # |      |      |      |
    # |      |      |      |
    # v      v      v      v
    (False, False, False, False): None,
    (False, False, False, True): None,
    (False, False, True, False): None,
    (False, False, True, True): None,
    (False, True, False, False): HashAction.SET_NONE,
    (False, True, False, True): None,
    (False, True, True, False): HashAction.ADD,
    (False, True, True, True): None,
    (True, False, False, False): HashAction.ADD,
    (True, False, False, True): HashAction.EXCEPTION,
    (True, False, True, False): HashAction.ADD,
    (True, False, True, True): HashAction.EXCEPTION,
    (True, True, False, False): HashAction.ADD,
    (True, True, False, True): HashAction.EXCEPTION,
    (True, True, True, False): HashAction.ADD,
    (True, True, True, True): HashAction.EXCEPTION,
}


def _hash_fn(fields, globals):
    self_tuple = tuple_str('self', fields)
    return create_fn(
        '__hash__',
        ('self',),
        [f'return hash({self_tuple})'],
        globals=globals,
    )


class HashProcessor(Processor):
    def _process(self) -> None:
        class_hash = self._cls.__dict__.get('__hash__', dc.MISSING)
        has_explicit_hash = not (class_hash is dc.MISSING or (class_hash is None and '__eq__' in self._cls.__dict__))

        match (hash_action := HASH_ACTIONS[(
            bool(self._info.params.unsafe_hash),
            bool(self._info.params.eq),
            bool(self._info.params.frozen),
            has_explicit_hash,
        )]):
            case HashAction.SET_NONE:
                self._cls.__hash__ = None  # type: ignore
            case HashAction.ADD:
                flds = [f for f in self._info.instance_fields if (f.compare if f.hash is None else f.hash)]
                hash_fn = set_qualname(self._cls, _hash_fn(flds, self._info.globals))  # noqa
                self._cls.__hash__ = hash_fn  # type: ignore
            case HashAction.EXCEPTION:
                raise TypeError(f'Cannot overwrite attribute __hash__ in class {self._cls.__name__}')
            case None:
                pass
            case _:
                raise ValueError(hash_action)
