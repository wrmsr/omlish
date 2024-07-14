from .. import objects as objects_


def test_pickle():
    c = objects_.pickle()
    d0 = {'a': 'b'}
    buf = c.encode(d0)
    d1 = c.decode(buf)
    assert d0 == d1


def test_yaml():
    c = objects_.yaml()
    dct = {1: 2}
    assert isinstance(c.encode(dct), str)
    assert c.decode(c.encode(dct)) == dct


def test_bson():
    c = objects_.bson()
    dct = {'a': 2}
    assert isinstance(c.encode(dct), bytes)
    assert c.decode(c.encode(dct)) == dct


def test_cbor():
    c = objects_.cbor()
    dct = {1: 2}
    assert isinstance(c.encode(dct), bytes)
    assert c.decode(c.encode(dct)) == dct


def test_toml():
    c = objects_.toml()
    dct = {'x': 2}
    assert isinstance(c.encode(dct), str)
    assert c.decode(c.encode(dct)) == dct
