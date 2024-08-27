from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'omserv'
    description = 'omserv'

    dependencies = [
        f'omlish == {__version__}'
    ]

    optional_dependencies = {
        'server': [
            'h11 >= 0.14',
            'h2 >= 4.1',
            'priority >= 2',
            'wsproto >= 1.2',
        ],
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': ['omserv', 'omserv.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
