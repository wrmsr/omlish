from . import lang

_math = lang.proxy_import('._ext.cy.math', package=__package__)


def fmaf(x: float, y: float, z: float) -> float:
    return _math.fmaf_(x, y, z)


def fma(x: float, y: float, z: float) -> float:
    return _math.fma_(x, y, z)


def fmal(x: float, y: float, z: float) -> float:
    return _math.fmal_(x, y, z)
