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
            'mlx-lm ~= 0.24; sys_platform == "darwin"',

            'transformers ~= 4.52',
            'sentence-transformers ~= 4.1',

            'diffusers ~= 0.33.1',

            'sentencepiece ~= 0.2',
            'tiktoken ~= 0.9',
            'tokenizers ~= 0.21',
        ],

        'huggingface': [
            'huggingface-hub ~= 0.32',
            'datasets ~= 3.6',
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
            'duckduckgo-search ~= 8.0',
        ],

        'tinygrad': [
            # 'tinygrad @ git+https://github.com/tinygrad/tinygrad',
            'tinygrad ~= 0.10',
        ],

        'torch': [
            'torch ~= 2.7',
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
