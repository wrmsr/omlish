"""
https://ollama.com/library
https://github.com/ollama/ollama/blob/main/docs/api.md

==

curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Why is the sky blue?"
}'
"""
import ollama


def _main() -> None:
    response = ollama.chat(
        model='llama3.2:3b',
        messages=[
        {
            'role': 'user',
            'content': 'Why is the sky blue?',
        },
    ])
    print(response['message']['content'])


if __name__ == '__main__':
    _main()
