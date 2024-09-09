"""
TODO:
 - embed pip._internal.req.parse_requirements, add additional env stuff? breaks compat with raw pip
"""
# ruff: noqa: UP007
import os.path
import tempfile
import typing as ta

from omlish.lite.cached import cached_nullary


class RequirementsRewriter:
    def __init__(
            self,
            venv: ta.Optional[str] = None,
    ) -> None:
        super().__init__()
        self._venv = venv

    @cached_nullary
    def _tmp_dir(self) -> str:
        return tempfile.mkdtemp('-omlish-reqs')

    VENV_MAGIC = '# @omdev-venv'

    def rewrite_file(self, in_file: str) -> str:
        with open(in_file) as f:
            src = f.read()

        in_lines = src.splitlines(keepends=True)
        out_lines = []

        for l in in_lines:
            if self.VENV_MAGIC in l:
                lp, _, rp = l.partition(self.VENV_MAGIC)
                rp = rp.partition('#')[0]
                omit = False
                for v in rp.split():
                    if v[0] == '!':
                        if self._venv is not None and self._venv == v[1:]:
                            omit = True
                            break
                    else:
                        raise NotImplementedError

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
