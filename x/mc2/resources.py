"""
TODO:
 - refcount? ref.close drops self-ref, resources delete if at 0?
 - lock, probably
"""
import abc
import contextlib
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

    def _close(self) -> None:
        pass

    @ta.final
    def close(self) -> None:
        try:
            self._close()
        finally:
            check.state(self.resources.has_reference(self))
            self.resources.close()

    @ta.final
    def __enter__(self) -> ta.Self:
        return self

    @ta.final
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


##


class Resources:
    def __init__(self) -> None:
        super().__init__()

        self._closed = False

        self._refs: ta.MutableSet[ResourcesReference] = col.IdentityWeakSet()

        self._es = contextlib.ExitStack()
        self._es.__enter__()

    def __repr__(self) -> str:
        return lang.attr_repr(self, '_closed', with_id=True)

    def enter_context(self, cm):
        check.state(not self._closed)
        return self._es.enter_context(cm)

    def add_reference(self, ref: ResourcesReference) -> None:
        check.state(not self._closed)
        self._refs.add(ref)

    def has_reference(self, ref: ResourcesReference) -> bool:
        return ref in self._refs

    def close(self) -> None:
        try:
            self._es.__exit__(None, None, None)
        finally:
            self._closed = True

    def __del__(self) -> None:
        if not self._closed:
            ref_lst = list(self._refs)
            log.error(
                f'{__package__}.{self.__class__.__name__}.__del__: '  # noqa
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
