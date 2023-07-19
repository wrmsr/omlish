from .. import classes


@classes.dataclass()
class Foo:
    x: int
    y: int


def test_foo():
    print(Foo(1, 2))
