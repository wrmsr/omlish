import contextlib
import typing as ta

from omlish import lang
from omlish import resources as _resources
from omlish import typedvalues as tv
from omlish.logs import all as logs

from .types import Option


T = ta.TypeVar('T')


log = logs.get_module_logger(globals())


##


ResourcesRef: ta.TypeAlias = _resources.ResourcesRef
ResourcesRefNotRegisteredError: ta.TypeAlias = _resources.ResourcesRefNotRegisteredError

Resources: ta.TypeAlias = _resources.AsyncResources
ResourceManaged: ta.TypeAlias = _resources.AsyncResourceManaged


##


class ResourcesOption(Option, lang.Abstract):
    pass


class UseResources(tv.UniqueScalarTypedValue[Resources], ResourcesOption, lang.Final):
    @classmethod
    @contextlib.asynccontextmanager
    async def or_new(cls, options: ta.Sequence[Option]) -> ta.AsyncGenerator[Resources]:
        if (ur := tv.as_collection(options).get(UseResources)) is not None:
            async with ResourceManaged(ur.v, ur.v) as rs:
                yield rs

        else:
            async with Resources.new() as rs:
                yield rs
