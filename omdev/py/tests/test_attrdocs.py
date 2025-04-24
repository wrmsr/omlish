import inspect
import pprint

from ..attrdocs import extract_attr_docs


# Blah
SOME_GLOBAL = 42  # Huh
"""What?"""


class Foo:
    class Bar:
        x: int = 5
        'Foo.Bar.x'

    y: str = 'y'
    'Foo.y'

    z: int
    'Foo.z'


class Baz:
    class Qux:
        a: int = 5
        'Baz.Bar.a'

    b: str = 'y'
    'Baz.b'

    c: int
    'Baz.c'

    # Baz.d preceding
    # more
    d = 10  # Baz.d trailing
    'Baz.d'

    def barf(self) -> int:
        x: int = 5
        'Baz.barf.x'

        return x


def test_attr_docs():
    dsd = extract_attr_docs(inspect.getsource(Foo))
    pprint.pprint(dsd)
    print()

    #

    with open(__file__) as f:
        src = f.read()

    dsd = extract_attr_docs(src)
    pprint.pprint(dsd)
    print()
