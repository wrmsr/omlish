from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'ommlds'
    description = 'ommlds'

    dependencies = [
        f'omdev == {__version__}',
        f'omlish == {__version__}',
    ]

    optional_dependencies = {
        'backends': [
            # 'diffusers ~= 0.35',

            'llama-cpp-python ~= 0.3',

            'mlx ~= 0.28',
            'mlx-lm ~= 0.26; sys_platform == "darwin"',

            # 'sentencepiece ~= 0.2',  # FIXME: https://github.com/google/sentencepiece/issues/1121

            'tiktoken ~= 0.11',

            # 'tinygrad @ git+https://github.com/tinygrad/tinygrad',
            'tinygrad ~= 0.11',

            'tokenizers ~= 0.22',

            'torch ~= 2.8',

            'transformers ~= 4.56',
            'sentence-transformers ~= 5.1',
        ],

        'huggingface': [
            'huggingface-hub ~= 0.34',
            'datasets ~= 4.0',
        ],

        'numpy': [
            'numpy >= 1.26',
        ],

        'ocr': [
            'pytesseract ~= 0.3',

            'rapidocr-onnxruntime ~= 1.4',
        ],

        'pillow': [
            'pillow ~= 11.3',
        ],

        'search': [
            'ddgs ~= 9.5',
        ],

        'wiki': [
            'mwparserfromhell ~= 0.7',

            'wikitextparser ~= 0.56',  # !! GPL
        ],

        'xml': [
            'lxml >= 5.3; python_version < "3.13"',
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
