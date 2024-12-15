"""
https://github.com/sametmax/Bat-belt/blob/372117e3876328f84804a296ee9636dee1e82206/batbelt/hack.py#L196
"""
import contextlib


class MultiStopIteration(StopIteration):
    def throw(self):
        raise self


@contextlib.contextmanager
def multibreak():
    try:
        yield MultiStopIteration().throw
    except MultiStopIteration:
        pass


if __name__ == '__main__':
    with multibreak() as stop:
        for x in range(1, 4):
            for z in range(1, 4):
                for w in range(1, 4):
                    print(w)
                    if x * z * w == 2 * 2 * 2:
                        print('stop')
                        stop()
