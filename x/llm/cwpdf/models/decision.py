import contextlib
import logging
import os.path
import typing as ta

from omlish import lang

from ..vars import exit_stack
from ..vars import use_gpu


if ta.TYPE_CHECKING:
    import llama_cpp
else:
    llama_cpp = lang.proxy_import('llama_cpp')


log = logging.getLogger(__name__)


##


def decision_model() -> 'llama_cpp.Llama':
    log.info('Loading decision model')
    ret = exit_stack.get().enter_context(contextlib.closing(llama_cpp.Llama(
        model_path=os.path.expanduser('~/.cache/nexa/hub/DavidHandsome/Octopus-v2-PDF/gguf-q4_K_M/q4_K_M.gguf'),
        chat_format=None,
        n_ctx=2048,
        n_gpu_layers=-1 if use_gpu else 0,
        verbose=False,
    )))
    log.info('Decision model loaded')
    return ret
