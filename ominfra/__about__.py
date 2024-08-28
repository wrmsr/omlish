from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'ominfra'
    description = 'ominfra'

    dependencies = [
        f'omlish == {__version__}',
    ]

    optional_dependencies = {
        'ssh': [
            'paramiko >= 3.4',  # !! LGPL

            'asyncssh >= 2.16; python_version < "3.13"',  # cffi
        ],
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
