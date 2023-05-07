import pickle

import pytest

from .. import lang as lang_


def test_empty_map():
    ed = lang_.EmptyMap()
    assert len(ed) == 0
    with pytest.raises(KeyError):
        ed['x']
    buf = pickle.dumps(ed)
    ed2 = pickle.loads(buf)
    assert ed2 is ed
