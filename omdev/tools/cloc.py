"""
TODO:
 - handle test code separately
  - tags again lol - language:, test:, whitespace:, comment:,
"""
import dataclasses as dc
import os
import re
import typing as ta

from ..cli import CliModule


SUPPORTED_EXTENSIONS: ta.Mapping[str, str] = {
    '.c': 'c',
    '.cpp': 'c',
    '.h': 'c',
    '.hpp': 'c',
    '.py': 'python',
    '.js': 'javascript',
}


COMMENT_PATTERNS: ta.Mapping[str, tuple[str, str | None, str | None]] = {
    'c': (r'//', r'/\*', r'\*/'),
    'python': (r'#', None, None),
    'javascript': (r'//', r'/\*', r'\*/'),
}


@dc.dataclass(frozen=True)
class FileLineCount:
    loc: int
    blanks: int
    comments: int


def count_lines(file_path: str, language: str) -> FileLineCount:
    single_line_comment, block_comment_start, block_comment_end = COMMENT_PATTERNS[language]

    in_block_comment = False

    loc = 0
    blank_lines = 0
    comment_lines = 0

    with open(file_path, encoding='utf-8') as file:
        for line in file:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
                continue

            if in_block_comment:
                comment_lines += 1
                if block_comment_end and re.search(block_comment_end, stripped):
                    in_block_comment = False
                continue

            if block_comment_start and re.search(block_comment_start, stripped):
                comment_lines += 1
                if block_comment_end and not re.search(block_comment_end, stripped):
                    in_block_comment = True
                continue

            if single_line_comment and stripped.startswith(single_line_comment):
                comment_lines += 1
                continue

            loc += 1

    return FileLineCount(
        loc=loc,
        blanks=blank_lines,
        comments=comment_lines,
    )


def count_lines_in_directory(
        directory: str,
        *,
        include: list[re.Pattern[str]] | None = None,
        exclude: list[re.Pattern[str]] | None = None,
) -> ta.Mapping[str, FileLineCount]:
    results: dict[str, FileLineCount] = {}
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            file_path = os.path.join(root, file)

            if include and not any(p.fullmatch(file_path) for p in include):
                continue
            if exclude and any(p.fullmatch(file_path) for p in exclude):
                continue

            language = SUPPORTED_EXTENSIONS[ext]
            results[file_path] = count_lines(file_path, language)

    return results


def display_results(results: ta.Mapping[str, FileLineCount]) -> None:
    total_loc = total_blanks = total_comments = 0
    file_width = max(map(len, results))
    dash_width = 41 + file_width

    print(
        f"{'File'.ljust(file_width)} "
        f"{'LOC':<10} "
        f"{'Blank Lines':<15} "
        f"{'Comment Lines':<15}",
    )

    print('-' * dash_width)

    for file, counts in sorted(results.items()):
        loc, blanks, comments = counts.loc, counts.blanks, counts.comments
        total_loc += loc
        total_blanks += blanks
        total_comments += comments
        print(
            f'{file.ljust(file_width)} '
            f'{loc:<10} '
            f'{blanks:<15} '
            f'{comments:<15}',
        )

    print('-' * dash_width)

    print(
        f"{' ' * file_width} "
        f"{'LOC':<10} "
        f"{'Blank Lines':<15} "
        f"{'Comment Lines':<15}",
    )

    print('-' * dash_width)

    print(
        f"{'Total'.ljust(file_width)} "
        f"{total_loc:<10} "
        f"{total_blanks:<15} "
        f"{total_comments:<15}",
    )


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='Count lines of code in source files.')

    parser.add_argument('directory', help='The directory to analyze.', nargs='+')

    parser.add_argument('-i,', '--include', action='append')
    parser.add_argument('-e,', '--exclude', action='append')

    args = parser.parse_args()

    #

    include: list[re.Pattern[str]] | None = None
    if args.include:
        include = [re.compile(p) for p in args.include]

    exclude: list[re.Pattern[str]] | None = None
    if args.exclude:
        exclude = [re.compile(p) for p in args.exclude]

    #

    results_by_directory: dict[str, FileLineCount] = {}
    for directory in args.directory:
        results = count_lines_in_directory(
            directory,
            include=include,
            exclude=exclude,
        )

        if not results:
            continue

        display_results(results)
        print()

        results_by_directory[directory] = FileLineCount(
            loc=sum(flc.loc for flc in results.values()),
            blanks=sum(flc.blanks for flc in results.values()),
            comments=sum(flc.comments for flc in results.values()),
        )

    if len(results_by_directory) > 1:
        display_results(results_by_directory)
        print()


# @omlish-manifest
_CLI_MODULE = CliModule('cloc', __name__)


if __name__ == '__main__':
    _main()
