import typing as ta

import pytest

from omlish import check

from ..sync import Resources
from ..sync import ResourceManaged
from ..asyncs import AsyncResources
from ..asyncs import AsyncResourceManaged


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


def make_rc(*, resources: Resources | None = None) -> ResourceManaged[Rc]:
    with Resources.or_new(resources) as resources:
        return resources.new_managed(resources.enter_context(Rc()))


def test_resources_given():
    with Resources.new() as resources:
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


async def a_make_arc(*, resources: AsyncResources | None = None) -> AsyncResourceManaged[Arc]:
    async with AsyncResources.or_new(resources) as resources:
        return resources.new_managed(await resources.enter_async_context(Arc()))


async def a_make_rc(*, resources: AsyncResources | None = None) -> AsyncResourceManaged[Rc]:
    async with AsyncResources.or_new(resources) as resources:
        return resources.new_managed(resources.enter_context(Rc()))


@pytest.mark.asyncs('asyncio')
async def test_async_resources_given():
    async with AsyncResources.new() as resources:
        async with (await a_make_arc(resources=resources)) as arc:
            assert isinstance(arc, Arc)
            assert arc.state == 'entered'
        async with (await a_make_rc(resources=resources)) as rc:
            assert isinstance(rc, Rc)
            assert rc.state == 'entered'
        assert arc.state == 'entered'
        assert rc.state == 'entered'
    assert arc.state == 'exited'
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
