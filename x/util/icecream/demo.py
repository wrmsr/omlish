from .icecream import ic


def _main():
    def foo(i):
        return i + 333

    ic(foo(123))


if __name__ == '__main__':
    _main()
