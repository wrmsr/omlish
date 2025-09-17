"""
TODO:
 - embed pip._internal.req.parse_requirements, add additional env stuff? breaks compat with raw pip
"""
# ruff: noqa: UP007 UP045
import os.path
import re
import tempfile
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.logs.modules import get_module_logger

from ..packaging.requires import RequiresParserSyntaxError
from ..packaging.requires import parse_requirement


log = get_module_logger(globals())  # noqa


##


class RequirementsRewriter:
    def __init__(
            self,
            *,
            venv: ta.Optional[str] = None,
            only_pats: ta.Optional[ta.Sequence[re.Pattern]] = None,
    ) -> None:
        super().__init__()

        self._venv = venv
        self._only_pats = only_pats

    @cached_nullary
    def _tmp_dir(self) -> str:
        return tempfile.mkdtemp('-omlish-reqs')

    VENV_MAGIC = '# @omlish-venv'

    def rewrite_file(self, in_file: str) -> str:
        with open(in_file) as f:
            src = f.read()

        in_lines = src.splitlines(keepends=True)
        out_lines = []

        for l in in_lines:
            if l.split('#')[0].strip():
                omit = False

                if self.VENV_MAGIC in l:
                    lp, _, rp = l.partition(self.VENV_MAGIC)
                    rp = rp.partition('#')[0]
                    for v in rp.split():
                        if v[0] == '!':
                            if self._venv is not None and self._venv == v[1:]:
                                omit = True
                                break
                        else:
                            raise NotImplementedError

                if (
                        not omit and
                        (ops := self._only_pats) is not None and
                        not l.strip().startswith('-')
                ):
                    try:
                        pr = parse_requirement(l.split('#')[0].strip())
                    except RequiresParserSyntaxError:
                        pass
                    else:
                        if not any(op.fullmatch(pr.name) for op in ops):
                            omit = True

                if omit:
                    out_lines.append('# OMITTED:  ' + l)
                    continue

            out_req = self.rewrite(l.rstrip('\n'), for_file=True)
            out_lines.append(out_req + '\n')

        out_file = os.path.join(self._tmp_dir(), os.path.basename(in_file))
        if os.path.exists(out_file):
            raise Exception(f'file exists: {out_file}')

        with open(out_file, 'w') as f:
            f.write(''.join(out_lines))
        log.info('Rewrote requirements file %s to %s', in_file, out_file)
        return out_file

    def rewrite(self, in_req: str, *, for_file: bool = False) -> str:
        if in_req.strip().startswith('-r'):
            l = in_req.strip()
            lp, _, rp = l.partition(' ')
            if lp == '-r':
                inc_in_file, _, rest = rp.partition(' ')
            else:
                inc_in_file, rest = lp[2:], rp

            inc_out_file = self.rewrite_file(inc_in_file)
            if for_file:
                return ' '.join(['-r ', inc_out_file, rest])
            else:
                return '-r' + inc_out_file

        else:
            return in_req
