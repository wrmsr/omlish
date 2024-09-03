"""
foo includes
"""
# Hi!
import os.path


def foo() -> str:
    return os.getcwd()


if __name__ == '__main__':
    def _main() -> None:
        print('hi')

    _main()
