"""
https://platform.openai.com/docs/guides/function-calling
"""
import openai

from omdev.secrets import load_secrets


def _main() -> None:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_delivery_date",
                "description": (
                    "Get the delivery date for a customer's order. Call this whenever you need to know the delivery "
                    "date, for example when a customer asks 'Where is my package'"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The customer's order ID.",
                        },
                    },
                    "required": ["order_id"],
                    "additionalProperties": False,
                },
            }
        }
    ]

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
