import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.specs import jsonschema as js


##


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaCodeGenConfig(lang.Final):
    generated_marker: bool = True
    strict: bool = True
    allow_any_fallbacks: bool = False

    allow_unknown_x: bool = True
    allowed_unknown_tags: ta.AbstractSet[str] = frozenset({'discriminator'})

    ignored_keyword_types: ta.AbstractSet[type[js.Keyword]] = frozenset({
        js.Description,
        js.Title,
        js.Format,
        js.Maximum,
        js.ExclusiveMaximum,
        js.Minimum,
        js.ExclusiveMinimum,
        js.MaxItems,
        js.MinItems,
        js.UniqueItems,
    })
