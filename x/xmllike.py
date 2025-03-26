import io
import typing as ta

from omlish import lang
from omlish.funcs.genmachine import GenMachine


##


class XmlLikeParser(GenMachine[str, 'XmlLikeParser.Output']):
    class Output(lang.Abstract, lang.Sealed):
        pass

    class IdleOutput(Output):
        pass

    def __init__(self) -> None:
        super().__init__(self._do_main())

        self._stack: list[dict[str, str]] = []

    def _char_in(self, c: str) -> str:
        if c and len(c) != 1:
            raise ValueError(c)

        return c

    def _do_main(self):
        while True:
            c = self._char_in((yield None))  # noqa

            if c == '<':
                c = self._char_in((yield None))  # noqa

                if c == '/':
                    return self._do_tag('close')
                else:
                    return self._do_tag('open', c)

    def _do_tag(
            self,
            mode: ta.Literal['open', 'close'],
            prefix: str = '',
    ):
        sb = io.StringIO()
        if prefix:
            sb.write(prefix)

        while True:
            c = self._char_in((yield None))  # noqa

            if c == '>':
                break

            sb.write(c)

        t = sb.getvalue()
        return self._do_main()


##


def _main() -> None:
    p = XmlLikeParser()
    for c in 'abcd<tools><tool>efg</tool><tool>hij</tool></tools>':
        for o in p(c):
            print(o)


if __name__ == '__main__':
    _main()
