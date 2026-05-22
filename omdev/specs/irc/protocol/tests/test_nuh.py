import dataclasses as dc
import itertools

from ..nuh import Nuh


@dc.dataclass(frozen=True)
class NuhSplitTest:
    source: str
    nuh: Nuh
    canonical: bool = False


NUH_TESTS = list(itertools.starmap(NuhSplitTest, [
    ('coolguy', Nuh('coolguy'), True),
    ('coolguy!ag@127.0.0.1', Nuh('coolguy', 'ag', '127.0.0.1'), True),
    ('coolguy!~ag@localhost', Nuh('coolguy', '~ag', 'localhost'), True),
    ('!ag@127.0.0.1', Nuh(None, 'ag', '127.0.0.1'), True),
    ('coolguy!@127.0.0.1', Nuh('coolguy', '', '127.0.0.1')),
    ('coolguy@127.0.0.1', Nuh('coolguy', None, '127.0.0.1'), True),
    ('coolguy!ag@', Nuh('coolguy', 'ag', '')),
    ('coolguy!ag', Nuh('coolguy', 'ag', None), True),
    ('coolguy!ag@net\x035w\x03ork.admin', Nuh('coolguy', 'ag', 'net\x035w\x03ork.admin'), True),
    ('coolguy!~ag@n\x02et\x0305w\x0fork.admin', Nuh('coolguy', '~ag', 'n\x02et\x0305w\x0fork.admin'), True),
    ('testnet.ergo.chat', Nuh('testnet.ergo.chat'), True),
]))


def test_splitting_nuh():
    for td in NUH_TESTS:
        pn = Nuh.parse(td.source)
        assert pn == td.nuh
        if td.canonical:
            assert pn.canonical == td.source
