import argparse
import typing as ta

from omlish import dataclasses as dc


##


class ToolPack:
    # bind() -> inj.Elements

    pass


##


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('profile')
    args, argv = parser.parse_known_args()

    print(f'{args=} {argv=}')


if __name__ == '__main__':
    _main()
