# @omlish-llm-author "gpt-5.4-thinking"
import argparse
import sys
import typing as ta

from .parsing import parse_patch
from .types import ExtendedHeaderKind
from .types import FilePatch
from .types import PatchSet


##


DESCRIPTION = """\
Unified diff metadata.

Examples:
    $ git diff | unidiff
    $ hg diff | unidiff --show-diff
    $ unidiff -f patch.diff

"""


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
    )

    parser.add_argument(
        '--show-diff',
        action='store_true',
        default=False,
        dest='show_diff',
        help='output diff to stdout',
    )

    parser.add_argument(
        '-f',
        '--file',
        dest='diff_file',
        type=argparse.FileType('r'),
        help='if not specified, read diff data from stdin',
    )

    return parser


def _display_path(fp: FilePatch) -> str:
    if fp.is_deleted_file:
        return fp.old_path or '<unknown>'
    if fp.is_new_file:
        return fp.new_path or '<unknown>'
    return fp.new_path or fp.old_path or '<unknown>'


def _is_rename(fp: FilePatch) -> bool:
    has_from = any(h.kind == ExtendedHeaderKind.RENAME_FROM for h in fp.extended_headers)
    has_to = any(h.kind == ExtendedHeaderKind.RENAME_TO for h in fp.extended_headers)
    return has_from and has_to


def _iter_modified_files(files: ta.Iterable[FilePatch]) -> ta.Iterator[FilePatch]:
    for fp in files:
        if not fp.is_new_file and not fp.is_deleted_file:
            yield fp


def _iter_added_files(files: ta.Iterable[FilePatch]) -> ta.Iterator[FilePatch]:
    for fp in files:
        if fp.is_new_file:
            yield fp


def _iter_removed_files(files: ta.Iterable[FilePatch]) -> ta.Iterator[FilePatch]:
    for fp in files:
        if fp.is_deleted_file:
            yield fp


def _print_summary(patch: PatchSet) -> None:
    print('Summary')
    print('-------')

    additions = 0
    deletions = 0
    renamed_files = 0

    modified_files = list(_iter_modified_files(patch.files))
    added_files = list(_iter_added_files(patch.files))
    removed_files = list(_iter_removed_files(patch.files))

    for fp in patch.files:
        path = _display_path(fp)

        if fp.binary:
            print(f'{path}:', '(binary file)')
        else:
            additions += fp.added_count
            deletions += fp.removed_count
            print(f'{path}:', f'+{fp.added_count:d} additions,', f'-{fp.removed_count:d} deletions')

        if _is_rename(fp):
            renamed_files += 1

    print()
    print(
        f'{len(modified_files):d} modified file(s), '
        f'{len(added_files):d} added file(s), '
        f'{len(removed_files):d} removed file(s)',
    )
    if renamed_files:
        print(f'{renamed_files:d} file(s) renamed')
    print(f'Total: {additions:d} addition(s), {deletions:d} deletion(s)')


def _main(argv: ta.Sequence[str] | None = None) -> int:
    parser = get_parser()
    args = parser.parse_args(argv)

    if args.diff_file is not None:
        diff_text = args.diff_file.read()
    else:
        diff_text = sys.stdin.read()

    patch = parse_patch(diff_text)

    if args.show_diff:
        sys.stdout.write(diff_text)
        if diff_text and not diff_text.endswith('\n'):
            sys.stdout.write('\n')
        print()

    _print_summary(patch)
    return 0


if __name__ == '__main__':
    raise SystemExit(_main())
