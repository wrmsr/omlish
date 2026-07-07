import abc
import annotationlib
import typing as ta

from .core.symbols import TypeInfo
from .core.types import Type


UnresolvedForwardRefPolicy: ta.TypeAlias = ta.Literal['unbound', 'raise']


##


class ForwardRefResolution(ta.NamedTuple):
    obj: str | annotationlib.ForwardRef
    name: str
    resolve: ta.Callable[[], object]


class ForwardRefResolver(ta.Protocol):
    def __call__(self, frr: ForwardRefResolution, /) -> object: ...


##


DEFAULT_UNRESOLVED_FORWARD_REF_POLICY: ta.Final[UnresolvedForwardRefPolicy] = 'unbound'


class Mirror:
    """
    TypeInfo and Type objects strictly flow *out of* a mirror, never into. The only methods that take them as parameters
    simply query internal state for their presence - no mutation is done on their behalf.
    """

    ##
    # universe

    @abc.abstractmethod
    def get_type_info(self, obj: type | str) -> TypeInfo:
        raise NotImplementedError

    @abc.abstractmethod
    def get_newtype_info(self, obj: object) -> TypeInfo:
        raise NotImplementedError

    ##
    # reflector

    @property
    @abc.abstractmethod
    def forward_ref_resolver(self) -> ForwardRefResolver | None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unresolved_forward_ref_policy(self) -> UnresolvedForwardRefPolicy | None:
        raise NotImplementedError

    @abc.abstractmethod
    def can_reflect_type(self, obj: object) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def reflect_type(self, obj: object) -> Type:
        raise NotImplementedError
