from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'omxtra'
    description = 'omxtra'

    dependencies = [
        f'omlish == {__version__}',
    ]

    optional_dependencies: dict = {
        'omdev': [
            f'omdev == {__version__}',
        ],

        'ssh': [
            'paramiko ~= 5.0',  # !! LGPL

            'asyncssh ~= 2.24',  # cffi
        ],
    }

    entry_points = {
        'omlish.manifests': {name: name},
    }


class Setuptools(SetuptoolsBase):
    cext = True

    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
