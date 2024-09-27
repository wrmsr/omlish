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
    # for s in [
    #     'hi',
    #
    #     textwrap.dedent("""
    #         {{- range .Messages }}GPT4 Correct
    #         {{- if eq .Role "system" }} System:
    #         {{- else if eq .Role "user" }} User:
    #         {{- else if eq .Role "assistant" }} Assistant:
    #         {{- end }} {{ .Content }}<|end_of_turn|>
    #         {{- end }}GPT4 Correct Assistant:
    #     """),
    # ]:
    #     t = parse(
    #         '-',
    #         s,
    #         funcs=dict(BUILTINS),
    #     )['-']
    #     print(t)

    for name, ins, has_err, result in [
        # ("empty", "", False, ''),
        # ("comment", "{{/*\n\n\n*/}}", False, ''),
        # ("spaces", " \t\n", False, " \t\n"),
        # ("text", "some text", False, "some text"),
        # ("emptyAction", "{{}}", True, '{{}}'),
        ("field", "{{.X}}", False, '{{.X}}'),
        ("simple command", "{{printf}}", False, '{{printf}}'),
        ("$ invocation", "{{$}}", False, "{{$}}"),
        ("variable invocation", "{{with $x := 3}}{{$x 23}}{{end}}", False, "{{with $x := 3}}{{$x 23}}{{end}}"),
        ("variable with fields", "{{$.I}}", False, "{{$.I}}"),
        ("multi-word command", "{{printf `%d` 23}}", False, "{{printf `%d` 23}}"),
        ("pipeline", "{{.X|.Y}}", False, '{{.X | .Y}}'),
        ("pipeline with decl", "{{$x := .X|.Y}}", False, '{{$x := .X | .Y}}'),
        ("nested pipeline", "{{.X (.Y .Z) (.A | .B .C) (.E)}}", False, '{{.X (.Y .Z) (.A | .B .C) (.E)}}'),
        ("field applied to parentheses", "{{(.Y .Z).Field}}", False, '{{(.Y .Z).Field}}'),
        ("simple if", "{{if .X}}hello{{end}}", False, '{{if .X}}"hello"{{end}}'),
        ("if with else", "{{if .X}}true{{else}}false{{end}}", False, '{{if .X}}"true"{{else}}"false"{{end}}'),
        ("if with else if", "{{if .X}}true{{else if .Y}}false{{end}}", False, '{{if .X}}"true"{{else}}{{if .Y}}"false"{{end}}{{end}}'),
        ("if else chain", "+{{if .X}}X{{else if .Y}}Y{{else if .Z}}Z{{end}}+", False, '"+"{{if .X}}"X"{{else}}{{if .Y}}"Y"{{else}}{{if .Z}}"Z"{{end}}{{end}}{{end}}"+"'),
        ("simple range", "{{range .X}}hello{{end}}", False, '{{range .X}}"hello"{{end}}'),
        ("chained field range", "{{range .X.Y.Z}}hello{{end}}", False, '{{range .X.Y.Z}}"hello"{{end}}'),
        ("nested range", "{{range .X}}hello{{range .Y}}goodbye{{end}}{{end}}", False, '{{range .X}}"hello"{{range .Y}}"goodbye"{{end}}{{end}}'),
        ("range with else", "{{range .X}}true{{else}}false{{end}}", False, '{{range .X}}"true"{{else}}"false"{{end}}'),
        ("range over pipeline", "{{range .X|.M}}true{{else}}false{{end}}", False, '{{range .X | .M}}"true"{{else}}"false"{{end}}'),
        ("range []int", "{{range .SI}}{{.}}{{end}}", False, '{{range .SI}}{{.}}{{end}}'),
        ("range 1 var", "{{range $x := .SI}}{{.}}{{end}}", False, '{{range $x := .SI}}{{.}}{{end}}'),
        ("range 2 vars", "{{range $x, $y := .SI}}{{.}}{{end}}", False, '{{range $x, $y := .SI}}{{.}}{{end}}'),
        ("range with break", "{{range .SI}}{{.}}{{break}}{{end}}", False, '{{range .SI}}{{.}}{{break}}{{end}}'),
        ("range with continue", "{{range .SI}}{{.}}{{continue}}{{end}}", False, '{{range .SI}}{{.}}{{continue}}{{end}}'),
        ("constants", "{{range .SI 1 -3.2i true false 'a' nil}}{{end}}", False, "{{range .SI 1 -3.2i true false 'a' nil}}{{end}}"),
        ("template", "{{template `x`}}", False, '{{template "x"}}'),
        ("template with arg", "{{template `x` .Y}}", False, '{{template "x" .Y}}'),
        ("with", "{{with .X}}hello{{end}}", False, '{{with .X}}"hello"{{end}}'),
        ("with with else", "{{with .X}}hello{{else}}goodbye{{end}}", False, '{{with .X}}"hello"{{else}}"goodbye"{{end}}'),
        ("with with else with", "{{with .X}}hello{{else with .Y}}goodbye{{end}}", False, '{{with .X}}"hello"{{else}}{{with .Y}}"goodbye"{{end}}{{end}}'),
        ("with else chain", "{{with .X}}X{{else with .Y}}Y{{else with .Z}}Z{{end}}", False, '{{with .X}}"X"{{else}}{{with .Y}}"Y"{{else}}{{with .Z}}"Z"{{end}}{{end}}{{end}}'),
        # Trimming spaces.
        ("trim left", "x \r\n\t{{- 3}}", False, '"x"{{3}}'),
        ("trim right", "{{3 -}}\n\n\ty", False, '{{3}}"y"'),
        ("trim left and right", "x \r\n\t{{- 3 -}}\n\n\ty", False, '"x"{{3}}"y"'),
        ("trim with extra spaces", "x\n{{-  3   -}}\ny", False, '"x"{{3}}"y"'),
        ("comment trim left", "x \r\n\t{{- /* hi */}}", False, '"x"'),
        ("comment trim right", "{{/* hi */ -}}\n\n\ty", False, '"y"'),
        ("comment trim left and right", "x \r\n\t{{- /* */ -}}\n\n\ty", False, '"x""y"'),
        ("block definition", '{{block "foo" .}}hello{{end}}', False, '{{template "foo" .}}'),

        ("newline in assignment", "{{ $x \n := \n 1 \n }}", False, "{{$x := 1}}"),
        ("newline in empty action", "{{\n}}", True, "{{\n}}"),
        ("newline in pipeline", "{{\n\"x\"\n|\nprintf\n}}", False, '{{"x" | printf}}'),
        ("newline in comment", "{{/*\nhello\n*/}}", False, ""),
        ("newline in comment", "{{-\n/*\nhello\n*/\n-}}", False, ""),
        ("spaces around continue", "{{range .SI}}{{.}}{{ continue }}{{end}}", False, '{{range .SI}}{{.}}{{continue}}{{end}}'),
        ("spaces around break", "{{range .SI}}{{.}}{{ break }}{{end}}", False, '{{range .SI}}{{.}}{{break}}{{end}}'),

        # Errors.
        ("unclosed action", "hello{{range", True, ""),
        ("unmatched end", "{{end}}", True, ""),
        ("unmatched else", "{{else}}", True, ""),
        ("unmatched else after if", "{{if .X}}hello{{end}}{{else}}", True, ""),
        ("multiple else", "{{if .X}}1{{else}}2{{else}}3{{end}}", True, ""),
        ("missing end", "hello{{range .x}}", True, ""),
        ("missing end after else", "hello{{range .x}}{{else}}", True, ""),
        ("undefined function", "hello{{undefined}}", True, ""),
        ("undefined variable", "{{$x}}", True, ""),
        ("variable undefined after end", "{{with $x := 4}}{{end}}{{$x}}", True, ""),
        ("variable undefined in template", "{{template $v}}", True, ""),
        ("declare with field", "{{with $x.Y := 4}}{{end}}", True, ""),
        ("template with field ref", "{{template .X}}", True, ""),
        ("template with var", "{{template $v}}", True, ""),
        ("invalid punctuation", "{{printf 3, 4}}", True, ""),
        ("multidecl outside range", "{{with $v, $u := 3}}{{end}}", True, ""),
        ("too many decls in range", "{{range $u, $v, $w := 3}}{{end}}", True, ""),
        ("dot applied to parentheses", "{{printf (printf .).}}", True, ""),
        ("adjacent args", "{{printf 3`x`}}", True, ""),
        ("adjacent args with .", "{{printf `x`.}}", True, ""),
        ("extra end after if", "{{if .X}}a{{else if .Y}}b{{end}}{{end}}", True, ""),
        ("break outside range", "{{range .}}{{end}} {{break}}", True, ""),
        ("continue outside range", "{{range .}}{{end}} {{continue}}", True, ""),
        ("break in range else", "{{range .}}{{else}}{{break}}{{end}}", True, ""),
        ("continue in range else", "{{range .}}{{else}}{{continue}}{{end}}", True, ""),
        # Other kinds of assignments and operators aren't available yet.
        ("bug0a", "{{$x := 0}}{{$x}}", False, "{{$x := 0}}{{$x}}"),
        ("bug0b", "{{$x += 1}}{{$x}}", True, ""),
        ("bug0c", "{{$x ! 2}}{{$x}}", True, ""),
        ("bug0d", "{{$x % 3}}{{$x}}", True, ""),
        # Check the parse fails for := rather than comma.
        ("bug0e", "{{range $x := $y := 3}}{{end}}", True, ""),
        # Another bug: variable read must ignore following punctuation.
        ("bug1a", "{{$x:=.}}{{$x!2}}", True, ""),                       # ! is just illegal here.
        ("bug1b", "{{$x:=.}}{{$x+2}}", True, ""),                       # $x+2 should not parse as ($x) (+2).
        ("bug1c", "{{$x:=.}}{{$x +2}}", False, "{{$x := .}}{{$x +2}}"), # It's OK with a space.
        # Check the range handles assignment vs. declaration properly.
        ("bug2a", "{{range $x := 0}}{{$x}}{{end}}", False, "{{range $x := 0}}{{$x}}{{end}}"),
        ("bug2b", "{{range $x = 0}}{{$x}}{{end}}", False, "{{range $x = 0}}{{$x}}{{end}}"),
        # dot following a literal value
        ("dot after integer", "{{1.E}}", True, ""),
        ("dot after float", "{{0.1.E}}", True, ""),
        ("dot after boolean", "{{true.E}}", True, ""),
        ("dot after char", "{{'a'.any}}", True, ""),
        ("dot after string", '{{"hello".guys}}', True, ""),
        ("dot after dot", "{{..E}}", True, ""),
        ("dot after nil", "{{nil.E}}", True, ""),
        # Wrong pipeline
        ("wrong pipeline dot", "{{12|.}}", True, ""),
        ("wrong pipeline number", "{{.|12|printf}}", True, ""),
        ("wrong pipeline string", "{{.|printf|\"error\"}}", True, ""),
        ("wrong pipeline char", "{{12|printf|'e'}}", True, ""),
        ("wrong pipeline boolean", "{{.|true}}", True, ""),
        ("wrong pipeline nil", "{{'c'|nil}}", True, ""),
        ("empty pipeline", '{{printf "%d" ( ) }}', True, ""),
        # Missing pipeline in block
        ("block definition", '{{block "foo"}}hello{{end}}', True, ""),
    ]:
        if not has_err:
            t = parse(
                '-',
                ins,
                funcs=dict(BUILTINS),
            )['-']
            r = t._root.string()
            assert r == result

        else:
            with pytest.raises(ParseError):  # noqa
                parse(
                    '-',
                    ins,
                    funcs=dict(BUILTINS),
                )
