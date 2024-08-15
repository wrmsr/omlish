"""A demonstration of Bluelet's approach to invoking (delegating to) sub-coroutines and spawning child coroutines."""
from .. import bluelet as bl


def child():
    print('Child started.')
    yield bl.null()
    print('Child resumed.')
    yield bl.null()
    print('Child ending.')
    yield bl.end(42)


def parent():
    print('Parent started.')
    yield bl.null()
    print('Parent resumed.')
    result = yield child()
    print('Child returned:', repr(result))
    print('Parent ending.')


def exc_child():
    yield bl.null()
    raise Exception()


def exc_parent():
    try:
        yield exc_child()
    except Exception as exc:
        print('Parent caught:', repr(exc))


def exc_grandparent():
    yield bl.spawn(exc_parent())


if __name__ == '__main__':
    bl.run(parent())
    bl.run(exc_grandparent())
