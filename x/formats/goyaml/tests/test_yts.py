import dataclasses as dc
import os.path
import typing as ta

from omdev.cache import data as dcache
from omlish import lang

from .. import parsing


##


YDS_DATA = dcache.GitSpec(
    'https://github.com/yaml/yaml-test-suite/',
    rev='ccfa74e56afb53da960847ff6e6976c0a0825709',
    subtrees=[
        'src/',
    ],
)


@lang.cached_function
def get_yts_files() -> ta.Sequence[str]:
    yts_data_dir = dcache.default().get(YDS_DATA)
    src_dir = os.path.join(yts_data_dir, 'src')
    return sorted(
        os.path.join(root, f)
        for root, dirs, files in os.walk(src_dir)
        for f in files
        if f.split('.')[-1] in ('yml', 'yaml')
    )


@dc.dataclass(frozen=True)
class YtsItem:
    name: str
    from_: str
    tags: str
    fail: bool
    yaml: str
    tree: str


def test_spec() -> None:
    for yts_f in get_yts_files():
        with open(yts_f) as f:
            src = f.read()

        # doc = yaml.safe_load(src)  # noqa

        obj, err = parsing.parse_str(
            src,
            parsing.ParseMode(0),
        )

        print(obj)
        print(repr(obj))
