# ruff: noqa: SLF001
import contextlib
import typing as ta

from .. import check
from .. import reflect as rfl
from .. import sql
from .fields import Field
from .fields import KeyField
from .fields import RefField
from .mappers import Mapper
from .registries import Registry
from .snaps import Snap
from .stores import Store
from .wrappers import WRAPPER_TYPES


##


class SqlStore(Store):
    def __init__(self, registry: Registry, db: sql.api.AsyncDb | sql.api.AsyncConn) -> None:
        super().__init__()

        self._registry = registry
        self._db = db

    #

    def _field_column_def(self, field: Field) -> str:
        sfx: list[str] = []
        rty: rfl.Type

        handled_optional = False

        if isinstance(field, KeyField):
            rty = field.key_cls
            sfx.append('primary key')

        elif isinstance(field, RefField):
            rty = field.ref_key_cls
            if not field.optional:
                sfx.append('not null')
            handled_optional = True

        else:
            rty = field.rty

        if isinstance(rty, rfl.Union) and rty.is_optional:
            rty = rty.without_none()
        else:
            if not handled_optional:
                sfx.append('not null')

        parts: list[str] = [field.store_name]

        if rty is int:
            parts.append('integer')
        elif rty is str:
            parts.append('text')
        else:
            raise TypeError(f'unsupported sql field type: {rty!r}')

        return ' '.join([*parts, *sfx])

    async def _create_schema(self) -> None:
        async with sql.api.connect(self._db) as conn:
            for mapper in self._registry.mappers:
                await sql.api.exec(conn, ' '.join([
                    f'create table if not exists {mapper.store_name}',
                    f'({", ".join(self._field_column_def(f) for f in mapper.fields)})',
                ]))

                for idx in mapper.indexes:
                    await sql.api.exec(conn, ' '.join([
                        f'create index if not exists {idx.store_name} on {mapper.store_name}'
                        f'({" ".join(mapper.store_name_by_field_name[f] for f in idx.fields)})',
                    ]))

    _has_created_schema: bool = False

    async def _maybe_create_schema(self) -> None:
        if self._has_created_schema:
            return

        await self._create_schema()
        self._has_created_schema = True

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

        _conn: sql.api.AsyncConn | None = None
        _txn: sql.api.AsyncTransaction | None = None
        _q: sql.api.AsyncQuerier | None = None

        @property
        def store(self) -> 'SqlStore':
            return self._o

        #

        async def __aenter__(self) -> ta.Self:
            await self._es.__aenter__()

            self._conn = await self._es.enter_async_context(sql.api.connect(self._o._db))

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
            clauses: list[str] = []
            params: list[ta.Any] = []

            for fk, fv in where.items():
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

            async with sql.api.query(check.not_none(self._q), stmt, params) as rows:
                return [row.to_dict() async for row in rows]

        #

        def _build_insert_stmt(self, m: Mapper, *, auto_key: bool = False) -> str:
            return ' '.join([
                'insert into',
                m._store_name,
                ''.join([
                    '(',
                    ', '.join([
                        f._store_name
                        for f in m._fields if not (f is m._key_field and auto_key)
                    ]),
                    ')',
                ]),
                'values',
                ''.join([
                    '(',
                    ', '.join([
                        '?'
                        for _ in range(len(m._fields) - (1 if auto_key else 0))
                    ]),
                    ')',
                ]),
                *(['returning id'] if auto_key else []),
            ])

        async def auto_key_insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> ta.Mapping[ta.Any, ta.Any]:
            await self._o._maybe_create_schema()

            stmt = self._build_insert_stmt(m, auto_key=True)

            iak: dict[ta.Any, ta.Any] = {}

            for snap in snaps:
                ak = snap[m._key_field._store_name]
                params = [snap[f._store_name] for f in m._fields if f is not m._key_field]
                vk = await sql.api.query_scalar(check.not_none(self._q), stmt, params)
                iak[ak] = vk

            return iak

        async def insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> None:
            await self._o._maybe_create_schema()

            stmt = self._build_insert_stmt(m)

            for snap in snaps:
                params = [snap[f._store_name] for f in m._fields]
                await sql.api.exec(check.not_none(self._q), stmt, params)

        async def update(self, m: Mapper, diffs: ta.Sequence[tuple[ta.Any, Snap]]) -> None:
            await self._o._maybe_create_schema()

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
                params = [*ud_diff.values(), vk]
                await sql.api.exec(check.not_none(self._q), stmt, params)

        async def delete(self, m: Mapper, keys: ta.Sequence[ta.Any]) -> None:
            await self._o._maybe_create_schema()

            stmt = ' '.join([
                'delete from',
                m._store_name,
                'where',
                m._key_field_store_name,
                '= ?',
            ])

            for k in keys:
                await sql.api.exec(check.not_none(self._q), stmt, [k])

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
