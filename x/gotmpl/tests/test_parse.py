import operator
import textwrap
import typing as ta

import pytest

from omlish import lang

from ..parse import ParseError
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

        textwrap.dedent("""
            {{- range .Messages }}GPT4 Correct
            {{- if eq .Role "system" }} System:
            {{- else if eq .Role "user" }} User:
            {{- else if eq .Role "assistant" }} Assistant:
            {{- end }} {{ .Content }}<|end_of_turn|>
            {{- end }}GPT4 Correct Assistant:
        """),

        "",
        "{{/*\n\n\n*/}}",
        " \t\n",
        "some text",
        "{{}}",
        "{{.X}}",
        "{{printf}}",
        "{{$}}",
        "{{with $x := 3}}{{$x 23}}{{end}}",
        "{{$.I}}",
        "{{printf `%d` 23}}",
        "{{.X|.Y}}",
        "{{$x := .X|.Y}}",
        "{{.X (.Y .Z) (.A | .B .C) (.E)}}",
        "{{(.Y .Z).Field}}",
        "{{if .X}}hello{{end}}",
        "{{if .X}}true{{else}}false{{end}}",
        "{{if .X}}true{{else if .Y}}false{{end}}",
        "+{{if .X}}X{{else if .Y}}Y{{else if .Z}}Z{{end}}+",
        "{{range .X}}hello{{end}}",
        "{{range .X.Y.Z}}hello{{end}}",
        "{{range .X}}hello{{range .Y}}goodbye{{end}}{{end}}",
        "{{range .X}}true{{else}}false{{end}}",
        "{{range .X|.M}}true{{else}}false{{end}}",
        "{{range .SI}}{{.}}{{end}}",
        "{{range $x := .SI}}{{.}}{{end}}",
        "{{range $x, $y := .SI}}{{.}}{{end}}",
        "{{range .SI}}{{.}}{{break}}{{end}}",
        "{{range .SI}}{{.}}{{continue}}{{end}}",
        "{{range .SI 1 -3.2i true false 'a' nil}}{{end}}",
        "{{template `x`}}",
        "{{template `x` .Y}}",
        "{{with .X}}hello{{end}}",
        "{{with .X}}hello{{else}}goodbye{{end}}",
        "{{with .X}}hello{{else with .Y}}goodbye{{end}}",
        "{{with .X}}X{{else with .Y}}Y{{else with .Z}}Z{{end}}",
        # Trimming spaces.
        "x \r\n\t{{- 3}}",
        "{{3 -}}\n\n\ty",
        "x \r\n\t{{- 3 -}}\n\n\ty",
        "x\n{{-  3   -}}\ny",
        "x \r\n\t{{- /* hi */}}",
        "{{/* hi */ -}}\n\n\ty",
        "x \r\n\t{{- /* */ -}}\n\n\ty",
        '{{block "foo" .}}hello{{end}}',

        "{{ $x \n := \n 1 \n }}",
        "{{\n}}",
        "{{\n\"x\"\n|\nprintf\n}}",
        "{{/*\nhello\n*/}}",
        "{{-\n/*\nhello\n*/\n-}}",
        "{{range .SI}}{{.}}{{ continue }}{{end}}",
        "{{range .SI}}{{.}}{{ break }}{{end}}",
    ]:
        t = parse(
            '-',
            s,
            funcs=dict(BUILTINS),
        )['-']
        print(t)

    for s in [
        # Errors.
        "hello{{range",
        "{{end}}",
        "{{else}}",
        "{{if .X}}hello{{end}}{{else}}",
        "{{if .X}}1{{else}}2{{else}}3{{end}}",
        "hello{{range .x}}",
        "hello{{range .x}}{{else}}",
        "hello{{undefined}}",
        "{{$x}}",
        "{{with $x := 4}}{{end}}{{$x}}",
        "{{template $v}}",
        "{{with $x.Y := 4}}{{end}}",
        "{{template .X}}",
        "{{template $v}}",
        "{{printf 3, 4}}",
        "{{with $v, $u := 3}}{{end}}",
        "{{range $u, $v, $w := 3}}{{end}}",
        "{{printf (printf .).}}",
        "{{printf 3`x`}}",
        "{{printf `x`.}}",
        "{{if .X}}a{{else if .Y}}b{{end}}{{end}}",
        "{{range .}}{{end}} {{break}}",
        "{{range .}}{{end}} {{continue}}",
        "{{range .}}{{else}}{{break}}{{end}}",
        "{{range .}}{{else}}{{continue}}{{end}}",
        # Other kinds of assignments and operators aren't available yet.
        "{{$x := 0}}{{$x}}",
        "{{$x += 1}}{{$x}}",
        "{{$x ! 2}}{{$x}}",
        "{{$x % 3}}{{$x}}",
        # Check the parse fails for := rather than comma.
        "{{range $x := $y := 3}}{{end}}",
        # Another bug: variable read must ignore following punctuation.
        "{{$x:=.}}{{$x!2}}",
        "{{$x:=.}}{{$x+2}}",
        "{{$x:=.}}{{$x +2}}",
        # Check the range handles assignment vs. declaration properly.
        "{{range $x := 0}}{{$x}}{{end}}",
        "{{range $x = 0}}{{$x}}{{end}}",
        # dot following a literal value
        "{{1.E}}",
        "{{0.1.E}}",
        "{{true.E}}",
        "{{'a'.any}}",
        '{{"hello".guys}}',
        "{{..E}}",
        "{{nil.E}}",
        # Wrong pipeline
        "{{12|.}}",
        "{{.|12|printf}}",
        "{{.|printf|\"error\"}}",
        "{{12|printf|'e'}}",
        "{{.|true}}",
        "{{'c'|nil}}",
        '{{printf "%d" ( ) }}',
        # Missing pipeline in block
        '{{block "foo"}}hello{{end}}',
    ]:
        with pytest.raises(ParseError):  # noqa
            parse(
                '-',
                s,
                funcs=dict(BUILTINS),
            )
