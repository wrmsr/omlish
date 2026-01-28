from omlish import sql
from omlish.sql.tabledefs.lower import lower_table_elements
from omlish.sql.tabledefs.rendering import render_create_statements

from .models import NODES


##


def setup_db(conn: sql.Querier) -> None:
    for stmt in render_create_statements(lower_table_elements(NODES)):
        sql.exec(conn, stmt)
