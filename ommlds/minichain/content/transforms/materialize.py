import typing as ta

from omlish import check
from omlish import dispatch
from omlish import lang
from omlish.text import templating as tpl

from ..types import Content
from ..types import ExtendedContent


##


class ContentNamespace(lang.Namespace, lang.Abstract):
    pass


CanContent: ta.TypeAlias = ta.Union[  # noqa
    str,
    ExtendedContent,
    ta.Iterable['CanContent'],
    None,
    type[ContentNamespace],
    tpl.Templater,
]


##


class ContentMaterializer:
    def __init__(
            self,
            *,
            templater_context: tpl.Templater.Context | None = None,
    ) -> None:
        super().__init__()

        self._templater_context = templater_context

    @dispatch.method
    def materialize(self, o: CanContent) -> Content:
        raise TypeError(o)

    #

    @materialize.register
    def materialize_str(self, o: str) -> Content:
        return o

    @materialize.register
    def materialize_extended(self, o: ExtendedContent) -> Content:
        return o

    #

    @materialize.register
    def materialize_iterable(self, o: ta.Iterable) -> Content:
        return [self.materialize(e) for e in o]

    @materialize.register
    def materialize_none(self, o: None) -> Content:
        return []

    #

    def _materialize_namespace_type(self, o: type[ContentNamespace]) -> Content:
        check.issubclass(o, ContentNamespace)

        def rec(v: ta.Any) -> ta.Generator[Content]:
            if isinstance(v, (bytes, bytearray, ta.Mapping)):
                return

            elif isinstance(v, type):
                if issubclass(v, ContentNamespace):
                    for n, e in v:
                        if n.startswith('_'):
                            continue
                        yield from rec(e)

            elif isinstance(v, ta.Iterable):
                for e in v:
                    yield from rec(e)

            else:
                yield self.materialize(v)

        return list(rec(o))

    @materialize.register
    def materialize_type(self, o: type) -> Content:
        if issubclass(o, ContentNamespace):
            return self._materialize_namespace_type(o)
        else:
            raise TypeError(o)

    #

    @materialize.register
    def materialize_templater(self, o: tpl.Templater) -> Content:
        return o.render(check.not_none(self._templater_context))


def materialize_content(
        o: CanContent,
        *,
        templater_context: tpl.Templater.Context | None = None,
) -> Content:
    return ContentMaterializer(
        templater_context=templater_context,
    ).materialize(o)
