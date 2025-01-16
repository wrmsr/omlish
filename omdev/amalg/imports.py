import dataclasses as dc
import os.path
import typing as ta

from omlish import check

from ..tokens import all as tks


##


@dc.dataclass(frozen=True, kw_only=True)
class Import:
    mod: str
    item: str | None
    as_: str | None

    src_path: str
    line: int

    mod_path: str | None

    toks: tks.Tokens = dc.field(repr=False)


def make_import(
        lts: tks.Tokens,
        *,
        src_path: str,
        mounts: ta.Mapping[str, str],
) -> Import | None:
    if not lts:
        return None
    ft = lts[0]

    if ft.name != 'NAME' or ft.src not in ('import', 'from'):
        return None

    ml = []
    il: list[str] | None = None
    as_ = None
    for tok in (it := iter(tks.ignore_ws(lts[1:]))):
        if tok.name in ('NAME', 'OP'):
            if tok.src == 'as':
                check.none(as_)
                nt = next(it)
                check.equal(nt.name, 'NAME')
                as_ = nt.src
            elif tok.src == 'import':
                check.equal(ft.src, 'from')
                il = []
            elif il is not None:
                il.append(tok.src)
            else:
                ml.append(tok.src)
        else:
            raise Exception(tok)

    mod = ''.join(ml)
    item = ''.join(il) if il is not None else None

    if (mnt := mounts.get(mod.partition('.')[0])) is not None:
        ps = mod.split('.')
        mod_path = os.path.abspath(os.path.join(
            mnt,
            *ps[1:-1],
            ps[-1] + '.py',
        ))

    elif not mod.startswith('.'):
        mod_path = None

    else:
        parts = mod.split('.')
        nd = len(parts) - parts[::-1].index('')
        mod_path = os.path.abspath(os.path.join(
            os.path.dirname(src_path),
            '../' * (nd - 1),
            *parts[nd:-1],
            parts[-1] + '.py',
        ))

        mod = check.isinstance(mod_path, str)

    return Import(
        mod=mod,
        item=item,
        as_=as_,

        src_path=src_path,
        line=check.not_none(ft.line),

        mod_path=mod_path,

        toks=lts,
    )
