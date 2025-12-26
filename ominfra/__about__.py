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
        'omdev': [
            f'omdev == {__version__}',
        ],

        'ssh': [
            'paramiko ~= 4.0',  # !! LGPL

            'asyncssh ~= 2.22',  # cffi
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
