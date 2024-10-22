"""Python 3 compatibility shims"""


def b(s):
    return bytes(s, 'latin1')
