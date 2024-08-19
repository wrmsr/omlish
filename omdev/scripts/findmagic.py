import argparse
import os.path


def _main(argv=None) -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--ext', '-x', dest='exts', action='append')
    arg_parser.add_argument('magic')
    arg_parser.add_argument('roots', nargs='*')
    args = arg_parser.parse_args(argv)
    print(args)

    if not args.exts:
        raise Exception('Must specify extensions')

    for root in args.roots:
        for dp, dns, fns in os.walk(root):
            for fn in fns:
                if not any(fn.endswith(f'.{x}') for x in args.exts):
                    continue
                print(os.path.join(dp, fn))


if __name__ == '__main__':
    _main()
