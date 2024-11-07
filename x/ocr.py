import argparse
import os.path
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    from PIL import Image
    import pytesseract
    import rapidocr_onnxruntime as rapidocr

else:
    Image = lang.proxy_import('PIL.Image')
    pytesseract = lang.proxy_import('pytesseract')
    rapidocr = lang.proxy_import('rapidocr_onnxruntime')


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
    parser.add_argument('file')
    parser.add_argument('-b', '--backend', default=DEFAULT_OCR_BACKEND)
    args = parser.parse_args()

    ocr = OCR_BACKENDS[args.backend]

    with Image.open(os.path.expanduser(args.file)) as img:
        text = ocr(img)

    print(text)


if __name__ == '__main__':
    _main()
