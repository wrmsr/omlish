from ... import orm
from .models import Business
from .models import Review
from .models import User
from .models import build_registry


##


def test_orm():
    registry = build_registry()

    store = orm.InMemoryStore()

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

    with orm.session(registry, store):
        alice = User(id=orm.key(1), name='Alice')
        bob = User(name='Bob')
        diner = Business(name="Alice's Diner")
        sushi = Business(name='Sushi Spot')

        orm.add(alice)
        orm.add(bob)
        orm.add(diner)
        orm.add(sushi)

        orm.add(Review(id=orm.key(1), business=orm.ref(Business, 1), user=orm.ref(User, 1), text='great pie'))
        orm.add(Review(business=orm.ref(diner), user=orm.ref(User, 2), text='solid brunch'))
        orm.add(Review(business=orm.ref(Business, 2), user=orm.ref(User, 1), text='fresh fish'))
        orm.add(Review(business=orm.ref(Business, 2), user=orm.ref(User, 2), text='it aight'))
        orm.add(Review(business=orm.ref(Business, 2), user=orm.ref(User, 2), text='it still aight'))

        assert orm.get(User, 1) is alice

        # pending = orm.query(Review).where_eq('business_id', 1).all()
        # print('pending reviews for business 1:', pending)

        print(orm.query(Review, business=orm.ref(Business, 2)))

        print(sushi.reviews())

    with orm.session(registry, store):
        orm.delete(orm.get(Review, 4))

        print(orm.query(Review, business=orm.ref(Business, 2)))

    with orm.session(registry, store):
        print(orm.query(Review, business=orm.ref(Business, 2)))

    with orm.session(registry, store):
        review_1 = orm.get(Review, 1)
        assert review_1 is not None

        assert orm.get(Review, 1) is review_1

        review_2 = orm.get(Review, 2)
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

    with orm.session(registry, store):
        [alice] = orm.query(User, name='Alice')
        print(alice)
        alice.favorite_business = orm.ref(Business, 2)
        print(alice)
        print(alice.favorite_business())

    with orm.session(registry, store):
        [alice] = orm.query(User, name='Alice')
        print(alice)
        print(alice.favorite_business())  # type: ignore
