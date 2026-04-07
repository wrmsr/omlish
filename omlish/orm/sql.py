# ruff: noqa: SLF001
"""
====

return sql.api.query_opt_one(db, lang.static(lambda: Q.select(
    [Q.i.value],
    Q.n.states,
    Q.eq(Q.n.key, Q.p.key),
)), {
    Q.p.key: key,
})

====

if mj is None:
    sql.api.exec(txn, Q.delete(
        Q.n.states,
        where=Q.eq(Q.n.key, key),
    ))

elif sql.api.query_scalar(txn, Q.select([
    Q.f.exists(Q.select(
        [1],
        Q.n.states,
        Q.eq(Q.n.key, key),
    )),
])):
    sql.api.exec(txn, Q.update(
        Q.n.states,
        [(Q.i.value, mj)],
        where=Q.eq(Q.i.key, key),
    ))

else:
    sql.api.exec(txn, Q.insert(
        [Q.i.key, Q.i.value],
        Q.n.states,
        [key, mj],
    ))
"""
import contextlib
import datetime
import typing as ta
import uuid

from .. import check
from .. import lang
from .. import reflect as rfl
from .. import sql
from .. import typedvalues as tv
from .fields import Field
from .fields import KeyField
from .fields import RefField
from .indexes import Index
from .mappers import Mapper
from .options import FieldOption
from .registries import Registry
from .snaps import Snap
from .stores import Store
from .timestamps import CreatedAt
from .timestamps import Timestamp
from .timestamps import UpdatedAt
from .wrappers import WRAPPER_TYPES


##


class FieldSqlType(tv.UniqueScalarTypedValue[sql.td.Dtype], FieldOption, lang.Final):
    pass


##


