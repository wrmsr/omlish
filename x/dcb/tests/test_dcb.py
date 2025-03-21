"""
TODO:
 - ! spec goes to json !
  - 'spec'? 'inspection'? 'template'?
  - I like 'spec' for the canonical form
  - 'analysis'? 'config'? what's, like, 'primed and ready to compile'?
  - 'preprocess'?
 - !!! can re-use ONLY SPECIFIC PARTS !!!
  - fine-grained compile caching, overriding, ...
 - if this works out, go hog wild with injection, won't be used 90% of the time...
"""
import inspect

from .. import api


##


@api.dataclass(frozen=True, order=True)
class A:
    i: int
    s: str = api.field(repr_fn=lambda s: f'{s}!', override=True)
    d: int = 5
    l: list = api.field(default_factory=list)

    @api.init
    def _init_foo(self) -> None:
        print('hi!')


def test_dcb():
    print(inspect.signature(A))

    a = A(5, 'hi')  # type: ignore[call-arg]
    print(a)

    assert hash(a) == hash(A(5, 'hi'))  # type: ignore[call-arg]

    assert A(4, 'hi') < a  # type: ignore[call-arg,operator]

    match a:
        case A(i, s):  # type: ignore[misc]
            print(f'{i=} {s=}')  # type: ignore[unreachable]
        case _:
            raise RuntimeError
