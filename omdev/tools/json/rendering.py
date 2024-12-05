import dataclasses as dc
import json
import typing as ta

from omlish import lang
from omlish import term
from omlish.formats.json.render import JsonRenderer
from omlish.formats.json.stream.parse import JsonStreamParserEvent
from omlish.formats.json.stream.render import StreamJsonRenderer


##


@dc.dataclass(frozen=True, kw_only=True)
class RenderingOptions:
    indent: int | str | None = None
    separators: tuple[str, str] | None = None
    sort_keys: bool = False
    raw: bool = False
    unicode: bool = False
    color: bool = False


def make_render_kwargs(opts: RenderingOptions) -> ta.Mapping[str, ta.Any]:
    return dict(
        indent=opts.indent,
        separators=opts.separators,
        sort_keys=opts.sort_keys,
        ensure_ascii=not opts.unicode,
    )


class Renderer(lang.Abstract):
    def __init__(self, opts: RenderingOptions) -> None:
        super().__init__()
        self._opts = opts
        self._kw = make_render_kwargs(opts)


##


def term_color(o: ta.Any, state: JsonRenderer.State) -> tuple[str, str]:
    if state is JsonRenderer.State.KEY:
        return term.SGR(term.SGRs.FG.BRIGHT_BLUE), term.SGR(term.SGRs.RESET)
    elif isinstance(o, str):
        return term.SGR(term.SGRs.FG.GREEN), term.SGR(term.SGRs.RESET)
    else:
        return '', ''


##


class EagerRenderer(Renderer):
    def render(self, v: ta.Any) -> str:
        if self._opts.raw:
            if not isinstance(v, str):
                raise TypeError(f'Raw output must be strings, got {type(v)}', v)

            return v

        elif self._opts.color:
            return JsonRenderer.render_str(
                v,
                **self._kw,
                style=term_color,
            )

        else:
            return json.dumps(
                v,
                **self._kw,
            )


##


class StreamRenderer(Renderer):
    def __init__(self, opts: RenderingOptions) -> None:
        super().__init__(opts)

        self._renderer = StreamJsonRenderer(
            style=term_color if self._opts.color else None,
            delimiter='\n',
            **self._kw,
        )

    def render(self, e: JsonStreamParserEvent) -> ta.Generator[str, None, None]:
        return self._renderer.render((e,))
