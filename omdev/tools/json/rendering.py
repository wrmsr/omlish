import dataclasses as dc
import json
import typing as ta

from omlish import lang
from omlish.formats.json.rendering import JsonRenderer
from omlish.formats.json.stream.parsing import Event
from omlish.formats.json.stream.rendering import StreamJsonRenderer
from omlish.formats.json5.rendering import Json5Renderer
from omlish.term import codes as tc


##


@dc.dataclass(frozen=True, kw_only=True)
class RenderingOptions:
    indent: int | str | None = None
    separators: tuple[str, str] | None = None
    sort_keys: bool = False
    raw: bool = False
    unicode: bool = False
    color: bool = False
    five: bool = False
    softwrap_length: int | None = None


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
        return tc.SGR(tc.SGRs.FG.BRIGHT_BLUE), tc.SGR(tc.SGRs.RESET)
    elif isinstance(o, str):
        return tc.SGR(tc.SGRs.FG.GREEN), tc.SGR(tc.SGRs.RESET)
    else:
        return '', ''


##


class EagerRenderer(Renderer):
    def render(self, v: ta.Any) -> str:
        if self._opts.raw:
            if not isinstance(v, str):
                raise TypeError(f'Raw output must be strings, got {type(v)}', v)

            return v

        elif self._opts.five:
            return Json5Renderer.render_str(
                v,
                **self._kw,
                **(dict(style=term_color) if self._opts.color else {}),
                multiline_strings=True,
                softwrap_length=self._opts.softwrap_length,
            )

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

    def render(self, e: Event) -> ta.Iterator[str]:
        return self._renderer.render((e,))
