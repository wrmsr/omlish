import contextlib
import contextvars


##


exit_stack: contextvars.ContextVar[contextlib.ExitStack] = contextvars.ContextVar('exit_stack')

data_dir: contextvars.ContextVar[str] = contextvars.ContextVar('data_dir')
