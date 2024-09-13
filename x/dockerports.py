import os.path
import typing as ta

from omlish import check
from omlish import lang
from omlish.formats import yaml


def _main():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    docker_dir = os.path.join(base_dir, 'docker')
    yml_file = os.path.join(docker_dir, 'compose.yml')

    with open(yml_file) as f:
        yml_src = f.read()

    with lang.disposing(yaml.WrappedLoaders.base(yml_src)) as loader:
        val = check.not_none(loader.get_single_data())
        root = check.isinstance(val.value, ta.Mapping)
        services = check.isinstance(check.single(v.value for k, v in root.items() if k.value == 'services'), ta.Mapping)
        print(services)


if __name__ == '__main__':
    _main()
