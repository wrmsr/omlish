import abc
import annotationlib
import typing as ta

from .core.symbols import TypeInfo
from .core.types import Type
from .core.types import TypeVarLikeType


DynamicTypeNameSuffix: ta.TypeAlias = ta.Literal['id', 'counter']

UnresolvedForwardRefPolicy: ta.TypeAlias = ta.Literal['unbound', 'raise']


##


class ForwardRefResolution(ta.NamedTuple):
    obj: str | annotationlib.ForwardRef
    name: str
    resolve: ta.Callable[[], object]


class ForwardRefResolver(ta.Protocol):
    def __call__(self, frr: ForwardRefResolution, /) -> object: ...


##


DEFAULT_DYNAMIC_TYPE_NAME_SUFFIX: ta.Final[DynamicTypeNameSuffix] = 'id'

DEFAULT_UNRESOLVED_FORWARD_REF_POLICY: ta.Final[UnresolvedForwardRefPolicy] = 'unbound'


class Mirror:
    @property
    @abc.abstractmethod
    def dynamic_type_name_suffix(self) -> DynamicTypeNameSuffix:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def forward_ref_resolver(self) -> ForwardRefResolver | None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unresolved_forward_ref_policy(self) -> UnresolvedForwardRefPolicy | None:
        raise NotImplementedError

    ##
    # universe

    @abc.abstractmethod
    def get_runtime_type(self, info: TypeInfo) -> object | None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_type_info(self, obj: type | str) -> TypeInfo:
        raise NotImplementedError

    @abc.abstractmethod
    def get_newtype_info(self, obj: object) -> TypeInfo:
        raise NotImplementedError

    ##
    # reflector

    @abc.abstractmethod
    def resolve_runtime_type_param(self, typ: TypeVarLikeType) -> object | None:
        raise NotImplementedError

    @abc.abstractmethod
    def reflect_type(self, obj: object) -> Type:
        raise NotImplementedError
