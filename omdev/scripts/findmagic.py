import argparse
import os.path
import re
import typing as ta


def find_magic(
        roots: ta.Sequence[str],
        magics: ta.Sequence[str],
        exts: ta.Sequence[str],
        *,
        py: bool = False,
) -> ta.Iterator[str]:
    if not magics:
        raise Exception('Must specify magics')
    if not exts:
        raise Exception('Must specify extensions')

    pats = [
        re.compile('^' + re.escape(m) + r'($|(\s.*))')
        for m in magics
    ]

    for root in roots:
        for dp, dns, fns in os.walk(root):  # noqa
            for fn in fns:
                if not any(fn.endswith(f'.{x}') for x in exts):
                    continue

                fp = os.path.join(dp, fn)
                with open(fp) as f:
                    src = f.read()

                if not any(
                        any(pat.fullmatch(l) for pat in pats)
                        for l in src.splitlines()
                ):
                    continue

                if py:
                    if fn == '__init__.py':
                        out = dp.replace(os.sep, '.')
                    elif fn.endswith('.py'):
                        out = fp[:-3].replace(os.sep, '.')
                    else:
                        out = fp
                else:
                    out = fp
                yield out


def _main(argv=None) -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--ext', '-x', dest='exts', action='append')
    arg_parser.add_argument('--magic', '-m', dest='magics', action='append')
    arg_parser.add_argument('--py', action='store_true')
    arg_parser.add_argument('roots', nargs='*')
    args = arg_parser.parse_args(argv)

    for out in find_magic(
        roots=args.roots,
        magics=args.magics,
        exts=args.exts,
        py=args.py,
    ):
        print(out)


if __name__ == '__main__':
    _main()
