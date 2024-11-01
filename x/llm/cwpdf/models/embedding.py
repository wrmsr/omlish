import contextlib
import logging
import os.path
import typing as ta

from omlish import lang

from ..vars import exit_stack


if ta.TYPE_CHECKING:
    import llama_cpp
else:
    llama_cpp = lang.proxy_import('llama_cpp')


log = logging.getLogger(__name__)


##


@lang.cached_function
def embedding_model() -> 'llama_cpp.Llama':
    log.info('Loading embedding model')
    ret = exit_stack.get().enter_context(contextlib.closing(llama_cpp.Llama(
        model_path=os.path.expanduser('~/.cache/nexa/hub/official/nomic-embed-text-v1.5/fp16.gguf'),
        embedding=True,
        n_ctx=2048,
        verbose=False,
    )))
    log.info('Embedding model loaded')
    return ret


def embed(
        s: str,
        mode: ta.Literal['embed', 'query'],
        *,
        embed_instruction: str = 'passage: ',
        query_instruction: str = 'query: ',
        normalize: bool = False,
        truncate: bool = True,
) -> list[float]:
    inst = {
        'embed': embed_instruction,
        'query': query_instruction,
    }[mode]

    return embedding_model().embed(
        f'{inst}{s}',
        normalize,
        truncate,
    )
