import contextlib
import typing as ta
import urllib.parse

import pytest

from ... import check
from ...secrets.tests.harness import HarnessSecrets
from ...testing import pytest as ptu


@ptu.skip.if_cant_import('snowflake.connector')
@pytest.mark.online
def test_snowflake(harness):
    url = harness[HarnessSecrets].get_or_skip('snowflake_url')

    #

    pu = urllib.parse.urlparse(url.reveal())

    opts: dict[str, ta.Any] = {
        'user': urllib.parse.unquote(pu.username),
        'host': pu.hostname,
        'password': urllib.parse.unquote(pu.password),
    }

    if 'database' in opts and 'schema' not in opts:
        name_spaces = [urllib.parse.unquote_plus(e) for e in opts['database'].split('/')]
        if len(name_spaces) == 1:
            pass
        elif len(name_spaces) == 2:
            opts['database'] = name_spaces[0]
            opts['schema'] = name_spaces[1]
        else:
            raise Exception(opts['database'])

    if (
            'account' not in opts and
            'host' in opts and
            '.snowflakecomputing.com' not in opts['host'] and
            'port' not in opts
    ):
        if '.' in (account := opts['host']):
            account = account.partition('.')[0].partition('-')[0]
        opts['account'] = account
        opts['host'] += '.snowflakecomputing.com'
        opts['port'] = '443'

    opts.setdefault('autocommit', False)

    opts.setdefault('session_parameters', {})['CLIENT_TELEMETRY_ENABLED'] = False

    #

    import snowflake.connector

    with contextlib.closing(snowflake.connector.connect(**opts)) as conn:
        cur = conn.cursor()
        res = check.not_none(cur.execute('select current_version()'))
        print(res.fetchall())
        res.close()
        cur.close()
