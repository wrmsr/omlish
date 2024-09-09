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

        'tokens': [
            'tokenize_rt ~= 6.0',
        ],

        'wheel': [
            'wheel ~= 0.44',
        ],
    }


class Setuptools(SetuptoolsBase):
    cexts = True

    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
