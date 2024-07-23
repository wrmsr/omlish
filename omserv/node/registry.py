"""
TODO:
 - async engine / conn adapter :|
 - serverside created_at/updated_at
"""
import contextlib
import dataclasses as dc
import socket
import textwrap
import typing as ta
import uuid

import anyio
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as saa
import sqlalchemy.ext.compiler
import sqlalchemy.orm
import sqlalchemy.sql.elements

from omlish import asyncs as au
from omlish import check
from omlish import sql

from ..secrets import load_secrets  # noqa


##


class IdMixin:
    _id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)


##


class utcnow(sa.sql.expression.FunctionElement):
    type = sa.TIMESTAMP()


@sa.ext.compiler.compiles(utcnow)
def _compile_utcnow(
        element: utcnow,
        compiler: sa.sql.compiler.SQLCompiler,
        **kw: ta.Any,
) -> str:
    return "timezone('utc', now())"


##


class TimestampsMixin:
    created_at = sa.Column(
        sa.TIMESTAMP(timezone=True),
        server_default=utcnow(),
        nullable=False,
    )

    updated_at = sa.Column(
        sa.TIMESTAMP(timezone=True),
        server_default=utcnow(),
        server_onupdate=sa.schema.FetchedValue(for_update=True),
        nullable=False,
    )


##


CREATE_UPDATED_AT_FUNCTION_STATEMENT = textwrap.dedent("""
    create or replace function set_updated_at_timestamp()
    returns trigger as $$
    begin
        new.updated_at = now() at time zone 'utc';
        return new;
    end;
    $$ language 'plpgsql';
""")


##


def get_update_at_trigger_name(table_name: str) -> str:
    return f'trigger__updated_at_{table_name}'


#


class CreateUpdateAtTrigger(sa.schema.DDLElement):
    def __init__(self, table_name: str) -> None:
        super().__init__()
        self.table_name = table_name


@sa.ext.compiler.compiles(CreateUpdateAtTrigger)
def _compile_create_update_at_trigger(
        element: CreateUpdateAtTrigger,
        compiler: sa.sql.compiler.SQLCompiler,
        **kw: ta.Any,
):
    return textwrap.dedent(f"""
        create trigger {get_update_at_trigger_name(element.table_name)}
            before update
            on {element.table_name}
            for each row
            execute procedure set_updated_at_timestamp()
    """)


#


class DropUpdateAtTrigger(sa.schema.DDLElement):
    def __init__(self, table_name: str) -> None:
        super().__init__()
        self.table_name = table_name


@sa.ext.compiler.compiles(DropUpdateAtTrigger)
def _compile_drop_update_at_trigger(
        element: DropUpdateAtTrigger,
        compiler: sa.sql.compiler.SQLCompiler,
        **kw: ta.Any,
) -> str:
    return f'drop trigger if exists {get_update_at_trigger_name(element.table_name)} on {element.table_name}'


#


def create_updated_at_trigger(metadata: sa.MetaData, table_name: str) -> None:
    sa.event.listen(metadata, 'after_create', CreateUpdateAtTrigger(table_name))
    sa.event.listen(metadata, 'before_drop', DropUpdateAtTrigger(table_name))


##


Metadata = sa.MetaData()
Base: ta.Any = sa.orm.declarative_base(metadata=Metadata)


class Node(
    IdMixin,
    TimestampsMixin,
    Base,
):
    __tablename__ = 'nodes'
    __table_args__ = (
        sa.Index('nodes_by_uuid', 'uuid', unique=True),
    )

    uuid = sa.Column(sa.String(50), nullable=False, unique=True)
    hostname = sa.Column(sa.String(100), nullable=False)

    heartbeat_at = sa.Column(sa.TIMESTAMP(timezone=True))


Nodes = Node.__table__


create_updated_at_trigger(Metadata, 'nodes')


##


@dc.dataclass()
class NodeInfo:
    uuid: str
    hostname: str


class NodeRegistrant:
    def __init__(
            self,
            engine: sql.AsyncEngineLike,
    ) -> None:
        super().__init__()

        self._engine = sql.async_adapt(engine)

        self._info = NodeInfo(
            uuid=str(uuid.uuid4()).replace('-', ''),
            hostname=socket.gethostname(),
        )

    @au.mark_anyio
    async def __call__(self) -> None:
        async with contextlib.AsyncExitStack() as aes:
            conn: sql.AsyncConnection = await aes.enter_async_context(self._engine.connect())  # noqa

            nid: int

            async with conn.begin():
                rows = (await conn.execute(
                    sa.select(Nodes).where(Nodes.c.uuid == self._info.uuid)
                )).fetchall()

                if len(rows) > 0:
                    row = check.single(rows)
                    nid = row['_id']

                else:
                    result = await conn.execute(Nodes.insert(), [{
                        'uuid': self._info.uuid,
                        'hostname': self._info.hostname,
                    }])
                    nid = check.single(result.inserted_primary_key)  # noqa

            print(f'{nid=}')
            for _ in range(10):
                await anyio.sleep(1.)
                async with conn.begin():  # FIXME: real autocommit lol
                    await conn.execute(sa.update(
                        Nodes
                    ).where(
                        Nodes.c.uuid == self._info.uuid,
                    ).values(
                        heartbeat_at=utcnow(),
                    ))


##


def _get_db_url() -> str:
    cfg = load_secrets()
    return f'postgresql+asyncpg://{cfg["postgres_user"]}:{cfg["postgres_pass"]}@{cfg["postgres_host"]}:5432'


async def _a_main() -> None:
    engine = sql.async_adapt(saa.create_async_engine(_get_db_url(), echo=True))

    conn: sql.AsyncConnection
    async with engine.connect() as conn:
        async with conn.begin():
            await conn.run_sync(Metadata.drop_all)
            await conn.execute(sa.text(CREATE_UPDATED_AT_FUNCTION_STATEMENT))
            await conn.run_sync(Metadata.create_all)

    await NodeRegistrant(engine)()


if __name__ == '__main__':
    # _backend = 'asyncio'
    _backend = 'trio'

    match _backend:
        case 'asyncio':
            anyio.run(_a_main, backend='asyncio')

        case 'trio':
            from omlish.testing.pydevd import patch_for_trio_asyncio
            patch_for_trio_asyncio()  # noqa

            anyio.run(au.with_trio_asyncio_loop(_a_main), backend='trio')

        case _:
            raise RuntimeError(f'Unknown backend: {_backend}')
