# !/usr/bin/env python3
"""
https://github.com/umlet/pwk/blob/dc23b3400108a71947a695f1fa1df0f514b42528/pwk
"""
import io
import tokenize


def translate_brace_python(
        s: str,
        *,
        indent_width: int = 4,
) -> str:
    lt = tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline)

    ret = io.StringIO()

    indent = 0
    open_braces = 0

    newline = False
    indent_up = False
    indent_down = False
    skip = False

    while True:
        try:
            t = next(lt)

            if t.type == tokenize.ENCODING:
                last_t = t
                continue

            if t.type == tokenize.OP and t.string == ';':
                newline = True

            elif t.type == tokenize.OP and t.string == ':':
                if open_braces == 0:
                    newline = True
                    indent_up = True

            elif t.type == tokenize.OP and t.string == '{':
                if last_t.type == tokenize.OP and last_t.string == ':':  # noqa
                    skip = True
                else:
                    open_braces += 1

            elif t.type == tokenize.OP and t.string == '}':
                if open_braces > 0:
                    open_braces -= 1
                elif open_braces == 0:
                    if indent > 0:
                        newline = True
                        indent_down = True
                        skip = True
                    else:
                        raise Exception('Too many closing braces')

            if indent_up:
                indent += indent_width
            elif indent_down:
                indent -= indent_width

            if newline and indent_up:
                ret.write(':\n' + ' ' * indent)
            elif newline:
                ret.write('\n' + ' ' * indent)
            else:
                if not skip:
                    ret.write(t.string)
                    ret.write(' ')

            newline = False
            indent_up = False
            indent_down = False
            skip = False
            last_t = t

        except StopIteration:
            break
        except tokenize.TokenError:
            continue

    ret.write('\n')
    return ret.getvalue()


def _main() -> None:
    print()
    for s in [
        'def f(x): { x += 2; return x }',
        'class Foo: { def __init__(x): { self._x = x } def f(self, x): { return self._x + x } }',
    ]:
        print(s)
        print(translate_brace_python(s))
        print()


if __name__ == '__main__':
    _main()
