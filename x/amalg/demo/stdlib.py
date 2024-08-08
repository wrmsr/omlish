import os.path  # noqa
import pprint  # noqa
import typing as ta  # noqa


##


T = ta.TypeVar('T')


##
# x.amalg.demo.stdlib


def check_not_none(obj: ta.Optional[T]) -> T:
    if obj is None:
        raise Exception('Must not be None')
    return obj


##
# x.amalg.demo.demo


def _main() -> None:
    check_not_none(5)

    pprint.pprint('hi')


if __name__ == '__main__':
    _main()
