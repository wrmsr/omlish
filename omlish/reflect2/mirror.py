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


class ReflectSubstitutor(ta.Protocol):
    """
    Consulted with each runtime object about to be reflected - at every level of descent, before cache consultation. A
    non-None result is reflected in the object's stead. The result itself is not re-substituted (so self-mapping cannot
    loop), but its constituents are as they are descended into. Must be pure and stable for the lifetime of its mirror
    - reflections incorporating its results are cached.
    """

    def __call__(self, obj: object, /) -> object | None: ...


##


DEFAULT_UNRESOLVED_FORWARD_REF_POLICY: ta.Final[UnresolvedForwardRefPolicy] = 'unbound'


class Mirror:
    """TypeInfo and Type objects strictly flow *out of* a mirror, never into."""

    @property
    @abc.abstractmethod
    def forward_ref_resolver(self) -> ForwardRefResolver | None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unresolved_forward_ref_policy(self) -> UnresolvedForwardRefPolicy | None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def reflect_substitutor(self) -> ReflectSubstitutor | None:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def get_type_info(self, obj: type | str | ta.NewType) -> TypeInfo:
        raise NotImplementedError

    @abc.abstractmethod
    def can_reflect_type(self, obj: object) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def reflect_type(self, obj: object) -> Type:
        raise NotImplementedError
