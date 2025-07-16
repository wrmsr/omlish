from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, eq=False)
@dc.extra_class_params(repr_id=True)
class ContentPlaceholder(lang.Final):
    # kw_only to prevent misuse - the string passed to this class is not the Content itself, just the name of the
    # placeholder
    name: str | None = dc.field(default=None, kw_only=True, metadata=dc.extra_field_params(repr_fn=lang.opt_repr))


content_placeholder = ContentPlaceholder


class ContentPlaceholderMarker(lang.Marker):
    pass
