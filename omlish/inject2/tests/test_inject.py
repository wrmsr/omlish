import pprint

from ... import inject2 as inj


def test_inject():
    es = inj.Elements([
        inj.as_binding(420),
    ])

    pprint.pprint(es)
