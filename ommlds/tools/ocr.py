"""
TODO:
 - linux clipboard
"""
import argparse
import io
import os.path
import sys
import typing as ta

from omdev.cli import CliModule
from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import pytesseract
    import rapidocr_onnxruntime as rapidocr
    from PIL import Image

    from omdev.clipboard import darwin_cf as darwin_clipboard

else:
    pytesseract = lang.proxy_import('pytesseract')
    rapidocr = lang.proxy_import('rapidocr_onnxruntime')
    Image = lang.proxy_import('PIL.Image')

    darwin_clipboard = lang.proxy_import('omdev.clipboard.darwin_cf')


##


Ocr: ta.TypeAlias = ta.Callable[['Image.Image'], str]

OCR_BACKENDS: ta.Mapping[str, Ocr] = {
    'rapidocr': lambda img: '\n'.join(text[1] for text in rapidocr.RapidOCR()(img)[0] or []),
    'tesseract': lambda img: pytesseract.image_to_string(img),
}

DEFAULT_OCR_BACKEND = 'rapidocr'


##


def _get_img_data(file: str | None) -> ta.Any:
    if file == '@':
        if sys.platform == 'darwin':
            cis = darwin_clipboard.get_darwin_clipboard_data(types={'public.png'})
            if not cis:
                raise RuntimeError('No clipboard image data found')
            return io.BytesIO(check.not_none(cis[0].data))

        else:
            raise OSError(sys.platform)

    elif file:
        return os.path.expanduser(file)

    else:
        return sys.stdin.buffer


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('-b', '--backend', choices=list(OCR_BACKENDS), default=DEFAULT_OCR_BACKEND)
    args = parser.parse_args()

    #

    ocr = OCR_BACKENDS[args.backend]

    img_data = _get_img_data(args.file)

    with Image.open(img_data) as img:
        text = ocr(img)

    print(text)


# @omlish-manifest
_CLI_MODULE = CliModule('ocr', __name__)


if __name__ == '__main__':
    _main()
