import dataclasses as dc

from .processing import Processor
from .utils import create_fn
from .utils import set_qualname
from .utils import tuple_str


def _hash_fn(fields, globals):
    self_tuple = tuple_str('self', fields)
    return create_fn(
        '__hash__',
        ('self',),
        [f'return hash({self_tuple})'],
        globals=globals,
    )


def _hash_set_none(cls, fields, globals):
    return None


def _hash_add(cls, fields, globals):
    flds = [f for f in fields if (f.compare if f.hash is None else f.hash)]
    return set_qualname(cls, _hash_fn(flds, globals))


def _hash_exception(cls, fields, globals):
    # Raise an exception.
    raise TypeError(f'Cannot overwrite attribute __hash__ in class {cls.__name__}')


#
#                +-------------------------------------- unsafe_hash?
#                |      +------------------------------- eq?
#                |      |      +------------------------ frozen?
#                |      |      |      +----------------  has-explicit-hash?
#                |      |      |      |
#                |      |      |      |        +-------  action
#                |      |      |      |        |
#                v      v      v      v        v
HASH_ACTIONS = {(False, False, False, False): None,  # noqa
                (False, False, False, True ): None,  # noqa
                (False, False, True,  False): None,  # noqa
                (False, False, True,  True ): None,  # noqa
                (False, True,  False, False): _hash_set_none,  # noqa
                (False, True,  False, True ): None,  # noqa
                (False, True,  True,  False): _hash_add,  # noqa
                (False, True,  True,  True ): None,  # noqa
                (True,  False, False, False): _hash_add,  # noqa
                (True,  False, False, True ): _hash_exception,  # noqa
                (True,  False, True,  False): _hash_add,  # noqa
                (True,  False, True,  True ): _hash_exception,  # noqa
                (True,  True,  False, False): _hash_add,  # noqa
                (True,  True,  False, True ): _hash_exception,  # noqa
                (True,  True,  True,  False): _hash_add,  # noqa
                (True,  True,  True,  True ): _hash_exception,  # noqa
                }
# See https://bugs.python.org/issue32929#msg312829 for an if-statement version of this table.


class HashProcessor(Processor):
    def _process(self) -> None:
        class_hash = self._cls.__dict__.get('__hash__', dc.MISSING)
        has_explicit_hash = not (class_hash is dc.MISSING or (class_hash is None and '__eq__' in self._cls.__dict__))

        hash_action = HASH_ACTIONS[(
            bool(self._info.params.unsafe_hash),
            bool(self._info.params.eq),
            bool(self._info.params.frozen),
            has_explicit_hash,
        )]
        if hash_action:
            self._cls.__hash__ = hash_action(self._cls, self._info.instance_fields, self._info.globals)  # type: ignore
