"""
TODO:
 - move to omlish.sql, pg-specific trigger compiler - https://docs.sqlalchemy.org/en/20/core/compiler.html
"""
import textwrap
import typing as ta

import sqlalchemy as sa
import sqlalchemy.ext.compiler


##


class IdMixin:
    _id = sa.Column(
        sa.Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True,
    )


##


class utcnow(sa.sql.expression.FunctionElement):  # noqa
    inherit_cache = True
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
    inherit_cache = False

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
        create or replace trigger {get_update_at_trigger_name(element.table_name)}
            before update
            on {element.table_name}
            for each row
            execute procedure set_updated_at_timestamp()
    """)


#


class DropUpdateAtTrigger(sa.schema.DDLElement):
    inherit_cache = False

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


def install_updated_at_trigger(metadata: sa.MetaData, table_name: str) -> None:
    sa.event.listen(metadata, 'after_create', CreateUpdateAtTrigger(table_name))
    sa.event.listen(metadata, 'before_drop', DropUpdateAtTrigger(table_name))
