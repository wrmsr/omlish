import contextlib
import contextvars
import sys


##


exit_stack: contextvars.ContextVar[contextlib.ExitStack] = contextvars.ContextVar('exit_stack')

data_dir: contextvars.ContextVar[str] = contextvars.ContextVar('data_dir')

use_gpu: bool = sys.platform == 'linux'
