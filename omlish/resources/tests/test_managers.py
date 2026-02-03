import contextlib
import typing as ta

import pytest

from ... import check
from ..managers import AsyncResourceManaged
from ..managers import AsyncResourceManager
from ..managers import ResourceManaged
from ..managers import ResourceManager


##


class Rc:
    state: ta.Literal['new', 'entered', 'exited'] = 'new'

    def __enter__(self) -> ta.Self:
        check.state(self.state == 'new')
        self.state = 'entered'
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        check.state(self.state == 'entered')
        self.state = 'exited'


class Arc:
    state: ta.Literal['new', 'entered', 'exited'] = 'new'

    async def __aenter__(self) -> ta.Self:
        check.state(self.state == 'new')
        self.state = 'entered'
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        check.state(self.state == 'entered')
        self.state = 'exited'


##


def make_rc(*, resources: ResourceManager | None = None) -> ResourceManaged[Rc]:
    with ResourceManager.or_new(resources) as resources:  # noqa
        return resources.new_managed(resources.enter_context(Rc()))


def test_resources_given():
    with ResourceManager.new() as resources:  # noqa
        with (make_rc(resources=resources)) as rc:
            assert isinstance(rc, Rc)
            assert rc.state == 'entered'
        assert rc.state == 'entered'
    assert rc.state == 'exited'


def test_resources_not_given():
    with make_rc() as rc:
        assert isinstance(rc, Rc)
        assert rc.state == 'entered'
    assert rc.state == 'exited'


##


async def a_make_arc(*, resources: AsyncResourceManager | None = None) -> AsyncResourceManaged[Arc]:
    async with AsyncResourceManager.or_new(resources) as resources:  # noqa
        return resources.new_managed(await resources.enter_async_context(Arc()))


def a_make_arc2(*, resources: AsyncResourceManager | None = None) -> ta.AsyncContextManager[Arc]:
    @contextlib.asynccontextmanager
    async def inner():
        async with AsyncResourceManager.or_new(resources) as rs:  # noqa
            yield await rs.enter_async_context(Arc())

    return inner()


async def a_make_rc(*, resources: AsyncResourceManager | None = None) -> AsyncResourceManaged[Rc]:
    async with AsyncResourceManager.or_new(resources) as resources:  # noqa
        return resources.new_managed(resources.enter_context(Rc()))


@pytest.mark.asyncs('asyncio')
async def test_async_resources_given():
    async with AsyncResourceManager.new() as resources:
        async with (await a_make_arc(resources=resources)) as arc:
            assert isinstance(arc, Arc)
            assert arc.state == 'entered'

        async with a_make_arc2(resources=resources) as arc2:
            assert isinstance(arc, Arc)
            assert arc2.state == 'entered'

        async with (await a_make_rc(resources=resources)) as rc:
            assert isinstance(rc, Rc)
            assert rc.state == 'entered'

        assert arc.state == 'entered'
        assert arc2.state == 'entered'
        assert rc.state == 'entered'

    assert arc.state == 'exited'
    assert arc2.state == 'exited'
    assert rc.state == 'exited'  # type: ignore[unreachable]


@pytest.mark.asyncs('asyncio')
async def test_async_resources_not_given():
    async with (await a_make_arc()) as arc:
        assert isinstance(arc, Arc)
        assert arc.state == 'entered'

    assert arc.state == 'exited'

    async with (await a_make_rc()) as rc:  # type: ignore[unreachable]
        assert isinstance(rc, Rc)
        assert rc.state == 'entered'

    assert rc.state == 'exited'
