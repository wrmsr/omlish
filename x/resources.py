import functools
import importlib.resources
import os
import typing as ta




def _main() -> None:
    rsrs = get_relative_resources('', globals=globals())
    print(rsrs)
    assert 'get_relative_resources' in rsrs['resources.py'].read_bytes().decode()


if __name__ == '__main__':
    _main()
