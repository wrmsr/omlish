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
            'anthropic ~= 0.37',

            'openai ~= 1.51',

            'sentence_transformers ~= 3.2',

            'transformers ~= 4.45',
        ],

        'huggingface': [
            'huggingface-hub ~= 0.25',
            'datasets ~= 3.0',
        ],

        'llamacpp': [
            'llama-cpp-python ~= 0.3',
        ],

        'numpy': [
            'numpy >= 1.20',
        ],

        'pillow': [
            'pillow ~= 11.0',
        ],

        'tinygrad': [
            # 'tinygrad @ git+https://github.com/tinygrad/tinygrad',
            'tinygrad ~= 0.9',
        ],

        'torch': [
            'torch ~= 2.5',
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
