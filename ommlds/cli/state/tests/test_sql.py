import pytest

from ..sql import SqlStateStorage


@pytest.mark.xfail(reason='WIP')
@pytest.mark.asyncs('asyncio')
async def test_sql(tmp_path):
    ss = SqlStateStorage(SqlStateStorage.Config(
        file=tmp_path / 'state.db',
    ))
    assert (await ss.load_state('barf', str)) is None
    await ss.save_state('barf', 'foo', str)
    assert (await ss.load_state('barf', str)) == 'foo'
