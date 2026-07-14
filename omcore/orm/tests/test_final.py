# ruff: noqa: PT012
import pytest

from ... import check
from ... import dataclasses as dc
from ... import orm


@pytest.mark.asyncs('asyncio')
async def test_final():
    @dc.dataclass(kw_only=True)
    class Foo:
        id: orm.Key[int] = orm.auto_key()

        mut: str | None = None
        immut: str | None = None

    registry = orm.registry(
        orm.dataclass_mapper(
            Foo,
            field_options=dict(
                immut=[orm.FinalFieldOption()],
            ),
        ),
    )

    store = orm.InMemoryStore()

    async with orm.session(registry, store):
        foo0 = await orm.add_one(Foo())
        assert foo0.mut is None
        assert foo0.immut is None

    async with orm.session(registry, store):
        foo1 = check.not_none(await orm.get(Foo, foo0.id))
        assert foo1.mut is None
        assert foo1.immut is None
        foo1.mut = 'mut!'
        assert foo1.mut == 'mut!'
        assert foo1.immut is None

    async with orm.session(registry, store):
        foo1 = check.not_none(await orm.get(Foo, foo0.id))
        assert foo1.mut == 'mut!'
        assert foo1.immut is None

    with pytest.raises(orm.FinalFieldModifiedError):
        async with orm.session(registry, store):
            foo1 = check.not_none(await orm.get(Foo, foo0.id))
            foo1.immut = 'immut!'
