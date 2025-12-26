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
            'black ~= 25.12',
        ],

        'c': [
            'pycparser ~= 2.23',
            'pcpp ~= 1.30',
        ],

        'doc': [
            'docutils ~= 0.22',

            'markdown-it-py ~= 4.0',
            'mdit-py-plugins ~= 0.5',

            'pygments ~= 2.19',
        ],

        'mypy': [
            'mypy ~= 1.19',
        ],

        'prof': [
            'gprof2dot ~= 2025.4',
        ],

        'qr': [
            'segno ~= 1.6',
        ],

        'tui': [
            'rich ~= 14.2',
            'textual ~= 6.11',  # [syntax]
            'textual-dev ~= 1.8',
            'textual-speedups ~= 0.2',
        ],
    }

    entry_points = {
        'omlish.manifests': {name: name},
    }

    cli_scripts = {
        'om': f'{name}.cli.main:_main',
    }


class Setuptools(SetuptoolsBase):
    cext = True
    rs = True

    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
