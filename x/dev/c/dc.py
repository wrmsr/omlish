import pickle


def _main():
    from ._dc import point  # noqa
    p = point(1, 2)
    print(p)
    print(p.x)
    p2 = pickle.loads(pickle.dumps(p))
    assert isinstance(p2, point)
    assert (p2.x, p2.y) == (p.x, p.y)


if __name__ == '__main__':
    _main()
