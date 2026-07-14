# ruff: noqa: UP006 UP007 UP045
"""
TODO:
 - -x / --exec - os.exec entrypoint
 - refuse to install non-exec-relevant Bootstraps when chosen
"""
import argparse
import dataclasses as dc
import io
import itertools
import os
import shutil
import sys
import typing as ta

from .. import lang
from .base import Bootstrap
from .harness import BOOTSTRAP_TYPES_BY_NAME
from .harness import bootstrap


with lang.auto_proxy_import(globals()):
    import runpy


##


class _OrderedArgsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if 'ordered_args' not in namespace:
            setattr(namespace, 'ordered_args', [])
        if self.const is not None:
            value = self.const
        else:
            value = values
        namespace.ordered_args.append((self.dest, value))


def _or_opt(ty):
    return (ty, ta.Optional[ty])


def _int_or_str(v):
    try:
        return int(v)
    except ValueError:
        return v


def _add_arguments(parser: argparse.ArgumentParser) -> None:
    # ta.Optional[ta.Mapping[str, ta.Tuple[ta.Optional[int], ta.Optional[int]]]]

    for cname, cls in BOOTSTRAP_TYPES_BY_NAME.items():
        for fld in dc.fields(cls.Config):
            aname = f'--{cname}:{fld.name}'
            kw: ta.Dict[str, ta.Any] = {}

            if fld.type in _or_opt(str):
                pass
            elif fld.type in _or_opt(bool):
                kw.update(const=True, nargs=0)
            elif fld.type in _or_opt(int):
                kw.update(type=int)
            elif fld.type in _or_opt(float):
                kw.update(type=float)
            elif fld.type in _or_opt(ta.Union[int, str]):
                kw.update(type=_int_or_str)

            elif fld.type in (
                    *_or_opt(ta.Sequence[str]),
                    *_or_opt(ta.Mapping[str, ta.Optional[str]]),
                    *_or_opt(ta.Mapping[int, ta.Union[int, str, None]]),
                    *_or_opt(ta.Mapping[str, ta.Tuple[ta.Optional[int], ta.Optional[int]]]),
            ):
                if aname[-1] != 's':
                    raise NameError(aname)
                aname = aname[:-1]

            else:
                raise TypeError(fld)

            parser.add_argument(aname.replace('_', '-'), action=_OrderedArgsAction, **kw)


def _process_arguments(args: ta.Any) -> ta.Sequence[Bootstrap.Config]:
    if not (oa := getattr(args, 'ordered_args', None)):
        return []

    cfgs: ta.List[Bootstrap.Config] = []

    for cname, cargs in [
        (n, list(g))
        for n, g in
        itertools.groupby(oa, key=lambda s: s[0].partition(':')[0])
    ]:
        ccls = BOOTSTRAP_TYPES_BY_NAME[cname].Config
        flds = {f.name: f for f in dc.fields(ccls)}

        kw: ta.Dict[str, ta.Any] = {}
        for aname, aval in cargs:
            k = aname.partition(':')[2]

            if k not in flds:
                k += 's'
                fld = flds[k]

                if fld.type in _or_opt(ta.Sequence[str]):
                    kw.setdefault(k, []).append(aval)

                elif fld.type in _or_opt(ta.Mapping[str, ta.Optional[str]]):
                    if '=' not in aval:
                        kw.setdefault(k, {})[aval] = None
                    else:
                        ek, _, ev = aval.partition('=')
                        kw.setdefault(k, {})[ek] = ev

                elif fld.type in _or_opt(ta.Mapping[int, ta.Union[int, str, None]]):
                    fk, _, fv = aval.partition('=')
                    if not fv:
                        kw.setdefault(k, {})[int(fk)] = None
                    else:
                        kw.setdefault(k, {})[int(fk)] = _int_or_str(fv)

                elif fld.type in _or_opt(ta.Mapping[str, ta.Tuple[ta.Optional[int], ta.Optional[int]]]):
                    fk, _, fv = aval.partition('=')
                    if ',' in fv:
                        tl, tr = fv.split(',')
                    else:
                        tl, tr = None, None
                    kw.setdefault(k, {})[fk] = (_int_or_str(tl) if tl else None, _int_or_str(tr) if tr else None)

                else:
                    raise TypeError(fld)

            else:
                kw[k] = aval

        cfg = ccls(**kw)
        cfgs.append(cfg)

    return cfgs


##


def _main() -> int:
    parser = argparse.ArgumentParser()

    _add_arguments(parser)

    parser.add_argument('-m', '--module', action='store_true')
    parser.add_argument('-c', '--code', action='store_true')
    parser.add_argument('-x', '--exec', action='store_true')
    parser.add_argument('target')
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    if len([a for a in ('module', 'code', 'exec') if getattr(args, a)]) > 1:
        raise Exception('Multiple exec mode specified')

    cfgs = _process_arguments(args)

    with bootstrap(*cfgs):
        tgt = args.target

        if args.exec:
            exe = shutil.which(tgt)
            if exe is None:
                raise FileNotFoundError(exe)

            os.execl(exe, exe, *args.args)

            return 0  # type: ignore  # noqa

        sys.argv = [tgt, *(args.args or ())]

        if args.code:
            exec(tgt, {}, {})

        elif args.module:
            runpy._run_module_as_main(tgt)  # type: ignore  # noqa

        else:
            with io.open_code(tgt) as fp:
                src = fp.read()

            ns = dict(
                __name__='__main__',
                __file__=tgt,
                __builtins__=__builtins__,
                __spec__=None,
            )

            import __main__  # noqa
            __main__.__dict__.clear()
            __main__.__dict__.update(ns)
            exec(compile(src, tgt, 'exec'), __main__.__dict__, __main__.__dict__)

        return 0


if __name__ == '__main__':
    sys.exit(_main())
