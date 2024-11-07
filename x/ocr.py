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


def _main() -> None:
    from PIL import Image
    img = Image.open(os.path.expanduser('~/Desktop/Screen Shot 2024-11-07 at 14.55.49.png'))

    ocr = rapidocr.RapidOCR()
    result, _ = ocr(img)  # noqa
    text = '\n'.join(text[1] for text in result or [])
    print(text)

    print()

    text = pytesseract.image_to_string(img)
    print(text)


if __name__ == '__main__':
    _main()
