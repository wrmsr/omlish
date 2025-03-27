from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'ommlx'
    description = 'ommlx'

    dependencies = [
        f'omdev == {__version__}',
        f'omlish == {__version__}',
    ]

    optional_dependencies = {
        'backends': [
            'mlx-lm ~= 0.22; sys_platform == "darwin"',

            'sentence-transformers ~= 4.0',

            'transformers ~= 4.50',
        ],

        'huggingface': [
            'huggingface-hub ~= 0.27',
            'datasets ~= 3.5',
        ],

        'llamacpp': [
            'llama-cpp-python ~= 0.3',
        ],

        'numpy': [
            'numpy >= 1.26',
        ],

        'ocr': [
            'pytesseract ~= 0.3',

            'rapidocr-onnxruntime ~= 1.4',
        ],

        'pillow': [
            'pillow ~= 11.1',
        ],

        'search': [
            'duckduckgo-search ~= 7.5',
        ],

        'tinygrad': [
            # 'tinygrad @ git+https://github.com/tinygrad/tinygrad',
            'tinygrad ~= 0.10',
        ],

        'torch': [
            'torch ~= 2.6',
        ],

        'wiki': [
            'mwparserfromhell ~= 0.6',

            'wikitextparser ~= 0.56',  # !! GPL
        ],

        'xml': [
            'lxml ~= 5.3; python_version < "3.13"',
        ],
    }

    entry_points = {
        'omlish.manifests': {name: name},
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
