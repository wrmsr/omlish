import os.path

import yaml

from .. import parsing


def _test_parsing(src: str) -> None:
    doc = yaml.safe_load(src)  # noqa

    obj = parsing.parse_str(
        src,
        parsing.ParseMode(0),
    )

    print(obj)
    print(repr(obj))


def test_parsing_sample():
    with open(os.path.join(os.path.dirname(__file__), 'sample.yaml')) as f:
        src = f.read()
    _test_parsing(src)


def test_parsing_docker_compose():
    with open('docker/compose.yml') as f:
        src = f.read()
    _test_parsing(src)
