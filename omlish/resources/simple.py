import typing as ta
import warnings

from .. import check
from .. import lang
from .debug import _ResourcesDebug
from .errors import ResourceNotEnteredError
from .errors import UnclosedResourceWarning


##


class BaseSimpleResource(_ResourcesDebug, lang.Abstract):
    """
    IMPORTANT: Subclasses must not raise exceptions in constructors or resources will be leaked (given the intended
    usage ergonomics). Do any validation in `_enter`.
    """

    _resource_state: ta.Literal[
        'new',

        'entering',
        'failed_entering',
        'entered',

        'closing',
        'failed_closing',
        'closed',
    ] = 'new'

    #

    @ta.final
    @property
    def _entered(self) -> bool:
        return self._resource_state == 'entered'

    @ta.final
    @property
    def _closed(self) -> bool:
        return self._resource_state in ('failed_closing', 'closed')

    #

    @ta.final
    def _check_entered(self) -> None:
        if not self._entered:
            raise ResourceNotEnteredError(self)  # noqa

    #

    @property
    def _is_resourceless(self) -> bool:
        return False

    @ta.final
    def __del__(self) -> None:
        if (
                self._entered and
                not self._closed and
                not self._is_resourceless and
                self._resources_debug
        ):
            warnings.warn(
                f'\n\n{(sep := ("=" * 40))}\n'
                f'{self.__class__.__name__} object '
                f'{self._resources_debug_repr or f"at {hex(id(self))}"} '
                f'was not properly closed before finalization. Please ensure that `__exit__` or `close()` is called '
                f'before the object is finalized.'
                f'\n\n'
                f'{"".join(self._resources_debug_traceback).rstrip()}'
                f'\n{sep}\n',
                UnclosedResourceWarning,
            )


class SimpleResource(BaseSimpleResource, lang.Abstract):
    @ta.final
    def __enter__(self) -> ta.Self:
        check.state(self._resource_state == 'new')
        self._resource_state = 'entering'
        try:
            self._enter()
            self._init_debug()
        except BaseException as e:  # noqa
            self._resource_state = 'failed_entering'
            raise
        self._resource_state = 'entered'
        return self

    def _enter(self) -> None:
        pass

    #

    @ta.final
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_internal(exc_val)

    @ta.final
    def close(self) -> None:
        self._close_internal(None)

    @ta.final
    def _close_internal(self, reason: BaseException | None) -> None:
        if not self._closed:
            try:
                self._close(reason)
            except BaseException as e:  # noqa
                self._resource_state = 'failed_closing'
                raise
            self._resource_state = 'closed'

    def _close(self, reason: BaseException | None) -> None:
        pass


class AsyncSimpleResource(BaseSimpleResource, lang.Abstract):
    @ta.final
    async def __aenter__(self) -> ta.Self:
        check.state(self._resource_state == 'new')
        self._resource_state = 'entering'
        try:
            await self._enter()
            self._init_debug()
        except BaseException as e:  # noqa
            self._resource_state = 'failed_entering'
            raise
        self._resource_state = 'entered'
        return self

    async def _enter(self) -> None:
        pass

    #

    @ta.final
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_internal(exc_val)

    @ta.final
    async def aclose(self) -> None:
        await self._close_internal(None)

    @ta.final
    async def _close_internal(self, reason: BaseException | None) -> None:
        if not self._closed:
            try:
                await self._close(reason)
            except BaseException as e:  # noqa
                self._resource_state = 'failed_closing'
                raise
            self._resource_state = 'closed'

    async def _close(self, reason: BaseException | None) -> None:
        pass
