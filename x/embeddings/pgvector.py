"""
https://www.reddit.com/r/PostgreSQL/comments/1fq6s35/18_months_of_pgvector_learnings_in_47
"""
import contextlib
import os.path

import sqlalchemy as sa

from omlish import check
from omlish import lang
from omlish.docker.tests.services import ComposeServices
from omlish.sql import dbs
from omlish.sql.tests.dbs import TestingDbs


def _main():
    cs = ComposeServices(
        config_file_path=os.path.join(os.path.dirname(__file__), '../../docker/compose.yml'),
    )
    ds = TestingDbs(cs)

    url = check.isinstance(check.isinstance(ds.specs()['pgvector'].loc, dbs.UrlDbLoc).url, str)
    url = dbs.set_url_engine(url, 'postgresql+pg8000')

    with contextlib.ExitStack() as es:
        engine = sa.create_engine(url, echo=True)
        es.enter_context(lang.defer(engine.dispose))

        with engine.connect() as conn:
            for stmt in [
                'create extension vector',
                'drop table if exists items',
                'create table items (id bigserial primary key, embedding vector(3))',
                "insert into items (embedding) values ('[1,2,3]'), ('[4,5,6]')",
                "select * from items order by embedding <-> '[3,1,2]' limit 5",
            ]:
                print(stmt)
                result = conn.execute(sa.text(stmt))
                if result.returns_rows:
                    print(list(result))


if __name__ == '__main__':
    _main()
