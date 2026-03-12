# Copyright (c) 2025 Darren Burns
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import dataclasses as dc
import pathlib

from rich.align import Align
from rich.console import Console
from rich.console import ConsoleOptions
from rich.console import RenderResult
from rich.markup import escape
from rich.rule import Rule
from rich.segment import Segment
from rich.table import Table
from rich.text import Text

from ....unidiff import PatchedFile
from .underlinebar import UnderlineBar


##


def simple_pluralise(word: str, number: int) -> str:
    if number == 1:
        return word
    else:
        return word + 's'


@dc.dataclass()
class PatchSetHeader:
    file_modifications: int
    file_additions: int
    file_removals: int
    line_additions: int
    line_removals: int

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        if self.file_modifications:
            yield Align.center(
                f"[blue]{self.file_modifications} {simple_pluralise('file', self.file_modifications)} changed",
            )
        if self.file_additions:
            yield Align.center(
                f"[green]{self.file_additions} {simple_pluralise('file', self.file_additions)} added",
            )
        if self.file_removals:
            yield Align.center(
                f"[red]{self.file_removals} {simple_pluralise('file', self.file_removals)} removed",
            )

        bar_width = console.width // 5
        changed_lines = max(1, self.line_additions + self.line_removals)
        added_lines_ratio = self.line_additions / changed_lines

        line_changes_summary = Table.grid()
        line_changes_summary.add_column()
        line_changes_summary.add_column()
        line_changes_summary.add_column()
        line_changes_summary.add_row(
            f'[bold green]+{self.line_additions} ',
            UnderlineBar(
                highlight_range=(0, added_lines_ratio * bar_width),
                highlight_style='green',
                background_style='red',
                width=bar_width,
            ),
            f' [bold red]-{self.line_removals}',
        )

        bar_hpad = len(str(self.line_additions)) + len(str(self.line_removals)) + 4
        yield Align.center(line_changes_summary, width=bar_width + bar_hpad)
        yield Segment.line()


class RemovedFileBody:
    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Rule(characters='╲', style='hatched')
        yield Rule(' [red]File was removed ', characters='╲', style='hatched')
        yield Rule(characters='╲', style='hatched')
        yield Rule(style='border', characters='▔')


@dc.dataclass()
class BinaryFileBody:
    size_in_bytes: int

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Rule(characters='╲', style='hatched')
        yield Rule(
            Text(f' File is binary · {self.size_in_bytes} bytes ', style='blue'),
            characters='╲',
            style='hatched',
        )
        yield Rule(characters='╲', style='hatched')
        yield Rule(style='border', characters='▔')


class PatchedFileHeader:
    def __init__(self, patch: PatchedFile):
        self.patch = patch
        if patch.is_rename:
            self.path_prefix = (
                f'[dim][s]{escape(pathlib.Path(patch.source_file).name)}[/] → [/]'
            )
        elif patch.is_added_file:
            self.path_prefix = f'[bold green]Added [/]'
        else:
            self.path_prefix = ''

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Rule(
            f'{self.path_prefix}[b]{escape(self.patch.path)}[/] ([green]{self.patch.added} additions[/], '
            f'[red]{self.patch.removed} removals[/])',
            style='border',
            characters='▁',
        )


class OnlyRenamedFileBody:
    """Represents a file that was renamed but the content was not changed."""

    def __init__(self, patch: PatchedFile):
        self.patch = patch

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Rule(characters='╲', style='hatched')
        yield Rule(' [blue]File was only renamed ', characters='╲', style='hatched')
        yield Rule(characters='╲', style='hatched')
        yield Rule(style='border', characters='▔')
