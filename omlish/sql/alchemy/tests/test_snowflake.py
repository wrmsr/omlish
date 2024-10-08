import os.path

import pytest
import sqlalchemy as sa
import yaml

from .... import lang
from ....testing import pytest as ptu


@ptu.skip.if_cant_import('snowflake.sqlalchemy')
@pytest.mark.online
def test_snowflake():
    if not os.path.isfile(sec_file := os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')):
        pytest.skip('No secrets')

    def _load_secrets():
        with open(sec_file) as f:
            dct = yaml.safe_load(f)
        os.environ['SNOWFLAKE_URL'] = dct['snowflake_url']

    _load_secrets()

    with lang.disposing(sa.create_engine(os.environ['SNOWFLAKE_URL'])) as engine:
        with engine.connect() as conn:
            print(conn.execute(sa.text('select current_version()')).fetchone()[0])  # type: ignore
