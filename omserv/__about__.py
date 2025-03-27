from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'omserv'
    description = 'omserv'

    dependencies = [
        f'omlish == {__version__}',
    ]

    optional_dependencies = {
        'server': [
            'h11 ~= 0.14',
            'h2 ~= 4.2',
            'priority ~= 2.0',
            'wsproto ~= 1.2',
        ],

        'templates': [
            'jinja2 ~= 3.1',
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
