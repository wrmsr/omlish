from .. import simple as simple_


def test_set_once_property():
    class A:
        value = simple_.set_once()

    a = A()
    try:
        a.value
    except ValueError:
        pass
    else:
        raise ValueError('Expected exception')
    a.value = 1
    assert a.value == 1
