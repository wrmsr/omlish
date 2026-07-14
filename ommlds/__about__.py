from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'ommlds'
    description = 'ommlds'

    dependencies = [
        f'omlish == {__version__}',
    ]

    optional_dependencies = {
        'omdev': [
            f'omdev == {__version__}',
        ],

        #

        'backends': [
            # 'diffusers ~= 0.39',

            'llama-cpp-python ~= 0.3',

            'mlx ~= 0.32; sys_platform == "darwin"',
            'mlx-lm ~= 0.31; sys_platform == "darwin"',

            'sentencepiece ~= 0.2',

            'tiktoken ~= 0.13',

            # 'tinygrad @ git+https://github.com/tinygrad/tinygrad',
            'tinygrad ~= 0.13',

            'tokenizers ~= 0.22',

            'torch ~= 2.13',

            'transformers ~= 5.11',
            'sentence-transformers ~= 5.6',
        ],

        'huggingface': [
            'huggingface-hub ~= 1.23',
            'datasets ~= 5.0',
        ],

        'nanochat': [
            'regex >= 2026.7',
        ],

        'numpy': [
            'numpy >= 2.5',
        ],

        'ocr': [
            'pytesseract ~= 0.3',

            'rapidocr-onnxruntime ~= 1.4',
        ],

        'pillow': [
            'pillow ~= 12.3',
        ],

        'search': [
            'ddgs ~= 9.14',

            'tavily-python ~= 0.7',
        ],

        'xml': [
            'lxml >= 6.1',
        ],
    }

    entry_points = {
        'omlish.manifests': {name: name},
    }


class Setuptools(SetuptoolsBase):
    rs = True

    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
