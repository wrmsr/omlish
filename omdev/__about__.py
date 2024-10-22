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
            'black ~= 24.10',
        ],

        'c': [
            'pycparser ~= 2.22',
            'cffi ~= 1.17',
            'pcpp ~= 1.30',
        ],

        'docutils': [
            'docutils ~= 0.21',
        ],

        'mypy': [
            'mypy ~= 1.11',
        ],

        'prof': [
            'gprof2dot ~= 2024.6',
        ],

        'tokens': [
            'tokenize_rt ~= 6.1',
        ],

        'wheel': [
            'wheel ~= 0.44',
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
