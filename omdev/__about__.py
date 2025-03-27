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

            'cffi ~= 1.17',
        ],

        'doc': [
            'docutils ~= 0.21',

            'markdown ~= 3.7',
        ],

        'mypy': [
            'mypy ~= 1.15',
        ],

        'prof': [
            'gprof2dot ~= 2024.6',
        ],

        'ptk': [
            'prompt-toolkit ~= 3.0',
        ],

        'qr': [
            'segno ~= 1.6',
        ],

        'wheel': [
            'wheel ~= 0.45',
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
