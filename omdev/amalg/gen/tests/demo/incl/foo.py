# @omlish-lite
"""
foo includes
"""
# Hi!
import os.path

from omlish.lite.resources import read_package_resource_binary


FAVICON_ICO = read_package_resource_binary(__package__, 'favicon.ico')


def foo() -> str:
    return os.getcwd()


if __name__ == '__main__':
    def _foo_main() -> None:
        print('hi')

    _foo_main()
