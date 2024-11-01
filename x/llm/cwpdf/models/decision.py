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


##


UserIntent: ta.TypeAlias = ta.Literal[
    'query_with_pdf',
    'generate_slide_column_chart',
    'generate_slide_pie_chart',
]


_USER_INTENT_MAP: ta.Mapping[str, UserIntent] = {
    '<nexa_0>':  'query_with_pdf',
    '<nexa_2>':  'generate_slide_column_chart',
    '<nexa_4>':  'generate_slide_pie_chart',
}


def classify_user_intent(query: str) -> UserIntent | None:
    prompt_template = (
        'Below is the query from the users, please call the correct function and generate the parameters to call the '
        'function.'
        '\n\n'
        'Query: {query}'
        '\n\n'
        'Response:'
    )

    prompt = prompt_template.format(query=query)

    output = decision_model().create_completion(
        prompt,
        stop=['<nexa_end>'],
    )

    raw_intent = output['choices'][0]['text'].strip()  # noqa

    return _USER_INTENT_MAP.get(raw_intent)
