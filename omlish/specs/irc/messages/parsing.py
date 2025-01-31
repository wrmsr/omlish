import typing as ta

from .... import dataclasses as dc
from .base import Message
from .formats import MessageFormat


##


class ParseError(Exception):
    pass


def parse_message(cls: type[Message], params: ta.Sequence[str]) -> Message:
    mf = cls.FORMAT

    kws: dict = {}
    i = 0
    for fp in mf.params:
        if isinstance(fp, MessageFormat.KwargParam):
            if i >= len(params):
                if not fp.optional:
                    raise ParseError(f'Missing param: {fp.name}')
                continue

            kv: ta.Any
            if (ar := fp.arity) is MessageFormat.KwargParam.Arity.SINGLE:
                kv = params[i]
                i += 1

            elif ar is MessageFormat.KwargParam.Arity.VARIADIC:
                kv = params[i:]
                i = len(params)

            elif ar is MessageFormat.KwargParam.Arity.COMMA_LIST:
                kv = params[i].split(',')
                i += 1

            else:
                raise TypeError(ar)

            kws[fp.name] = kv

        elif isinstance(fp, MessageFormat.LiteralParam):
            if i >= len(params):
                raise ParseError('Missing literal param')

            pv = params[i]
            if fp.text != pv:
                raise ParseError(f'Unexpected literal: {pv}')
            i += 1

        else:
            raise TypeError(fp)

    if i != len(params):
        raise ParseError('Unconsumed params')

    if (up := mf.unpack_params) is not None:
        kws = dict(up(kws))

    return cls(**kws)


##


class UnparsedMessage(ta.NamedTuple):
    name: str
    params: ta.Sequence[str]


def unparse_message(msg: Message) -> UnparsedMessage:
    mf = msg.FORMAT

    kws = {k: v for k, v in dc.asdict(msg).items() if v is not None}

    if (up := mf.unpack_params) is not None:
        kws = dict(up.backward(kws))

    params = []

    for fp in mf.params:
        if isinstance(fp, MessageFormat.KwargParam):
            # FIXME
            raise NotImplementedError

        elif isinstance(fp, MessageFormat.LiteralParam):
            params.append(fp.text)

        else:
            raise TypeError(fp)

    return UnparsedMessage(
        name=mf.name,
        params=params,
    )
