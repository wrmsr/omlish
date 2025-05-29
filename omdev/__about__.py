from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'omdev'
    description = 'omdev'

    dependencies = [
        f'omlish == {__version__}',
    ]

    optional_dependencies = {
        'black': [
            'black ~= 25.1',
        ],

        'c': [
            'pycparser ~= 2.22',
            'pcpp ~= 1.30',
        ],

        'doc': [
            'docutils ~= 0.21',

            'markdown-it-py ~= 3.0',
            'mdit-py-plugins ~= 0.4',

            'pygments ~= 2.19',
        ],

        'mypy': [
            'mypy ~= 1.16',
        ],

        'prof': [
            'gprof2dot ~= 2025.4',
        ],

        'ptk': [
            'prompt-toolkit ~= 3.0',
        ],

        'qr': [
            'segno ~= 1.6',
        ],
    }

    entry_points = {
        'omlish.manifests': {name: name},
    }

    cli_scripts = {
        'om': f'{name}.cli.main:_main',
    }


class Setuptools(SetuptoolsBase):
    cexts = True

    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
