import typing as ta

import anyio
import pytest

from ... import asyncs as au
from ... import dataclasses as dc  # noqa
from ... import inject as inj
from ... import lang  # noqa


T = ta.TypeVar('T')


##


class SomeManager:
    ec = 0
    xc = 0

    def __enter__(self) -> ta.Self:
        self.ec += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.xc += 1


def test_managed():
    with inj.create_managed_injector(
        inj.bind(SomeManager, singleton=True, to_fn=inj.make_managed_provider(SomeManager)),
    ) as i:
        sm = i[SomeManager]
        assert sm.ec == 1
        assert i[SomeManager] is sm
        assert sm.ec == 1
        assert sm.xc == 0
    assert sm.ec == 1
    assert sm.xc == 1


##


class SomeAsyncManager:
    ec = 0
    xc = 0

    async def __aenter__(self) -> ta.Self:
        self.ec += 1
        await anyio.sleep(.01)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.xc += 1


@pytest.mark.asyncio
async def test_async_managed():
    async with inj.create_async_managed_injector(
            inj.bind(SomeAsyncManager, singleton=True, to_fn=inj.make_async_managed_provider(SomeAsyncManager)),
    ) as i:
        sam = await au.s_to_a(i.provide)(SomeAsyncManager)
        assert sam.ec == 1
        assert i[SomeAsyncManager] is sam
        assert sam.ec == 1
        assert sam.xc == 0
    assert sam.ec == 1
    assert sam.xc == 1


##


# def test_custom_inject():
#     @dc.dataclass(frozen=True)
#     @dc.extra_params(cache_hash=True)
#     class _JankManagedTag(lang.Final):
#         tag: ta.Any
#
#     def jank_managed(a):
#         b = inj.as_binding(a)
#         mg_key = dc.replace(b.key, tag=_JankManagedTag(b.key.tag))
#
#         def prov(i: inj.Injector):
#             o = i[mg_key]
#             i[contextlib.ExitStack].enter_context(o)
#             return o
#
#         return inj.as_elements(
#             dc.replace(b, key=mg_key),
#             dc.replace(b, provider=inj.fn(prov, b.key.ty)),
#         )
#
#     with inj.create_managed_injector(inj.as_elements(
#             inj.bind(420),
#             jank_managed(SomeManager),
#     )) as i:
#         assert i[int] == 420
#         sm = i[SomeManager]
#         assert (sm.ec, sm.xc) == (1, 0)
#     assert (sm.ec, sm.xc) == (1, 1)
