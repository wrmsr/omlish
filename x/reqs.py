import os.path
import tempfile



def rewrite_file(in_file: str, tmp_dir: str) -> str:
    out_file = os.path.join(tmp_dir, os.path.basename(in_file))
    if os.path.exists(out_file):
        raise Exception(f'file exists: {out_file}')

    with open(in_file) as f:
        src = f.read()

    in_lines = src.splitlines(keepends=True)
    out_lines = []

    for l in in_lines:
        if l.strip().startswith('-r'):
            l = l.strip()
            lp, _, rp = l.partition(' ')
            if lp == '-r':
                inc_file, _, rest = rp.partition(' ')
            else:
                inc_file, rest = lp[2:], rp
            # raise NotImplementedError
            print((inc_file, rest))
        else:
            out_lines.append(l)

    raise NotImplementedError


def _main() -> None:
    in_file = 'requirements-dev.txt'
    tmp_dir = tempfile.mkdtemp('-omlish-reqs')
    out_file = rewrite_file(in_file, tmp_dir)

    from pip._internal.network.session import PipSession  # noqa
    from pip._internal.req import parse_requirements  # noqa

    parsed_reqs = list(parse_requirements(
            out_file,
            finder=None,
            options=None,
            session=PipSession()
    ))

    print(parsed_reqs)


if __name__ == '__main__':
    _main()
