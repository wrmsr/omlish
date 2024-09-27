import textwrap
from ..parse import parse


def test_parse():
    for s in [
        'hi',
        '{{ hi }} there',
        textwrap.dedent("""
            {{- range .Messages }}GPT4 Correct
            {{- if eq .Role "system" }} System:
            {{- else if eq .Role "user" }} User:
            {{- else if eq .Role "assistant" }} Assistant:
            {{- end }} {{ .Content }}<|end_of_turn|>
            {{- end }}GPT4 Correct Assistant:
        """),
    ]:
        t = parse('-', s)['-']
        print(t)
