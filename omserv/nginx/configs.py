"""
TODO:
 - omnibus/jmespath

https://nginx.org/en/docs/dev/development_guide.html
https://nginx.org/en/docs/dev/development_guide.html#config_directives
https://nginx.org/en/docs/example.html

https://github.com/yandex/gixy
"""
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang
from omlish.text.indent import IndentWriter


@dc.dataclass()
class Items(lang.Final):
    lst: list['Item']

    @classmethod
    def of(cls, obj: ta.Any) -> 'Items':
        if isinstance(obj, Items):
            return obj
        return cls([Item.of(e) for e in check.isinstance(obj, list)])


@dc.dataclass()
class Item(lang.Final):
    name: str
    args: list[str] | None = None
    block: Items | None = None

    @classmethod
    def of(cls, obj: ta.Any) -> 'Item':
        if isinstance(obj, Item):
            return obj
        args = check.isinstance(obj, tuple)
        name, args = check.isinstance(args[0], str), args[1:]
        if args and not isinstance(args[-1], str):
            block, args = Items.of(args[-1]), args[:-1]
        else:
            block = None
        return Item(name, [check.isinstance(e, str) for e in args], block=block)


def render(wr: IndentWriter, obj: ta.Any) -> None:
    if isinstance(obj, Item):
        wr.write(obj.name)
        for e in obj.args or ():
            wr.write(' ')
            wr.write(e)
        if obj.block:
            wr.write(' {\n')
            with wr.indent():
                render(wr, obj.block)
            wr.write('}\n')
        else:
            wr.write(';\n')

    elif isinstance(obj, Items):
        for e2 in obj.lst:
            render(wr, e2)

    else:
        raise TypeError(obj)


def _main() -> None:
    conf = Items.of([
        ('user', 'www', 'www'),
        ('worker_processes', '2'),
        ('events', [
            ('worker_connections', '2000'),
        ]),
    ])

    wr = IndentWriter()
    render(wr, conf)
    print(wr.getvalue())


if __name__ == '__main__':
    _main()
