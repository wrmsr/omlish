"""
TODO:
 - options lol - csv header, newline, etc
"""
import dataclasses as dc
import enum
import json
import typing as ta

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

else:
    ast = lang.proxy_import('ast')
    csv = lang.proxy_import('csv')
    tomllib = lang.proxy_import('tomllib')

    yaml = lang.proxy_import('yaml')

    dotenv = lang.proxy_import('omlish.formats.dotenv')
    json5 = lang.proxy_import('omlish.formats.json5')
    props = lang.proxy_import('omlish.formats.props')
    xml = lang.proxy_import('omlish.formats.xml')


##


@dc.dataclass(frozen=True)
class Format:
    names: ta.Sequence[str]
    load: ta.Callable[[ta.TextIO], ta.Any]


class Formats(enum.Enum):
    JSON = Format(['json'], json.load)

    JSON5 = Format(['json5'], lambda f: json5.loads(f.read()))

    YAML = Format(['yaml', 'yml'], lambda f: yaml.safe_load(f))

    TOML = Format(['toml'], lambda f: tomllib.loads(f.read()))

    ENV = Format(['env', 'dotenv'], lambda f: dotenv.dotenv_values(stream=f))

    PROPS = Format(['properties', 'props'], lambda f: dict(props.Properties().load(f.read())))

    PY = Format(['py', 'python', 'repr'], lambda f: ast.literal_eval(f.read()))

    XML = Format(['xml'], lambda f: xml.build_simple_element(xml.parse_tree(f.read()).getroot()).se_dict())

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
