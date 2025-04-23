def cdiv(x: int, y: int) -> int:
    """https://python-history.blogspot.com/2010/08/why-pythons-integer-division-floors.html"""

    if y == 0:
        return 0
    u = abs(x) // abs(y)
    if (x < 0) ^ (y < 0):
        u *= -1
    return u


def cmod(x: int, y: int) -> int:
    return x - (cdiv(x, y) * y)
