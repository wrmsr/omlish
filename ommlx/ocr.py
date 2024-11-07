"""
TODO:
 - clipboard
"""
import argparse
import os.path
import sys
import typing as ta

from omdev.cli import CliModule
from omlish import lang


if ta.TYPE_CHECKING:
    import pytesseract
    import rapidocr_onnxruntime as rapidocr
    from PIL import Image

else:
    pytesseract = lang.proxy_import('pytesseract')
    rapidocr = lang.proxy_import('rapidocr_onnxruntime')
    Image = lang.proxy_import('PIL.Image')


##


Ocr: ta.TypeAlias = ta.Callable[['Image.Image'], str]

OCR_BACKENDS: ta.Mapping[str, Ocr] = {
    'rapidocr': lambda img: '\n'.join(text[1] for text in rapidocr.RapidOCR()(img)[0] or []),
    'tesseract': lambda img: pytesseract.image_to_string(img),
}

DEFAULT_OCR_BACKEND = 'rapidocr'


##


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('-b', '--backend', default=DEFAULT_OCR_BACKEND)
    args = parser.parse_args()

    ocr = OCR_BACKENDS[args.backend]

    with Image.open(os.path.expanduser(args.file) if args.file else sys.stdin.buffer) as img:
        text = ocr(img)

    print(text)


# @omlish-manifest
_CLI_MODULE = CliModule('ocr', __name__)


if __name__ == '__main__':
    _main()
