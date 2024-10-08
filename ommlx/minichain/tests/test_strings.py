from ..strings import transform_strings


def test_transforms():
    assert transform_strings(lambda s: s + '!', 'hello') == 'hello!'
    assert transform_strings(lambda s: s + '!', ['hello', 'there']) == ['hello!', 'there!']
