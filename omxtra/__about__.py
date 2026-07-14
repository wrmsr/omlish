from omcore.__about__ import ProjectBase
from omcore.__about__ import SetuptoolsBase
from omcore.__about__ import __version__


class Project(ProjectBase):
    name = 'omxtra'
    description = 'omxtra'

    dependencies = [
        f'omcore == {__version__}',
    ]

    optional_dependencies: dict = {
        'omdev': [
            f'omdev == {__version__}',
        ],

        'async': [
            'greenlet ~= 3.5',
        ],

        'ssh': [
            'paramiko ~= 5.0',  # !! LGPL

            'asyncssh ~= 2.24',  # cffi
        ],

        'wiki': [
            'mwparserfromhell ~= 0.7',

            'wikitextparser ~= 1.0',  # !! GPL
        ],
    }

    entry_points = {
        'omcore.manifests': {name: name},
    }


class Setuptools(SetuptoolsBase):
    cext = True

    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
