"""
TODO:
 - options lol - csv header, newline, etc
 - edn
"""
import dataclasses as dc
import enum
import json
import typing as ta

from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import ast
    import csv
    import tomllib

    import yaml

    from omlish.formats import dotenv
    from omlish.formats import json5
    from omlish.formats import props
    from omlish.formats import xml
    from omlish.formats.json import stream as json_stream
    from omlish.formats.json5 import parsing as json5_parsing

else:
    ast = lang.proxy_import('ast')
    csv = lang.proxy_import('csv')
    tomllib = lang.proxy_import('tomllib')

    yaml = lang.proxy_import('yaml')

    dotenv = lang.proxy_import('omlish.formats.dotenv')
    json5 = lang.proxy_import('omlish.formats.json5')
    props = lang.proxy_import('omlish.formats.props')
    xml = lang.proxy_import('omlish.formats.xml')
    json_stream = lang.proxy_import('omlish.formats.json.stream')
    json5_parsing = lang.proxy_import('omlish.formats.json5.parsing')


##


@dc.dataclass(frozen=True)
class Format:
    names: ta.Sequence[str]
    load: ta.Callable[[ta.TextIO], ta.Any]


def _load_jsons(f: ta.TextIO) -> list[ta.Any]:
    return list(json_stream.stream_parse_values(f.read()))


def _load_json5s(f: ta.TextIO) -> list[ta.Any]:
    return list(json5_parsing.parse_many(f.read()))


def _load_xml(f: ta.TextIO) -> dict[str, ta.Any]:
    tree = xml.parse_tree(f.read())
    sel = xml.build_simple_element(check.not_none(tree.getroot()))
    return sel.se_dict()


class Formats(enum.Enum):
    JSON = Format(['json'], json.load)

    JSON5 = Format(['json5'], lambda f: json5.loads(f.read()))

    JSON_STREAM = Format(['jsons'], lambda f: _load_jsons(f))
    JSON5_STREAM = Format(['json5s'], lambda f: _load_json5s(f))

    YAML = Format(['yaml', 'yml'], lambda f: yaml.safe_load(f))

    TOML = Format(['toml'], lambda f: tomllib.loads(f.read()))

    ENV = Format(['env', 'dotenv'], lambda f: dotenv.dotenv_values(stream=f))

    PROPS = Format(['properties', 'props'], lambda f: dict(props.Properties().load(f.read())))

    PY = Format(['py', 'python', 'repr'], lambda f: ast.literal_eval(f.read()))

    XML = Format(['xml'], _load_xml)

    CSV = Format(['csv'], lambda f: list(csv.DictReader(f)))
    TSV = Format(['tsv'], lambda f: list(csv.DictReader(f, delimiter='\t')))
    FLAT_CSV = Format(['fcsv'], lambda f: list(csv.reader(f)))
    FLAT_TSV = Format(['ftsv'], lambda f: list(csv.reader(f, delimiter='\t')))


FORMATS_BY_NAME: ta.Mapping[str, Format] = {
    n: f
    for e in Formats
    for f in [e.value]
    for n in f.names
}
