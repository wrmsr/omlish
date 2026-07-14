from .. import transforms as tf


def test_transforms():
    foo: tf.Transform[int, int] = tf.flat_map[int, int](lambda x: [x, x + 10])

    it = foo(range(3))
    assert list(it) == [0, 10, 1, 11, 2, 12]

    l: list = []
    foo = tf.compose(
        foo,
        tf.apply[int](l.append),
        tf.map(lambda i: i + 1),
    )

    it = foo(range(3))
    assert not l
    assert list(it) == [1, 11, 2, 12, 3, 13]
    assert l == [0, 10, 1, 11, 2, 12]
