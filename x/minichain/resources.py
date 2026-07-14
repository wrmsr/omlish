import contextlib
import typing as ta

from omcore import lang
from omcore import resources as _resources
from omcore import typedvalues as tv
from omcore.logs import all as logs

from .types import Option


T = ta.TypeVar('T')


log = logs.get_module_logger(globals())


##


ResourcesRef: ta.TypeAlias = _resources.ResourceManagerRef
ResourcesRefNotRegisteredError: ta.TypeAlias = _resources.ResourceManagerRefNotRegisteredError

Resources: ta.TypeAlias = _resources.AsyncResourceManager

# Explicitly not marked as `ta.TypeAlias` because it confuses pycharm.
ResourceManaged = _resources.AsyncResourceManaged


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
