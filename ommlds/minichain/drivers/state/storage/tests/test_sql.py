import pytest

from ..sql import SqlStateStorage


@pytest.mark.asyncs('asyncio')
async def test_sql(tmp_path):
    ss = SqlStateStorage(SqlStateStorage.Config(
        file=str(tmp_path / 'state.db'),
    ))

    assert (await ss.load_state('barf', str)) is None

    await ss.save_state('barf', 'foo', str)
    assert (await ss.load_state('barf', str)) == 'foo'

    await ss.save_state('barf', 'bar', str)
    assert (await ss.load_state('barf', str)) == 'bar'

    await ss.save_state('barf', None, str)
    assert (await ss.load_state('barf', str)) is None
