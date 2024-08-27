from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'ommlx'
    description = 'ommlx'

    dependencies = [
        f'omlish == {__version__}',
    ]

    optional_dependencies = {
        'torch': [
            'torch >= 2.4',
        ],
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
