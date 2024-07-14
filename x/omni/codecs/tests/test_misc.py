from .. import misc as misc_


def test_lines():
    c = misc_.lines()
    assert c.decode(c.encode(['a', 'b'])) == ['a', 'b']
