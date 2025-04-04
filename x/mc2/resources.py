"""
TODO:
 - resources is IdentityKeyMap -> refcount, obj?
 - lock, probably
 - @dc.init to inc _resources refcount? who 'exits' what / where?
"""
import abc
import logging
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

from .services import Response
from .services import ResponseOutput  # noqa


ResponseOutputT = ta.TypeVar('ResponseOutputT', bound='ResponseOutput')


log = logging.getLogger(__name__)


##


class ResourcesReference(lang.Abstract):
    @property
    @abc.abstractmethod
    def resources(self) -> 'Resources':
        raise NotImplementedError

    def close(self) -> None:
        check.state(self.resources.has_reference(self))
        self.resources.close()


##


class Resources:
    def __init__(self) -> None:
        super().__init__()

        self._closed = False

        self._refs: ta.MutableSet[ResourcesReference] = col.IdentityWeakSet()

    def __repr__(self) -> str:
        return lang.attr_repr(self, '_closed', with_id=True)

    def add_reference(self, ref: ResourcesReference) -> None:
        self._refs.add(ref)

    def has_reference(self, ref: ResourcesReference) -> bool:
        return ref in self._refs

    def close(self) -> None:
        self._closed = True

    def __del__(self) -> None:
        if not self._closed:
            ref_lst = list(self._refs)
            log.error(
                f'{__package__}.{self.__class__.__name__}.__del__: '
                f'%r deleted without being closed! '
                f'refs: %r',
                self,
                ref_lst,
            )


##


@dc.dataclass(frozen=True)
@dc.extra_params(repr_id=True)
class ResourcesResponse(
    Response[ResponseOutputT],
    ResourcesReference,
    lang.Abstract,
    ta.Generic[ResponseOutputT],
):
    _resources: Resources = dc.field(kw_only=True)

    @dc.init
    def _register_resources_reference(self) -> None:
        self._resources.add_reference(self)

    @property
    @ta.final
    def resources(self) -> 'Resources':
        return self._resources
