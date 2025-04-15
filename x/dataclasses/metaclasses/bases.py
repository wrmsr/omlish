import typing as ta

from .params import get_metaclass_params


T = ta.TypeVar('T')


##


# @ta.dataclass_transform(field_specifiers=(field,))  # FIXME: ctor
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
        *get_metaclass_params(Data).confer,
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
        *get_metaclass_params(Frozen).confer,
        'generic_init',
    ]),
):
    v: T
