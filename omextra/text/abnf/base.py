import abc
import typing as ta

from omlish import check
from omlish import lang


OpTuple: ta.TypeAlias = tuple['Op', ...]


##


class Op(lang.Abstract, lang.PackageSealed):
    def _match_repr(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}'


class CompositeOp(Op, lang.Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            leaf_op_cls = LeafOp
        except NameError:
            pass
        else:
            check.not_issubclass(cls, leaf_op_cls)

    @property
    @abc.abstractmethod
    def children(self) -> OpTuple:
        raise NotImplementedError

    @abc.abstractmethod
    def replace_children(self, *children: Op) -> Op:
        raise NotImplementedError


class LeafOp(Op, lang.Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_issubclass(cls, CompositeOp)
