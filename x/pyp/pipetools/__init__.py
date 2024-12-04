from .utils import foreach


__version__ = VERSION = 1, 1, 0
__versionstr__ = foreach(str) | '.'.join < VERSION

from .main import X
from .main import maybe
from .main import pipe
from .main import xpartial
from .utils import *
