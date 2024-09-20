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
            'llama-cpp-python ~= 0.2',

            'openai ~= 1.47',

            'sentence_transformers ~= 3.1',

            'transformers ~= 4.44',
        ],

        'huggingface': [
            'huggingface-hub ~= 0.25',
            'datasets ~= 3.0',
        ],

        'pillow': [
            'pillow ~= 10.4',
        ],

        'tinygrad': [
            # 'tinygrad @ git+https://github.com/tinygrad/tinygrad',
            'tinygrad ~= 0.9',
        ],

        'torch': [
            'torch ~= 2.4',
        ],

        'wiki': [
            'mwparserfromhell ~= 0.6',
            'wikitextparser ~= 0.56',  # !! GPL
        ],

        'xml': [
            'lxml ~= 5.3; python_version < "3.13"',
        ],
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
