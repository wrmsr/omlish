from .. import bluelet as bl


def sleeper(duration: float) -> bl.Coro:
    print('Going to sleep for %i seconds...' % duration)
    yield bl.sleep(duration)
    print('...woke up after %i seconds.' % duration)


def sleepy() -> bl.Coro:
    for i in (0, 1, 3, 5):
        yield bl.spawn(sleeper(i))


if __name__ == '__main__':
    bl.run(sleepy())
