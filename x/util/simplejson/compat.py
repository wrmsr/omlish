"""Python 3 compatibility shims
"""
import sys
PY3 = True
from importlib import reload as reload_module
def b(s):
    return bytes(s, 'latin1')
from io import StringIO, BytesIO
text_type = str
binary_type = bytes
string_types = (str,)
integer_types = (int,)
unichr = chr

long_type = integer_types[-1]
