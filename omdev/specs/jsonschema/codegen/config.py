import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.specs import jsonschema as jsch


##


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaCodeGenConfig(lang.Final):
    omit_generated_marker: bool = False
    non_strict: bool = False
    allow_any_fallbacks: bool = False

    forbid_unknown_x: bool = False
    allowed_unknown_tags: ta.AbstractSet[str] = frozenset({'discriminator'})

    multiline_threshold: int = 80

    ignored_keyword_types: ta.AbstractSet[type[jsch.Keyword]] = frozenset({
        jsch.Description,
        jsch.Title,
        jsch.Format,
        jsch.Maximum,
        jsch.ExclusiveMaximum,
        jsch.Minimum,
        jsch.ExclusiveMinimum,
        jsch.MaxItems,
        jsch.MinItems,
        jsch.UniqueItems,
    })
