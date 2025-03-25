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

    def _do_main(self):
        while True:
            c = yield None  # noqa

            if c and len(c) != 1:
                raise ValueError(c)

            yield [self.IdleOutput()]


##


def _main() -> None:
    p = XmlLikeParser()
    for c in 'abcd<tool>efg</tool>':
        for o in p(c):
            print(o)


if __name__ == '__main__':
    _main()
