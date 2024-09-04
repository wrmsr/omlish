from .icecream import ic


def _main():
    def foo(i):
        return i + 333

    ic(foo(123))

    #

    d = {'key': {1: 'one'}}
    ic(d['key'][1])

    class klass():
        attr = 'yep'

    ic(klass.attr)

    #

    def first():
        pass

    def second():
        pass

    def third():
        pass

    def foo(x):
        ic()
        first()

        if x > 2:
            ic()
            second()
        else:
            ic()
            third()

    foo(1)
    foo(2)


if __name__ == '__main__':
    _main()
