# ruff: noqa: SLF001
import contextlib
import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from ..text import inflect
from .backrefs import Backref
from .fields import Field
from .fields import FieldOption
from .fields import KeyField
from .fields import RefField
from .indexes import Index
from .indexes import IndexOption
from .keys import Key
from .mappers import Mapper
from .mappers import MapperOption
from .queries import Query
from .refs import Ref
from .registries import Registry
from .sessions import Session
from .sessions import active_session
from .stores import Store


K = ta.TypeVar('K')
T = ta.TypeVar('T')


##


def index(
        *fields: str,
        store_name: str | None = None,
        options: ta.Sequence[IndexOption] | None = None,
) -> Index:
    check.not_empty(fields)
    for f in fields:
        check.non_empty_str(f)

    return Index(
        _fields=fields,
        _store_name=store_name,
        _options=options,
    )


def field(
        name: str,
        ty: ta.Any,
        *,
        store_name: str | None = None,
        backref_binding: ta.Any | None = None,
        options: ta.Sequence[FieldOption] | None = None,
) -> Field:
    check.non_empty_str(name)

    #

    rty = rfl.type_(ty)

    #

    fld_cls: type[Field] = Field
    if isinstance(rty, rfl.Generic):
        if rty.cls is Key:
            fld_cls = KeyField
        elif rty.cls is Ref:
            fld_cls = RefField
    elif (
            isinstance(rty, rfl.Union) and
            rty.is_optional and
            isinstance(oa := rty.without_none(), rfl.Generic) and
            oa.cls is Ref
    ):
        fld_cls = RefField

    #

    if store_name is None:
        if fld_cls is RefField:
            store_name = name + '_id'
        else:
            store_name = name

    #

    return fld_cls(
        _name=name,
        _store_name=store_name,
        _rty=rty,
        _backref_binding=backref_binding,
        _options=options,
    )


def mapper(
        cls: type,
        fields: ta.Sequence[Field] | None = None,
        *,
        store_name: str | None = None,
        indexes: ta.Sequence[Index | ta.Sequence[str] | str] | None = None,
        backrefs: ta.Sequence[Backref] | None = None,
        options: ta.Sequence[MapperOption] | None = None,
) -> Mapper:
    check.isinstance(cls, type)

    #

    if fields is None:
        if dc.is_dataclass(cls):
            return dataclass_mapper(
                cls,
                store_name=store_name,
                indexes=indexes,
            )
        else:
            raise ValueError(f'Must provide fields for class {cls!r}')

    #

    if store_name is None:
        ns = lang.split_string_casing(cls.__name__)
        store_name = '_'.join([*ns[:-1], inflect.tableize(ns[-1])])

    #

    fields_by_name = col.make_map(((f.name, f) for f in fields), strict=True)

    #

    index_lst: list[Index] = []

    for ia in indexes or ():
        if not isinstance(ia, Index):
            if isinstance(ia, str):
                ia = [ia]
            ia = index(*ia)

        if ia._given_store_name is None:
            dsn = '__'.join([
                store_name,
                *[fields_by_name[f].store_name for f in ia.fields],
            ])
            ia = ia._with_store_name(dsn)

        index_lst.append(ia)

    #

    return Mapper(
        cls,  # noqa
        store_name,
        fields,
        indexes=index_lst,
        backrefs=backrefs,
        options=options,
    )


def dataclass_mapper(
        cls: type,
        *,
        store_name: str | None = None,
        field_options: ta.Mapping[str, ta.Sequence[FieldOption]] | None = None,
        indexes: ta.Sequence[Index | ta.Sequence[str] | str] | None = None,
        options: ta.Sequence[MapperOption] | None = None,
) -> Mapper:
    check.arg(dc.is_dataclass(cls))

    dc_rfl = dc.reflect(cls)

    #

    field_options = dict(field_options or {})

    fields: list[Field] = []

    for df in dc_rfl.fields.values():  # noqa
        df_os = field_options.pop(df.name, None)

        fields.append(field(
            df.name,
            dc_rfl.field_annotations[df.name],
            backref_binding=df,
            options=df_os or None,
        ))

    check.empty(field_options)

    backrefs: list[Backref] = []

    for cdf in dc_rfl.fields_inspection.cls_fields.values():
        if isinstance(br := cdf.default, Backref):
            backrefs.append(br)

    #

    return mapper(
        cls,  # noqa
        fields,
        store_name=store_name,
        indexes=indexes,
        backrefs=backrefs,
        options=options,
    )


def registry(*mappers: Mapper | type) -> Registry:
    mapper_lst: list[Mapper] = []

    for a in mappers:
        if isinstance(a, Mapper):
            mapper_lst.append(a)
        elif isinstance(a, type):
            mapper_lst.append(mapper(a))
        else:
            raise TypeError(a)

    return Registry(mapper_lst)


#


def session(
        registry: Registry,  # noqa
        store: Store,
        *,
        no_auto_flush: bool = False,
) -> ta.AsyncContextManager[Session]:
    @contextlib.asynccontextmanager
    async def inner():
        async with Session(
            registry,
            store,
            no_auto_flush=no_auto_flush,
        ) as sess:
            async with sess.activate():
                yield sess

    return inner()


async def abort() -> None:
    await active_session().abort()


async def add(*objs: ta.Any) -> None:
    return await active_session().add(*objs)


async def add_one(obj: T) -> T:
    await add(obj)
    return obj


@ta.overload
async def get(cls: type[T], k: Key[K]) -> T | None:
    ...


@ta.overload
async def get(cls: type[T], k: K) -> T | None:
    ...


async def get(cls, k):  # noqa
    return await active_session().get(cls, k)


async def delete(*objs: ta.Any) -> None:
    await active_session().delete(*objs)


async def flush() -> None:
    await active_session().flush()


async def refresh(*objs: ta.Any) -> None:
    await active_session().refresh(*objs)


async def refresh_one(obj: T) -> T:
    await active_session().refresh(obj)
    return obj


#


def make_query(
        cls: type[T],
        **where: ta.Any,
) -> Query[T]:
    return Query(
        cls,
        where,
    )


async def query(
        cls: type[T],
        **where: ta.Any,
) -> list[T]:
    return await active_session().query(make_query(cls, **where))


async def query_one(
        cls: type[T],
        **where: ta.Any,
) -> T | None:
    objs = await query(cls, **where)
    if not objs:
        return None
    return check.single(objs)
