"""
https://github.com/wrmsr/Chat-with-PDF-locally/blob/f34be6b0b5537d57c306946277d7a88daf8af097/prompts.py
"""
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


COLUMN_CHART_TEMPLATE = (
    '<s>[INST] <<SYS>>\n'
    'You are a helpful assistant that generates a specific JSON response based on the given query. Your task is to '
    'analyze the query and create a JSON object with two main keys: "text" and "chart_data".\n'
    '\n'
    'The "text" key should contain:\n'
    '1. "title_text": A brief, relevant title for the information.\n'
    '2. "main_text": A short summary or key takeaway from the data.\n'
    '\n'
    'The "chart_data" key should contain:\n'
    '1. "type": Always set to "chart".\n'
    '2. "chart_type": Always set to "COLUMN_CLUSTERED".\n'
    '3. "chart_data": An object with "categories" (array of labels) and "series" (array of objects with "name" and'
    ' "values").\n'
    '4. "title_text": A title for the chart.\n'
    '5. "description_text": A brief description of what the chart shows.\n'
    '\n'
    'Analyze the following query and generate the appropriate JSON response:\n'
    '{query}\n'
    '<<USR>>'
)


PIE_CHART_TEMPLATE = (
    '<s>[INST] <<SYS>>\n'
    'You are a helpful assistant that generates a specific JSON response based on the given query. Your task is to '
    'analyze the query and create a JSON object with two main keys: "text" and "chart_data".\n'
    '\n'
    'The "text" key should contain:\n'
    '1. "title_text": A brief, relevant title for the information.\n'
    '2. "main_text": A short summary or key takeaway from the data.\n'
    '\n'
    'The "chart_data" key should contain:"\n'
    '1. "type": Always set to "chart".\n'
    '2. "chart_type": Always set to "PIE".\n'
    '3. "chart_data": An object with "categories" (array of labels) and "values" (array of numeric values'
    ' corresponding to each category). The values should be decimal representations of percentages and must add up to 1'
    ' (representing 100%).\n'
    '4. "title_text": A title for the chart.\n'
    '5. "description_text": A brief description of what the chart shows.\n'
    '\n'
    'Analyze the following query and generate the appropriate JSON response:\n'
    '{query}\n'
    '<<USR>>'
)


@lang.cached_function
def pie_chart_model() -> 'llama_cpp.Llama':
    log.info('Loading pie chart model')
    ret = exit_stack.get().enter_context(contextlib.closing(llama_cpp.Llama(
        model_path=os.path.expanduser('~/.cache/nexa/hub/official/gemma-2-2b-instruct/fp16.gguf'),
        lora_path=os.path.expanduser('~/.cache/nexa/hub/DavidHandsome/Pie-Chart-LoRA/gguf-fp16/fp16.gguf'),
        chat_format='gemma',
        n_ctx=2048,
        n_gpu_layers=-1 if use_gpu else 0,
        verbose=False,
    )))
    log.info('Pie chart model loaded')
    return ret


def generate_pie_chart_code(query: str) -> str:
    prompt = PIE_CHART_TEMPLATE.format(query=query)

    output = pie_chart_model().create_completion(
        prompt,
        stop=['<end>'],
        logprobs=None,
        max_tokens=2048,
        temperature=0.7,
        top_k=50,
        top_p=1.0,
    )

    raw_code = output['choices'][0]['text'].strip()  # type: ignore

    return raw_code
