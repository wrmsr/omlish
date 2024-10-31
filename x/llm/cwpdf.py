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
import dataclasses as dc
import io
import os.path
import re
import typing as ta

import numpy as np
import pypdf


##


@dc.dataclass(frozen=True)
class Doc:
    content: str
    metadata: ta.Mapping[str, ta.Any] | None = None


##


def extract_text_from_page(page: pypdf.PageObject) -> str:
    return page.extract_text(
        extraction_mode='plain',
    )


##


PDF_FILTER_WITH_LOSS = {
    'DCTDecode',
    'DCT',
    'JPXDecode',
}

PDF_FILTER_WITHOUT_LOSS = {
    'LZWDecode',
    'LZW',
    'FlateDecode',
    'Fl',
    'ASCII85Decode',
    'A85',
    'ASCIIHexDecode',
    'AHx',
    'RunLengthDecode',
    'RL',
    'CCITTFaxDecode',
    'CCF',
    'JBIG2Decode',
}


def extract_from_images_with_rapidocr(
        images: ta.Sequence[ta.Iterable[np.ndarray] | bytes],
) -> str:
    from rapidocr_onnxruntime import RapidOCR

    ocr = RapidOCR()
    text = ''
    for img in images:
        result, _ = ocr(img)
        if result:
            result = [text[1] for text in result]
            text += '\n'.join(result)

    return text


def extract_images_from_page(page: pypdf.PageObject) -> str:
    if '/XObject' not in page['/Resources'].keys():  # type: ignore
        return ''

    xobj = page['/Resources']['/XObject'].get_object()  # type: ignore
    images = []
    for obj in xobj:
        if xobj[obj]['/Subtype'] == '/Image':
            if xobj[obj]['/Filter'][1:] in PDF_FILTER_WITHOUT_LOSS:
                height, width = xobj[obj]['/Height'], xobj[obj]['/Width']

                images.append(
                    np.frombuffer(
                        xobj[obj].get_data(),
                        dtype=np.uint8,
                    ).reshape(
                        height,
                        width,
                        -1,
                    ),
                )

            elif xobj[obj]['/Filter'][1:] in PDF_FILTER_WITH_LOSS:
                images.append(xobj[obj].get_data())

            else:
                raise Exception('Unknown PDF Filter!')

    return extract_from_images_with_rapidocr(images)


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

    splits = (
        (splits + [lst[-1]])
        if keep_separator == 'end'
        else ([lst[0]] + splits)
    )

    return [s for s in splits if s]


def join_docs(
        docs: ta.Sequence[str],
        separator: str,
        *,
        strip_whitespace: bool = True,
) -> str | None:
    text = separator.join(docs)
    if strip_whitespace:
        text = text.strip()
    if text == '':
        return None
    else:
        return text


def merge_splits(
        splits: ta.Iterable[str],
        *,
        separator: str,
        chunk_size: int,
        chunk_overlap: int,
        length_function: ta.Callable[[str], int],
        strip_whitespace: bool,
) -> list[str]:
    separator_len = length_function(separator)

    docs = []
    current_doc: list[str] = []
    total = 0
    for d in splits:
        l = length_function(d)
        if total + l + (separator_len if len(current_doc) > 0 else 0) > chunk_size:
            if total > chunk_size:
                raise Exception(f'Created a chunk of size {total}, which is longer than the specified {chunk_size}')

            if len(current_doc) > 0:
                doc = join_docs(current_doc, separator)
                if doc is not None:
                    docs.append(doc)

                while (
                        total > chunk_overlap or
                        (total + l + (separator_len if len(current_doc) > 0 else 0) > chunk_size and total > 0)
                ):
                    total -= length_function(current_doc[0]) + (separator_len if len(current_doc) > 1 else 0)
                    current_doc = current_doc[1:]

        current_doc.append(d)
        total += l + (separator_len if len(current_doc) > 1 else 0)

    doc = join_docs(current_doc, separator)
    if doc is not None:
        docs.append(doc)

    return docs


def split_text(
        text: str,
        *,
        separators: ta.Sequence[str] = ("\n\n", "\n", " ", ""),
        is_separator_regex: bool = False,
        keep_separator: bool = True,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        length_function: ta.Callable[[str], int] = len,
        strip_whitespace: bool = True,
) -> list[str]:
    final_chunks = []

    separator = separators[-1]
    new_separators: ta.Sequence[str] = []
    for i, s in enumerate(separators):
        sep = s if is_separator_regex else re.escape(s)
        if not s:
            separator = s
            break
        if re.search(sep, text):
            separator = s
            new_separators = separators[i + 1:]
            break

    sep = separator if is_separator_regex else re.escape(separator)
    splits = split_text_with_regex(
        text,
        sep,
        keep_separator=keep_separator,
    )

    good_splits = []
    sep = '' if keep_separator else separator
    for s in splits:
        if length_function(s) >= chunk_size:
            good_splits.append(s)

        elif good_splits:
            merged_text = merge_splits(
                good_splits,
                separator=sep,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=length_function,
                strip_whitespace=strip_whitespace,
            )
            final_chunks.extend(merged_text)
            good_splits = []

        elif not new_separators:
            final_chunks.append(s)

        else:
            other_info = split_text(
                s,
                separators=new_separators,
            )
            final_chunks.extend(other_info)

    if good_splits:
        merged_text = merge_splits(
            good_splits,
            separator=sep,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
            strip_whitespace=strip_whitespace,
        )
        final_chunks.extend(merged_text)

    return final_chunks


def split_documents(
        documents: ta.Iterable[Doc],
        *,
        add_start_index: bool = False,
        chunk_overlap: int = 200,
        **kwargs: ta.Any,
) -> list[Doc]:
    texts, metadatas = [], []
    for doc in documents:
        texts.append(doc.content)
        metadatas.append(doc.metadata)

    out = []
    for i, text in enumerate(texts):
        index = 0
        previous_chunk_len = 0
        for chunk in split_text(
                text,
                chunk_overlap=chunk_overlap,
                **kwargs,
        ):
            metadata: dict = dict(metadatas[i] or {})

            if add_start_index:
                offset = index + previous_chunk_len - chunk_overlap
                index = text.find(chunk, max(0, offset))
                metadata['start_index'] = index
                previous_chunk_len = len(chunk)

            out.append(Doc(
                content=chunk,
                metadata=metadata,
            ))

    return out


##


def _main() -> None:
    pdf_file = os.path.expanduser('~/Downloads/nke-10k-2023.pdf')
    pdf_reader = pypdf.PdfReader(pdf_file)

    extract_images = False

    docs = [
        Doc(
            content=' '.join([
                extract_text_from_page(page),
                *([extract_images_from_page(page)] if extract_images else []),
            ]),
            metadata={
                'source': pdf_file,
                'page': page_number
            },
        )
        for page_number, page in enumerate(pdf_reader.pages)
    ]

    splits = split_documents(docs)

    print(splits)


if __name__ == '__main__':
    _main()
