import os

os.environ['DEBUG'] = '5'

import tinygrad as tg


def _main():
    t = tg.Tensor.randn(3, 3).realize()
    u = tg.Tensor.randn(6, 3).realize()
    v = (t.repeat((2, 1)) + u).sum()
    print(v.numpy())


if __name__ == '__main__':
    _main()
