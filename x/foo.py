import dataclasses as dc

from .cli import CliModule


SOME_CONST = 420


@dc.dataclass(frozen=True)
class SomeManifestThing:
    some_const: int


# @omlish-manifest
_FOO_MANIFEST = SomeManifestThing(some_const=SOME_CONST)

# @omlish-manifest
_FOO_MANIFEST2 = {'$x.foo.SomeManifestThing': {'some_const': SOME_CONST}}


##


# @omlish-manifest
_FOO_CLI_MODULE = CliModule('foo', __name__)


def _main() -> None:
    print('foo!')


if __name__ == '__main__':
    _main()
