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
        'c': [
            'pycparser >= 2.22',
            'cffi >= 1.17',
            'pcpp >= 1.30',
        ],

        'mypy': [
            'mypy >= 1.11',
        ],

        'tokens': [
            'tokenize_rt >= 6',
        ],
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
