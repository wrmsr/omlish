# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
See:
 - https://nginx.org/en/docs/dev/development_guide.html
 - https://nginx.org/en/docs/dev/development_guide.html#config_directives
 - https://nginx.org/en/docs/example.html
"""
import collections.abc
import dataclasses as dc
import typing as ta

from ..lite.check import check
from ..text.indent import IndentWriter


##


@dc.dataclass()
class NginxConfigItems:
    lst: ta.List['NginxConfigItem']

    @classmethod
    def of(cls, obj: ta.Any) -> 'NginxConfigItems':
        if isinstance(obj, NginxConfigItems):
            return obj
        return cls([NginxConfigItem.of(e) for e in check.isinstance(obj, list)])


@dc.dataclass()
class NginxConfigItem:
    name: str
    args: ta.Optional[ta.List[str]] = None
    block: ta.Optional[NginxConfigItems] = None

    @classmethod
    def of(cls, obj: ta.Any) -> 'NginxConfigItem':
        if isinstance(obj, NginxConfigItem):
            return obj
        args = check.isinstance(check.not_isinstance(obj, str), collections.abc.Sequence)
        name, args = check.isinstance(args[0], str), args[1:]
        if args and not isinstance(args[-1], str):
            block, args = NginxConfigItems.of(args[-1]), args[:-1]
        else:
            block = None
        return NginxConfigItem(name, [check.isinstance(e, str) for e in args], block=block)


def render_nginx_config(wr: IndentWriter, obj: ta.Any) -> None:
    if isinstance(obj, NginxConfigItem):
        wr.write(obj.name)
        for e in obj.args or ():
            wr.write(' ')
            wr.write(e)
        if obj.block:
            wr.write(' {\n')
            with wr.indent():
                render_nginx_config(wr, obj.block)
            wr.write('}\n')
        else:
            wr.write(';\n')

    elif isinstance(obj, NginxConfigItems):
        for e2 in obj.lst:
            render_nginx_config(wr, e2)

    else:
        raise TypeError(obj)


def render_nginx_config_str(obj: ta.Any) -> str:
    iw = IndentWriter()
    render_nginx_config(iw, obj)
    return iw.getvalue()
