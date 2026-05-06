import typing as ta

from omlish import check
from omlish.formats import json
from omlish.formats import json5
from omlish.formats.json import JsonRenderer

from .text import CanUiText
from .text import StyleUiText
from .text import UiText
from .text import UiTextStyle


##


class _StyleRendererOut:
    def __init__(self) -> None:
        super().__init__()

        self._stack: list[tuple[_StyleRendererOut.Op | None, list[CanUiText]]] = [(None, [])]

    class Op(ta.NamedTuple):  # noqa
        mode: ta.Literal['open', 'close']
        item: ta.Literal['key', 'str']

    @classmethod
    def style(cls, o: ta.Any, state: JsonRenderer.State) -> tuple[ta.Any, ta.Any] | None:
        if state is JsonRenderer.State.KEY:
            return (cls.Op('open', 'key'), cls.Op('close', 'key'))
        elif isinstance(o, str):
            return (cls.Op('open', 'str'), cls.Op('close', 'str'))
        else:
            return None

    def write(self, s: ta.Any) -> None:
        if isinstance(s, self.Op):
            if s.mode == 'open':
                self._stack.append((s, []))

            elif s.mode == 'close':
                (op, lst) = self._stack.pop()
                check.state(check.not_none(op).item == s.item)

                match s.item:
                    case 'key':
                        sty = UiTextStyle(color='blue')
                    case 'str':
                        sty = UiTextStyle(color='green')
                    case _:
                        raise ValueError(s.item)

                tx = StyleUiText(
                    UiText.of(*lst),
                    sty,
                )

                self._stack[-1][1].append(tx)

            else:
                raise ValueError(s.mode)

        elif isinstance(s, str):
            self._stack[-1][1].append(s)

        else:
            raise TypeError(s)

    def build(self) -> UiText:
        (op, lst) = check.single(self._stack)
        check.none(op)
        return UiText.of(*lst)


def render_json_ui_text(
        obj: ta.Any,
        *,
        mode: ta.Literal['pretty', 'compact', None] = None,
        five: bool = False,
        multiline_strings: bool = False,
) -> UiText:
    cls: ta.Any
    if five:
        cls = json5.Json5Renderer
    else:
        cls = JsonRenderer

    kw: dict[str, ta.Any] = {}
    match mode:
        case 'pretty':
            kw.update(json.PRETTY_KWARGS)
        case 'compact':
            kw.update(json.COMPACT_KWARGS)
        case None:
            pass
        case _:
            raise ValueError(mode)

    if multiline_strings:
        check.arg(five)
        kw.update(multiline_strings=True)

    out = _StyleRendererOut()
    kw.update(style=out.style)

    cls(out, **kw).render(obj)

    return out.build()
