import argparse
import os.path
import re


def _main(argv=None) -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--ext', '-x', dest='exts', action='append')
    arg_parser.add_argument('--magic', '-m', dest='magics', action='append')
    arg_parser.add_argument('roots', nargs='*')
    args = arg_parser.parse_args(argv)

    if not args.magics:
        raise Exception('Must specify magics')
    if not args.exts:
        raise Exception('Must specify extensions')

    pats = [
        re.compile('^' + re.escape(m) + r'($|(\s.*))')
        for m in args.magics
    ]

    for root in args.roots:
        for dp, dns, fns in os.walk(root):  # noqa
            for fn in fns:
                if not any(fn.endswith(f'.{x}') for x in args.exts):
                    continue
                fp = os.path.join(dp, fn)
                with open(fp) as f:
                    src = f.read()
                if not any(
                    any(pat.fullmatch(l) for pat in pats)
                    for l in src.splitlines()
                ):
                    continue
                if fn == '__init__.py':
                    print(dp)
                else:
                    print(fp)


if __name__ == '__main__':
    _main()
