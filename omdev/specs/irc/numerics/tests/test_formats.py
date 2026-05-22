from ..formats import Formats
from ..numerics import NUMERIC_REPLIES


def test_pats():
    for nr in NUMERIC_REPLIES:
        for nrf in nr.formats:
            ps = Formats.split_parts(nrf)
            r = ''.join(Formats.render_parts(ps))
            assert r == nrf
