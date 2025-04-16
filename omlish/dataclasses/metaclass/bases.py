import typing as ta

from ..concerns.frozen import unchecked_frozen_base
from .meta import DataMeta
from .specs import get_metaclass_spec


T = ta.TypeVar('T')


##


# @ta.dataclass_transform(field_specifiers=(field,))  # FIXME: ctor
@unchecked_frozen_base
class Data(
    eq=False,
    order=False,
    confer=frozenset([
        'confer',
        'final_subclasses',
    ]),
    metaclass=DataMeta,
):
    def __init__(self, *args, **kwargs):
        # Typechecking barrier
        super().__init__(*args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        # Typechecking barrier
        super().__init_subclass__(**kwargs)


class Frozen(
    Data,
    frozen=True,
    eq=False,
    order=False,
    confer=frozenset([
        *get_metaclass_spec(Data).confer,
        'frozen',
        'reorder',
        'cache_hash',
        'override',
    ]),
):
    pass


class Case(
    Frozen,
    abstract=True,
    override=True,
    final_subclasses=True,
    abstract_immediate_subclasses=True,
):
    pass


class Box(
    Frozen,
    ta.Generic[T],
    generic_init=True,
    confer=frozenset([
        *get_metaclass_spec(Frozen).confer,
        'generic_init',
    ]),
):
    v: T
