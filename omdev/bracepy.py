#!/usr/bin/env python3
# @omlish-lite
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
            elif not skip:
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


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'bracepy',
    'mod_name': __name__,
}}


if __name__ == '__main__':
    def _main(argv=None) -> None:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('-x', '--exec', action='store_true')
        parser.add_argument('cmd')

        args = parser.parse_args(argv)

        src = translate_brace_python(args.cmd)

        if args.exec:
            exec(src)
        else:
            print(src)

    _main()
