import pytest
import sqlalchemy as sa

from .... import lang
from ....secrets.tests.harness import HarnessSecrets
from ....testing import pytest as ptu


@ptu.skip.if_cant_import('snowflake.sqlalchemy')
@pytest.mark.online
def test_snowflake(harness):
    if (url := harness[HarnessSecrets].try_get('snowflake_url')) is None:
        pytest.skip('No url')

    with lang.disposing(sa.create_engine(url.reveal())) as engine:
        with engine.connect() as conn:
            print(conn.execute(sa.text('select current_version()')).fetchone()[0])  # type: ignore
