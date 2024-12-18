# MIT License
#
# Copyright (c) 2024 Stanford Open Virtual Assistant Lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# https://github.com/stanford-oval/storm/commit/aca7b559a06c730866310a3a4757dc365c5c1a1a

import os.path

# jfc
os.environ['DSP_CACHEDIR'] = os.path.join(os.path.dirname(__file__), 'cache')
# os.environ.get('DSP_NOTEBOOK_CACHEDIR')

from .collaborative_storm import *
from .dataclass import *
from .encoder import *
from .interface import *
from .lm import *
from .rm import *
from .storm_wiki import *
from .utils import *


__version__ = '1.0.0'
