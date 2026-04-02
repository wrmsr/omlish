import typing as ta

from ... import dataclasses as dc
from ... import orm


##


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class BusinessCategory:
    id: orm.Key[int] = dc.field(default_factory=orm.auto_key)

    business: orm.Ref['Business', int]

    tag: str


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class Business:
    id: orm.Key[int] = dc.field(default_factory=orm.auto_key)

    name: str

    categories: ta.ClassVar[orm.Backref[BusinessCategory]] = orm.backref(lambda: BusinessCategory.business)  # type: ignore[misc]  # noqa
    reviews: ta.ClassVar[orm.Backref['Review']] = orm.backref(lambda: Review.business)  # type: ignore[misc]  # noqa


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class User:
    id: orm.Key[int] = dc.field(default_factory=orm.auto_key)

    name: str

    _: dc.KW_ONLY

    favorite_business: orm.Ref[Business, int] | None = None

    src_relations: ta.ClassVar[orm.Backref['UserRelation']] = orm.backref(lambda: UserRelation.src)  # type: ignore[misc]  # noqa
    dst_relations: ta.ClassVar[orm.Backref['UserRelation']] = orm.backref(lambda: UserRelation.dst)  # type: ignore[misc]  # noqa

    reviews: ta.ClassVar[orm.Backref['Review']] = orm.backref(lambda: Review.user)  # type: ignore[misc]  # noqa


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class UserRelation:
    id: orm.Key[int] = dc.field(default_factory=orm.auto_key)

    src: orm.Ref[User, int]
    dst: orm.Ref[User, int]


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class Review:
    id: orm.Key[int] = dc.field(default_factory=orm.auto_key)

    business: orm.Ref[Business, int]
    user: orm.Ref[User, int]

    text: str


##


def build_registry() -> orm.Registry:
    return orm.registry(
        orm.mapper(Business, indexes=['name']),
        orm.mapper(BusinessCategory, indexes=['business']),
        orm.mapper(User, indexes=['name']),
        orm.mapper(UserRelation, indexes=['src', 'dst']),
        orm.mapper(Review, indexes=['business', 'user']),
        codec=orm.MarshalCodec(),
    )
