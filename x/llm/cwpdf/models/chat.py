import contextlib
import logging
import os.path
import typing as ta

from omlish import check
from omlish import lang

from ..docs import Doc
from ..vars import exit_stack
from ..vars import use_gpu


if ta.TYPE_CHECKING:
    import llama_cpp
else:
    llama_cpp = lang.proxy_import('llama_cpp')


log = logging.getLogger(__name__)


##


def chat_model() -> 'llama_cpp.Llama':
    log.info('Loading chat model')
    ret = exit_stack.get().enter_context(contextlib.closing(llama_cpp.Llama(
        model_path=os.path.expanduser('~/.cache/nexa/hub/official/Llama3.2-3B-Instruct/q4_0.gguf'),
        chat_format='llama-3',
        n_ctx=2048,
        n_gpu_layers=-1 if use_gpu else 0,
        verbose=False,
    )))
    log.info('Chat model loaded')
    return ret


def generate_question_answer(
        query: str,
        relevant_docs: ta.Iterable[Doc],
) -> ta.Iterator[str]:
    context = '\n\n'.join(d.content for d in relevant_docs)

    system_prompt = (
        'You are a QA assistant. Based on the following context, answer the question using bullet points and include '
        'necessary data.'
        '\n\n'
        'Context:'
        '\n'
        f'{context}'
    )

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': query},
    ]

    response_stream = chat_model().create_chat_completion(
        messages,  # type: ignore
        stop=['<nexa_end>'],
        max_tokens=2048,
        temperature=0.7,
        top_k=50,
        top_p=1.0,
        stream=True,
    )

    response_chunks = (
        check.isinstance(p['choices'][0]['delta'].get('content', ''), str)  # type: ignore
        for p in response_stream
    )

    return iter(response_chunks)