class SqlStore(Store):
    def __init__(self, registry: Registry, db: sql.AsyncDb | sql.AsyncConn) -> None:
        super().__init__()

        self._registry = registry
        self._db = db

        self._mappers: ta.Mapping[Mapper, SqlStore._Mapper] = {m: self._Mapper(self, m) for m in registry.mappers}

    #

    class _Mapper:
        def __init__(self, o: 'SqlStore', m: Mapper) -> None:
            super().__init__()

            self.o = o
            self.m = m

            self.field_encoders: dict[str, ta.Callable[[ta.Any], ta.Any]] = {}
            self.field_decoders: dict[str, ta.Callable[[ta.Any], ta.Any]] = {}

            for f in m.fields:
                rty = f.unwrapped_rty

                if isinstance(rty, rfl.Union) and rty.is_optional:
                    rty = rty.without_none()

                if rty is datetime.datetime:
                    self.field_decoders[f._store_name] = o._decode_datetime

                elif rty is uuid.UUID:
                    self.field_encoders[f._store_name] = o._encode_uuid
                    self.field_decoders[f._store_name] = o._decode_uuid

            self.encode_key = self.field_encoders.get(m._key_field_store_name, lang.identity)
            self.decode_key = self.field_decoders.get(m._key_field_store_name, lang.identity)

        def encode(self, snap: ta.Mapping[str, ta.Any]) -> ta.Mapping[str, ta.Any]:
            fes = self.field_encoders
            return {
                k: fe(v) if (fe := fes.get(k)) is not None else v
                for k, v in snap.items()
            }

        def decode(self, row: ta.Mapping[str, ta.Any]) -> Snap:
            fds = self.field_decoders
            return {
                k: fd(v) if (fd := fds.get(k)) is not None else v
                for k, v in row.items()
            }

    #

    def _decode_datetime(self, o: ta.Any) -> datetime.datetime | None:
        if o is None or isinstance(o, datetime.datetime):
            return o
        dt = datetime.datetime.fromisoformat(o)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.UTC)
        return dt

    def _encode_uuid(self, o: uuid.UUID | None) -> ta.Any | None:
        if o is None:
            return o
        return str(check.isinstance(o, uuid.UUID))

    def _decode_uuid(self, o: ta.Any) -> uuid.UUID | None:
        if o is None or isinstance(o, uuid.UUID):
            return o
        return uuid.UUID(check.isinstance(o, str))

    #

    def _field_table_def(self, field: Field) -> list[sql.td.Element]:
        if Timestamp in field.options:
            check.is_(field.rty, datetime.datetime)

            if CreatedAt in field.options:
                check.equal(field.name, 'created_at')
                return [sql.td.CreatedAt()]

            elif UpdatedAt in field.options:
                check.equal(field.name, 'updated_at')
                return [sql.td.UpdatedAt()]

            else:
                raise RuntimeError(f'Unknown timestamp field type {field}')

        els: list[sql.td.Element] = []

        rty: rfl.Type
        nullable: bool | None = None

        if isinstance(field, KeyField):
            rty = field.key_cls
            els.append(sql.td.PrimaryKey([field._store_name]))

        elif isinstance(field, RefField):
            rty = field.ref_key_cls
            nullable = field.optional

        else:
            rty = field.rty

        if isinstance(rty, rfl.Union) and rty.is_optional:
            rty = rty.without_none()
            nullable = True
        else:
            if nullable is None:
                nullable = False

        dty: sql.td.Dtype

        if (dty_opt := field.options.get(FieldSqlType)) is not None:
            dty = dty_opt.v

        elif rty is int:
            dty = sql.td.Integer()

        elif rty in (str, uuid.UUID):
            dty = sql.td.String()

        elif rty is datetime.datetime:
            dty = sql.td.Datetime()

        else:
            raise TypeError(f'unsupported sql field type: {rty!r}')

        els.append(sql.td.Column(
            field._store_name,
            dty,
            nullable=nullable,
        ))

        return els

    def _index_table_def(self, m: Mapper, idx: Index) -> list[sql.td.Element]:
        return [sql.td.Index(
            columns=[m._store_name_by_field_name[f] for f in idx.fields],
            name=idx._store_name,
        )]

    def _mapper_table_def(self, m: Mapper) -> sql.td.TableDef:
        els: list[sql.td.Element] = []

        for f in m.fields:
            els.extend(self._field_table_def(f))

        for idx in m.indexes:
            els.extend(self._index_table_def(m, idx))

        return sql.td.table_def(
            m._store_name,
            *els,
        )

    async def _create_schema(self) -> None:
        async with sql.connect(self._db) as conn:
            for m in self._registry.mappers:
                td = self._mapper_table_def(m)

                for stmt in sql.td.render_create_statements(
                        sql.td.lower_table_elements(td),
                        if_not_exists=True,
                ):
                    await sql.api.exec(conn, stmt)

    _has_created_schema: bool = False

    async def _maybe_create_schema(self) -> None:
        if self._has_created_schema:
            return

        await self._create_schema()
        self._has_created_schema = True

    #

    class _Context(Store.Context):
        def __init__(
                self,
                o: 'SqlStore',
                *,
                no_transaction: bool = False,
        ) -> None:
            super().__init__()

            self._o = o

            self._no_transaction = no_transaction

            self._es = contextlib.AsyncExitStack()

        _conn: sql.AsyncConn | None = None
        _txn: sql.AsyncTxn | None = None
        _q: sql.AsyncQuerier | None = None

        @property
        def store(self) -> 'SqlStore':
            return self._o

        #

        async def __aenter__(self) -> ta.Self:
            await self._es.__aenter__()

            self._conn = await self._es.enter_async_context(sql.connect(self._o._db))

            if not self._no_transaction:
                self._txn = await self._es.enter_async_context(self._conn.begin())
                self._q = self._txn
            else:
                self._q = self._conn

            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self._es.__aexit__(exc_type, exc_val, exc_tb)

        #

        async def finish(self) -> None:
            if not self._no_transaction:
                await check.not_none(self._txn).commit()

        async def abort(self) -> None:
            if not self._no_transaction:
                await check.not_none(self._txn).rollback()

        #

        async def fetch(self, m: Mapper, k: ta.Any) -> Snap | None:
            rows = await self.lookup(m, {m.key_field.store_name: k})
            return check.single(rows) if rows else None

        async def lookup(self, m: Mapper, where: ta.Mapping[str, ta.Any]) -> ta.Sequence[Snap]:
            sm = self._o._mappers[m]

            clauses: list[str] = []
            params: list[ta.Any] = []

            for fk, fv in sm.encode(where).items():
                check.not_in(fv.__class__, WRAPPER_TYPES)
                clauses.append(f'{fk} = ?')
                params.append(fv)

            stmt = ' '.join([
                'select',
                ', '.join(m._store_name_by_field_name.values()),
                'from',
                m._store_name,
                *(['where', ' and '.join(clauses)] if clauses else []),
            ])

            await self._o._maybe_create_schema()

            async with sql.query(check.not_none(self._q), stmt, params) as rows:
                return [sm.decode(row.to_dict()) async for row in rows]

        #

        def _build_insert_stmt(self, m: Mapper, *, auto_key: bool = False) -> str:
            return ' '.join([
                'insert into',
                m._store_name,
                ''.join([
                    '(',
                    ', '.join([
                        f._store_name
                        for f in m._fields
                        if not ((f is m._key_field and auto_key) or f in m._auto_value_fields)
                    ]),
                    ')',
                ]),
                'values',
                ''.join([
                    '(',
                    ', '.join([
                        '?'
                        for _ in range(len(m._fields) - (1 if auto_key else 0) - len(m._auto_value_fields))
                    ]),
                    ')',
                ]),
                *(['returning id'] if auto_key else []),
            ])

        async def auto_key_insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> ta.Mapping[ta.Any, ta.Any]:
            await self._o._maybe_create_schema()

            sm = self._o._mappers[m]

            stmt = self._build_insert_stmt(m, auto_key=True)

            iak: dict[ta.Any, ta.Any] = {}

            for snap in snaps:
                ak = snap[m._key_field_store_name]
                enc_snap = sm.encode(snap)
                params = [
                    enc_snap[f._store_name]
                    for f in m._fields
                    if f is not m._key_field and f not in m._auto_value_fields
                ]
                vk = await sql.query_scalar(check.not_none(self._q), stmt, params)
                iak[ak] = sm.decode_key(vk)

            return iak

        async def insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> None:
            await self._o._maybe_create_schema()

            sm = self._o._mappers[m]

            stmt = self._build_insert_stmt(m)

            for snap in snaps:
                enc_snap = sm.encode(snap)
                params = [
                    enc_snap[f._store_name]
                    for f in m._fields
                    if f not in m._auto_value_fields
                ]
                await sql.exec(check.not_none(self._q), stmt, params)

        async def update(self, m: Mapper, diffs: ta.Sequence[tuple[ta.Any, Snap]]) -> None:
            await self._o._maybe_create_schema()

            sm = self._o._mappers[m]

            for vk, ud_diff in diffs:
                check.not_in(m._key_field_store_name, ud_diff)
                stmt = ' '.join([
                    'update',
                    m._store_name,
                    'set',
                    ', '.join([f'{k} = ?' for k in ud_diff]),
                    'where',
                    m._key_field_store_name,
                    '= ?',
                ])
                params = [*sm.encode(ud_diff).values(), sm.encode_key(vk)]
                await sql.exec(check.not_none(self._q), stmt, params)

        async def delete(self, m: Mapper, keys: ta.Sequence[ta.Any]) -> None:
            await self._o._maybe_create_schema()

            sm = self._o._mappers[m]

            stmt = ' '.join([
                'delete from',
                m._store_name,
                'where',
                m._key_field_store_name,
                '= ?',
            ])

            for k in keys:
                await sql.exec(check.not_none(self._q), stmt, [sm.encode_key(k)])

    #

    def create_context(
            self,
            *,
            transaction: bool | ta.Literal['default'] = 'default',
    ) -> ta.AsyncContextManager[Store.Context]:
        return self._Context(
            self,
            no_transaction=False if transaction == 'default' else not transaction,
        )
