# MIT License
#
# Copyright (c) LangChain, Inc.
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
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import abc
import re
import typing as ta

from .docs import Doc


##


def split_text_with_regex(
        text: str,
        separator: str,
        *,
        keep_separator: bool | ta.Literal['start', 'end'],
) -> list[str]:
    if not separator:
        return [s for s in text if s]

    if not keep_separator:
        return [s for s in re.split(separator, text) if s]

    lst = re.split(f'({separator})', text)
    splits = (
        ([lst[i] + lst[i + 1] for i in range(0, len(lst) - 1, 2)])
        if keep_separator == 'end'
        else ([lst[i] + lst[i + 1] for i in range(1, len(lst), 2)])
    )

    if len(lst) % 2 == 0:
        splits += lst[-1:]

    if keep_separator == 'end':
        splits = [*splits, lst[-1]]
    else:
        splits = [lst[0], *splits]

    return [s for s in splits if s]


def join_texts(
        texts: ta.Sequence[str],
        separator: str,
        *,
        strip_whitespace: bool = True,
) -> str | None:
    joined = separator.join(texts)
    if strip_whitespace:
        joined = joined.strip()
    if joined == '':
        return None
    else:
        return joined


class TextSplitter:
    def __init__(
            self,
            *,
            chunk_size: int = 1000,
            chunk_overlap: int = 200,
            length_function: ta.Callable[[str], int] = len,
            strip_whitespace: bool = True,
    ) -> None:
        super().__init__()

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._length_function = length_function
        self._strip_whitespace = strip_whitespace

    def merge_splits(
            self,
            splits: ta.Iterable[str],
            separator: str,
    ) -> list[str]:
        separator_len = self._length_function(separator)

        docs = []
        current_doc: list[str] = []
        total = 0
        for d in splits:
            l = self._length_function(d)
            if total + l + (separator_len if len(current_doc) > 0 else 0) > self._chunk_size:
                if total > self._chunk_size:
                    raise Exception(f'Created a chunk of size {total}, which is longer than the specified {self._chunk_size}')  # noqa

                if len(current_doc) > 0:
                    doc = join_texts(current_doc, separator)
                    if doc is not None:
                        docs.append(doc)

                    while (
                            total > self._chunk_overlap or
                            (total + l + (separator_len if len(current_doc) > 0 else 0) > self._chunk_size and total > 0)  # noqa
                    ):
                        total -= self._length_function(current_doc[0]) + (separator_len if len(current_doc) > 1 else 0)
                        current_doc = current_doc[1:]

            current_doc.append(d)
            total += l + (separator_len if len(current_doc) > 1 else 0)

        doc = join_texts(current_doc, separator)
        if doc is not None:
            docs.append(doc)

        return docs

    @abc.abstractmethod
    def split_text(
            self,
            text: str,
            *,
            separators: ta.Sequence[str] | None = None,
    ) -> list[str]:
        raise NotImplementedError

    def split_docs(
            self,
            docs: ta.Iterable[Doc],
            *,
            add_start_index: bool = False,
    ) -> list[Doc]:
        texts, metadatas = [], []
        for doc in docs:
            texts.append(doc.content)
            metadatas.append(doc.metadata)

        out = []
        for i, text in enumerate(texts):
            index = 0
            previous_chunk_len = 0
            for chunk in self.split_text(text):
                metadata: dict = dict(metadatas[i] or {})

                if add_start_index:
                    offset = index + previous_chunk_len - self._chunk_overlap
                    index = text.find(chunk, max(0, offset))
                    metadata['start_index'] = index
                    previous_chunk_len = len(chunk)

                out.append(Doc(
                    content=chunk,
                    metadata=metadata,
                ))

        return out


class RecursiveTextSplitter(TextSplitter):
    def __init__(
            self,
            *,
            separators: ta.Sequence[str] = ('\n\n', '\n', ' ', ''),
            is_separator_regex: bool = False,
            keep_separator: bool = True,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._separators = separators
        self._is_separator_regex = is_separator_regex
        self._keep_separator = keep_separator

    def split_text(
            self,
            text: str,
            *,
            separators: ta.Sequence[str] | None = None,
    ) -> list[str]:
        if separators is None:
            separators = self._separators

        final_chunks = []

        separator = separators[-1]
        new_separators: ta.Sequence[str] = []
        for i, _s in enumerate(separators):
            sep = _s if self._is_separator_regex else re.escape(_s)
            if not _s:
                separator = _s
                break
            if re.search(sep, text):
                separator = _s
                new_separators = separators[i + 1:]
                break

        sep = separator if self._is_separator_regex else re.escape(separator)
        splits = split_text_with_regex(
            text,
            sep,
            keep_separator=self._keep_separator,
        )

        good_splits = []
        sep = '' if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                good_splits.append(s)
                continue

            if good_splits:
                merged_text = self.merge_splits(good_splits, sep)
                final_chunks.extend(merged_text)
                good_splits = []

            if not new_separators:
                final_chunks.append(s)

            else:
                other_info = self.split_text(s, separators=new_separators)
                final_chunks.extend(other_info)

        if good_splits:
            merged_text = self.merge_splits(good_splits, sep)
            final_chunks.extend(merged_text)

        return final_chunks
