"""
https://nginx.org/en/docs/dev/development_guide.html
https://nginx.org/en/docs/dev/development_guide.html#config_directives
https://nginx.org/en/docs/example.html

https://github.com/yandex/gixy

"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.text.indent import IndentWriter


@dc.dataclass()
class Items(lang.Final):
    lst: list['Item']


@dc.dataclass()
class Item(lang.Final):
    name: str
    args: list[str] | None = None
    block: Items | None = None


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
        for e in obj.lst:
            render(wr, e)

    else:
        raise TypeError(obj)


def _main():
    conf = Items([
        Item('user', ['www', 'www']),
        Item('worker_processes', ['2']),
        Item('events', block=Items([
            Item('worker_connections', ['2000']),
        ])),
    ])

    wr = IndentWriter()
    render(wr, conf)
    print(wr.getvalue())


if __name__ == '__main__':
    _main()
