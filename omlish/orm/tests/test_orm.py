import concurrent.futures as cf
import contextlib
import os.path
import sqlite3
import tempfile
import typing as ta

import pytest

from ... import lang
from ... import orm
from ... import sql
from ...asyncs.asyncio import all as au
from ..registries import Registry
from ..sql import SqlStore
from ..stores import Store
from .models import Business
from .models import Review
from .models import User
from .models import build_registry


##


async def _test_orm(store: Store, registry: Registry | None = None) -> None:
    if registry is None:
        registry = build_registry()

    # b = Business(id=orm.key(1), name='foo')  # noqa
    # u = User(id=orm.key(2), name='bar')  # noqa
    # r = Review(id=orm.key(3), business=orm.ref(Business, b.id), user=orm.ref(User, u.id), text='baz')
    # print(r)
    #
    # store = orm.InMemoryStore()
    #
    # with orm.Session(registry, store).activate() as session:
    #     session.add(b, u, r)
    #     assert r.business() is b
    #     r2 = session.get(Review, 3)
    #     assert r2 is r
    #
    #     session.flush()
    #
    # with orm.Session(registry, store).activate() as session:
    #     r3 = session.get(Review, 3)
    #     print(r3)

    async with orm.session(registry, store):
        alice = User(name='Alice')
        bob = User(name='Bob')
        charlie = User(id=orm.key(100), name='Charlie')

        diner = Business(name="Alice's Diner")
        sushi = Business(name='Sushi Spot')

        await orm.add(alice)
        await orm.add(bob)
        await orm.add(charlie)

        await orm.add(diner)
        await orm.add(sushi)

        await orm.add(Review(business=orm.ref(Business, 1), user=orm.ref(User, 1), text='great pie'))
        await orm.add(Review(business=orm.ref(diner), user=orm.ref(User, 2), text='solid brunch'))

        await orm.add(Review(business=orm.ref(Business, 2), user=orm.ref(alice), text='fresh fish'))
        await orm.add(Review(business=orm.ref(sushi), user=orm.ref(User, 2), text='it aight'))
        await orm.add(Review(business=orm.ref(sushi), user=orm.ref(bob), text='it still aight'))

        assert await orm.get(User, 100) is charlie

        # pending = orm.query(Review).where_eq('business_id', 1).all()
        # print('pending reviews for business 1:', pending)

        print(await orm.query(Review, business=orm.ref(Business, 2)))

        print(await sushi.reviews())

    async with orm.session(registry, store):
        await orm.delete(await orm.get(Review, 4))

        print(await orm.query(Review, business=orm.ref(Business, 2)))

    async with orm.session(registry, store):
        print(await orm.query(Review, business=orm.ref(Business, 2)))

    async with orm.session(registry, store):
        review_1 = await orm.get(Review, 1)
        assert review_1 is not None

        assert await orm.get(Review, 1) is review_1

        review_2 = await orm.get(Review, 2)
        assert review_2 is not None

        # same_review = orm.query(Review).where_eq('id', 1).one()
        # assert same_review is review_1

        # by_business = orm.query(Review).where_eq('business_id', 1).all()
        # print('loaded reviews for business 1:', by_business)

        review_1.text = 'great pie, would return'
        # by_user = orm.query(Review).where_eq('user_id', 1).all()
        # print('reviews by user 1 before commit:', by_user)

        # Current API nod toward future multi-hop paths:
        # orm.query(Review).where_eq(("business", "name"), "Alice's Diner")

    async with orm.session(registry, store):
        [alice] = await orm.query(User, name='Alice')
        print(alice)
        alice.favorite_business = orm.ref(Business, 2)
        print(alice)
        print(await alice.favorite_business())

    async with orm.session(registry, store):
        [alice] = await orm.query(User, name='Alice')
        print(alice)
        print(await alice.favorite_business())  # type: ignore


@pytest.mark.asyncs('asyncio')
async def test_orm_in_memory():
    await _test_orm(orm.InMemoryStore())


@pytest.mark.asyncs('asyncio')
async def test_orm_sql():
    db_path = os.path.join(tempfile.mkdtemp(), 'orm.db')
    registry = build_registry()
    with cf.ThreadPoolExecutor(max_workers=1) as exe:
        db = sql.api.DbapiDb(lambda: contextlib.closing(sqlite3.connect(db_path)))
        adb = sql.api.SyncToAsyncDb(ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToThread(exe=exe))), db)
        store = SqlStore(registry, adb)
        await _test_orm(store, registry)
