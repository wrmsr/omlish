import os.path
import tempfile



def rewrite_file(in_file: str, tmp_dir: str) -> str:
    with open(in_file) as f:
        src = f.read()

    in_lines = src.splitlines(keepends=True)
    out_lines = []

    for l in in_lines:
        if l.strip().startswith('-r'):
            l = l.strip()
            lp, _, rp = l.partition(' ')
            if lp == '-r':
                inc_in_file, _, rest = rp.partition(' ')
            else:
                inc_in_file, rest = lp[2:], rp

            inc_out_file = rewrite_file(inc_in_file, tmp_dir)
            out_lines.append(' '.join(['-r', inc_out_file, rest]) + '\n')

        else:
            out_lines.append(l)

    out_file = os.path.join(tmp_dir, os.path.basename(in_file))
    if os.path.exists(out_file):
        raise Exception(f'file exists: {out_file}')

    with open(out_file, 'w') as f:
        f.write(''.join(out_lines))
    return out_file


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

    print()
    print('\n'.join(f'{r.requirement} ({r.comes_from})' for r in parsed_reqs))


if __name__ == '__main__':
    _main()
