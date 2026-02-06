from omlish import sql

from .models import NODES


##


def setup_db(conn: sql.Querier) -> None:
    for stmt in sql.td.render_create_statements(sql.td.lower_table_elements(NODES)):
        sql.exec(conn, stmt)
