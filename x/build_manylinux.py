import argparse
import os
import shlex
import subprocess
import sys


##


DEFAULT_PY_TAGS = [
    'cp313-cp313',
    'cp313-cp313t',
    'cp314-cp314',
    'cp314-cp314t',
]


def compute_platform(arch: str) -> str:
    # Docker wants "linux/amd64" for x86_64
    if arch == 'x86_64':
        return 'linux/amd64'
    return f'linux/{arch}'


def build_image_name(arch: str, manylinux: str, registry: str) -> str:
    # e.g. quay.io/pypa/manylinux_2_34_x86_64
    return f'{registry}/manylinux_{manylinux}_{arch}'


def run(cmd: list[str], *, check: bool = True) -> int:
    print('+', ' '.join(shlex.quote(c) for c in cmd))
    return subprocess.run(cmd, check=check).returncode


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description='Build manylinux wheels inside Docker (C++ friendly).',
    )
    parser.add_argument(
        '--arch',
        choices=['x86_64', 'aarch64'],
        default='x86_64',
        help='Target manylinux image arch (default: %(default)s)',
    )
    parser.add_argument(
        '--manylinux',
        default='2_34',
        help='manylinux tag to use (e.g., 2_34, 2_28). Default: %(default)s',
    )
    parser.add_argument(
        '--registry',
        default='quay.io/pypa',
        help='Image registry/repo prefix. Default: %(default)s',
    )
    parser.add_argument(
        '--py-tags',
        default=','.join(DEFAULT_PY_TAGS),
        help="Comma-separated /opt/python tags to build, e.g.: 'cp313-cp313,cp313-cp313t,cp314-cp314,cp314-cp314t'",
    )
    parser.add_argument(
        '--cflags',
        default='-O3',
        help='CFLAGS for compilation. Default: %(default)s',
    )
    parser.add_argument(
        '--cxxflags',
        default='-O3',
        help='CXXFLAGS for compilation. Default: %(default)s',
    )
    parser.add_argument(
        '--workdir',
        default=os.getcwd(),
        help='Project root to mount at /io inside the container. Default: CWD',
    )
    parser.add_argument(
        '--no-auditwheel',
        action='store_true',
        help="Skip 'auditwheel repair' step.",
    )
    parser.add_argument(
        '--platform',
        default=None,
        help='Override --platform passed to docker (e.g., linux/amd64). Default: derived from arch',
    )
    parser.add_argument(
        '--image',
        default=None,
        help='Fully qualified image to use (overrides registry/manylinux/arch).',
    )
    parser.add_argument(
        '--pull',
        action='store_true',
        help='docker pull the image before running.',
    )
    args = parser.parse_args(argv)

    arch = args.arch
    platform = args.platform or compute_platform(arch)
    image = args.image or build_image_name(arch, args.manylinux, args.registry)

    # Normalize py-tags
    py_tags = [t.strip() for t in args.py_tags.split(',') if t.strip()]
    if not py_tags:
        print('No --py-tags specified after parsing.', file=sys.stderr)
        return 2

    # Build the inner bash script that runs inside the container.
    # Use a simple space-separated list rather than an array for convenience.
    tags_str = ' '.join(py_tags)

    inner_lines = [
        'set -e',
        f'manylinux-interpreters ensure {tags_str}',
        'rm -rf dist',
        f'for tag in {tags_str}; do',
        '  PYBIN="/opt/python/$tag/bin/python"',
        '  if [ -x "$PYBIN" ]; then',
        '    echo "==> Building for $tag"',
        '    "$PYBIN" -m pip -q install --root-user-action=ignore --upgrade build',
        '    "$PYBIN" -m build --wheel',
        '  else',
        '    echo "(skip $tag; not present in image)"',
        '  fi',
        'done',
    ]
    if not args.no_auditwheel:
        inner_lines.append('auditwheel repair -w dist dist/*.whl')

    inner_script = '\n'.join(inner_lines)

    # Optionally pull the image
    if args.pull:
        run(['docker', 'pull', image])

    # Compose docker run command
    cmd = [
        'docker',
        'run',
        '--rm',
        '--platform', platform,
        '-v', f'{os.path.abspath(args.workdir)}:/io',
        '-w', '/io',
        '-e', f'CFLAGS={args.cflags}',
        '-e', f'CXXFLAGS={args.cxxflags}',
        image,
        'bash', '-lc', inner_script,
    ]

    return run(cmd)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
