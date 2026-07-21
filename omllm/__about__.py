from omcore.__about__ import ProjectBase
from omcore.__about__ import SetuptoolsBase
from omcore.__about__ import __version__


class Project(ProjectBase):
    name = 'omllm'
    description = 'omllm'

    dependencies = [
        f'omcore == {__version__}',
    ]

    optional_dependencies = {
        'omdev': [
            f'omdev == {__version__}',
        ],

        'huggingface': [
            'huggingface-hub ~= 1.24',
        ],
    }

    entry_points = {
        'omcore.manifests': {name: name},
    }


class Setuptools(SetuptoolsBase):
    find_packages = {
        'include': [Project.name, f'{Project.name}.*'],
        'exclude': [*SetuptoolsBase.find_packages['exclude']],
    }
