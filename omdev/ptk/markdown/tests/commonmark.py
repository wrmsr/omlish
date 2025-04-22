# Copyright (c) 2015, Robin Stocker
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Original:
#  https://github.com/commonmark/commonmark-java/blob/749c0110cb48d8338b10593b849992d00d9d7611/commonmark-test-util/src/main/java/org/commonmark/testutil/example/ExampleReader.java
import dataclasses as dc
import enum
import json
import os.path
import re
import typing as ta

from omlish import check

from ....cache import data as dcache


##


@dc.dataclass(frozen=True)
class SpecExample:
    """Example of CommonMark source and the expected HTML rendering."""

    filename: str
    section: str
    info: str
    example_number: int
    source: str
    html: str

    def __str__(self) -> str:
        return f'File "{self.filename}" section "{self.section}" example {self.example_number}'


class SpecExampleReader:
    """Reader for files containing examples of CommonMark source and the expected HTML rendering (e.g. spec.txt)."""

    class _State(enum.Enum):
        BEFORE = 1
        SOURCE = 2
        HTML = 3

    def __init__(
            self,
            filename: str,
    ) -> None:
        super().__init__()

        self._filename = filename

        self._state = SpecExampleReader._State.BEFORE
        self._section: str | None = None

        # The gfm spec has additional text after the example marker for their additions, e.g. "table"
        self._info = ''
        self._source = ''
        self._html = ''
        self._example_number = 0

    def _reset_contents(self) -> None:
        self._source = ''
        self._html = ''

    def read(self, lines: ta.Iterable[str]) -> list[SpecExample]:
        self._reset_contents()

        lst: list[SpecExample] = []
        for line in lines:
            lst.extend(self._process_line(line.rstrip('\n')))

        return lst

    _SECTION_PAT = re.compile(r'#{1,6} *(.*)')

    _EXAMPLE_START_MARKER = '```````````````````````````````` example'
    _EXAMPLE_END_MARKER = '````````````````````````````````'

    def _process_line(self, line: str) -> ta.Iterator[SpecExample]:
        if self._state == SpecExampleReader._State.BEFORE:
            if (m := self._SECTION_PAT.match(line)) is not None:
                self._section = m.group(1)
                self._example_number = 0

            if line.startswith(self._EXAMPLE_START_MARKER):
                self._info = line[len(self._EXAMPLE_START_MARKER):].strip()
                self._state = SpecExampleReader._State.SOURCE
                self._example_number += 1

        elif self._state == SpecExampleReader._State.SOURCE:
            if line == '.':
                self._state = SpecExampleReader._State.HTML
            else:
                # examples use "rightwards arrow" to show tab
                processed_line = line.replace('\u2192', '\t')
                self._source += processed_line + '\n'

        elif self._state == SpecExampleReader._State.HTML:
            if line == self._EXAMPLE_END_MARKER:
                self._state = SpecExampleReader._State.BEFORE
                yield SpecExample(
                    filename=self._filename,
                    section=check.not_none(self._section),
                    info=self._info,
                    example_number=self._example_number,
                    source=self._source,
                    html=self._html,
                )
                self._reset_contents()
            else:
                self._html += line + '\n'


##


COMMONMARK_SPEC_DATA = dcache.GitSpec(
    'https://github.com/commonmark/commonmark-spec',
    rev='a78fcaf20eb281b0bfbed2427691f57b984b1d8f',
)


def _main() -> None:
    cs_dir = dcache.default().get(COMMONMARK_SPEC_DATA)
    spec_file = os.path.join(cs_dir, 'spec.txt')

    with open(spec_file) as f:
        er = SpecExampleReader(os.path.basename(spec_file))
        exs = er.read(f)

    exs_json = json.dumps([dc.asdict(ex) for ex in exs])
    print(exs_json)


if __name__ == '__main__':
    _main()
