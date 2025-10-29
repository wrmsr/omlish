from omlish.__about__ import ProjectBase
from omlish.__about__ import SetuptoolsBase
from omlish.__about__ import __version__


class Project(ProjectBase):
    name = 'omextra'
    description = 'omextra'

    dependencies = [
        # FIXME: text.antlr.cli deps omdev.cache.data, yet this lib is 'under' omdev.
        # f'omdev == {__version__}',

        f'omlish == {__version__}',
    ]

    optional_dependencies: dict = {
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
