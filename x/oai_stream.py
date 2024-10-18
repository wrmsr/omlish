from openai import OpenAI

from omdev.secrets import load_secrets


def _main():
    client = OpenAI(api_key=load_secrets().get('openai_api_key').reveal())

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say this is a test"}],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")


if __name__ == '__main__':
    _main()
