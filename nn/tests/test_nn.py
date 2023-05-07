import math


class Shape(tuple):
    @property
    def dim(self) -> int:
        return math.prod(self)


class Strides(tuple):
    def offset(self):
def test_nn():
    sh = Shape((1, 2, 3))
    print(sh)
    print(sh.dim)
