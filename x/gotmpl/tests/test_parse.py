import operator
import textwrap
import typing as ta

from omlish import lang
from ..parse import parse


BUILTINS: ta.Mapping[str, ta.Callable] = {
    "and": operator.and_,
    "call": lang.void,  # emptyCall,
    "html": lang.void,  # HTMLEscaper,
    "index": lang.void,  # index,
    "slice": slice,
    "js": lang.void,  # JSEscaper,
    "len": len,
    "not": operator.not_,
    "or": operator.or_,
    "print": lang.void,  # fmt.Sprint,
    "printf": lang.void,  # fmt.Sprintf,
    "println": lang.void,  # fmt.Sprintln,
    "urlquery": lang.void,  # URLQueryEscaper,

    # Comparisons
    "eq": operator.eq,  # ==
    "ge": operator.ge,  # >=
    "gt": operator.gt,  # >
    "le": operator.le,  # <=
    "lt": operator.lt,  # <
    "ne": operator.ne,  # !=
}


def test_parse():
    for s in [
        'hi',
        # '{{ hi }} there',
        textwrap.dedent("""
            {{- range .Messages }}GPT4 Correct
            {{- if eq .Role "system" }} System:
            {{- else if eq .Role "user" }} User:
            {{- else if eq .Role "assistant" }} Assistant:
            {{- end }} {{ .Content }}<|end_of_turn|>
            {{- end }}GPT4 Correct Assistant:
        """),
    ]:
        t = parse(
            '-',
            s,
            funcs=dict(BUILTINS),
        )['-']
        print(t)
