import dataclasses as dc
import os.path
import typing as ta

import yaml

from omdev.cache import data as dcache
from omlish import check
from omlish import lang
from omlish import marshal as msh

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
@msh.update_object_metadata(unknown_field='x')
class YtsItem:
    name: str | None = None

    from_: str | None = dc.field(default=None, metadata={msh.FieldMetadata: msh.FieldMetadata(name='from')})
    tags: str | None = None

    fail: bool = False

    yaml: str | None = None
    json: str | None = None

    x: ta.Mapping[str, ta.Any] | None = None


def test_spec() -> None:
    for yts_f in get_yts_files():
        with open(yts_f) as f:
            src = f.read()

        doc = yaml.safe_load(src)  # noqa
        items: list[YtsItem] = msh.unmarshal(doc, list[YtsItem])

        for item in items:
            print(yts_f)

            try:
                obj, err = parsing.parse_str(  # noqa
                    check.non_empty_str(item.yaml),
                    parsing.ParseMode(0),
                )

                if err:
                    if item.fail:
                        print(f'SUCCESS: {err}')
                    else:
                        print(f'FAILURE: {err}')
                else:  # noqa
                    if not item.fail:
                        print(f'SUCCESS: {obj}')
                    else:
                        print(f'FAILURE: {obj}')

            except Exception as e:  # noqa
                print(f'ERROR: {e}')
                # raise
