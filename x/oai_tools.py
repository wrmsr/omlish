"""
https://platform.openai.com/docs/guides/function-calling
"""
import typing as ta

import openai

from omdev.secrets import load_secrets
from ommlx.minichain.chat import ToolParam
from ommlx.minichain.chat import ToolSpec


def _opt_dct_fld(k, v):
    return {k: v} if v else {}


def render_tool_spec(td: ToolSpec) -> ta.Any:
    return {
        'type': 'function',
        'function': {

            'name': td.name,

            **_opt_dct_fld('description', td.desc),

            'parameters': {
                'type': 'object',
                'properties': {
                    tp.name: {
                        'type': tp.dtype,
                        **_opt_dct_fld('description', tp.desc),
                    }
                    for tp in td.params
                },

                'required': [tp.name for tp in td.params if tp.required],
                'additionalProperties': False,
            },
        }
    }


def _main() -> None:
    tool = ToolSpec(
        'get_delivery_date',
        [
            ToolParam('order_id', 'string', desc="The customer's order ID.", required=True),
        ],
        desc=(
            "Get the delivery date for a customer's order. Call this whenever you need to know the delivery date, for "
            "example when a customer asks 'Where is my package'"
        ),
    )

    tools = [render_tool_spec(tool)]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user.",
        },
        {"role": "user", "content": "Hi, can you tell me the delivery date for my order?"},
        {"role": "assistant", "content": "Hi there! I can help with that. Can you please provide your order ID?"},
        {"role": "user", "content": "i think it is order_12345"},
    ]

    client = openai.Client(api_key=load_secrets().get('openai_api_key').reveal())

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )

    print(response)


if __name__ == '__main__':
    _main()
