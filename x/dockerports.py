import os.path

from omlish import lang
from omlish.formats import yaml


def _main():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    docker_dir = os.path.join(base_dir, 'docker')
    yml_file = os.path.join(docker_dir, 'compose.yml')

    with open(yml_file) as f:
        yml_src = f.read()

    with lang.disposing(yaml.WrappedLoaders.base(yml_src)) as loader:
        while loader.check_data():
            val = loader.get_data()
            print(val)


if __name__ == '__main__':
    _main()
