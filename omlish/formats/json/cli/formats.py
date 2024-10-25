"""
TODO:
 - options lol - csv header, newline, etc
"""
import dataclasses as dc
import enum
import json
import typing as ta

from .... import lang


if ta.TYPE_CHECKING:
    import ast
    import csv
    import tomllib

    import yaml

    from ... import dotenv
    from ... import props
    from ... import xml

else:
    ast = lang.proxy_import('ast')
    csv = lang.proxy_import('csv')
    tomllib = lang.proxy_import('tomllib')

    yaml = lang.proxy_import('yaml')

    dotenv = lang.proxy_import('...dotenv', __package__)
    props = lang.proxy_import('...props', __package__)
    xml = lang.proxy_import('...xml', __package__)


##


@dc.dataclass(frozen=True)
class Format:
    names: ta.Sequence[str]
    load: ta.Callable[[ta.TextIO], ta.Any]


class Formats(enum.Enum):
    JSON = Format(['json'], json.load)
    YAML = Format(['yaml', 'yml'], lambda f: yaml.safe_load(f))
    TOML = Format(['toml'], lambda f: tomllib.loads(f.read()))
    ENV = Format(['env', 'dotenv'], lambda f: dotenv.dotenv_values(stream=f))
    PROPS = Format(['properties', 'props'], lambda f: dict(props.Properties().load(f.read())))
    PY = Format(['py', 'python', 'repr'], lambda f: ast.literal_eval(f.read()))
    XML = Format(['xml'], lambda f: xml.build_simple_element(xml.parse_tree(f.read()).getroot()).as_dict())
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
