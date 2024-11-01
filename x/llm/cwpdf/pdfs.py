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
import contextlib
import typing as ta

from omlish import lang

from .docs import Doc


if ta.TYPE_CHECKING:
    import numpy as np
    import pypdf

else:
    np = lang.proxy_import('numpy')
    pypdf = lang.proxy_import('pypdf')


T = ta.TypeVar('T')


##


def extract_text_from_page(page: 'pypdf.PageObject') -> str:
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
        images: ta.Sequence[ta.Iterable['np.ndarray'] | bytes],
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


def extract_images_from_page(page: 'pypdf.PageObject') -> str:
    if '/XObject' not in page['/Resources'].keys():  # type: ignore  # noqa
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


def extract_page_content(
        page: 'pypdf.PageObject',
        *,
        extract_images: bool = False,
) -> str:
    return ' '.join([
        extract_text_from_page(page),
        *([extract_images_from_page(page)] if extract_images else []),
    ])


##


def build_pdf_docs(pdf_file: str) -> list[Doc]:
    with contextlib.closing(pypdf.PdfReader(pdf_file)) as pdf_reader:
        return [
            Doc(
                content=extract_page_content(page),
                metadata={
                    'source': pdf_file,
                    'page': page_number,
                },
            )
            for page_number, page in enumerate(pdf_reader.pages)
        ]
