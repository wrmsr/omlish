# ruff: noqa: UP006 UP007 UP045
"""
TODO:
 - verify - systemd-analyze
 - sudo loginctl enable-linger "$USER"
 - idemp kill services that shouldn't be running, start ones that should
  - ideally only those defined by links to deploy home
  - ominfra.systemd / x.sd_orphans
"""
import os.path
import shutil
import sys
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check
from omlish.os.paths import abs_real_path
from omlish.os.paths import is_path_in_dir

from .specs import DeploySystemdSpec
from .tmp import DeployHomeAtomics
from .types import DeployHome


##


class DeploySystemdManager:
    def __init__(
            self,
            *,
            atomics: DeployHomeAtomics,
    ) -> None:
        super().__init__()

        self._atomics = atomics

    def _scan_link_dir(
            self,
            d: str,
            *,
            strict: bool = False,
    ) -> ta.Dict[str, str]:
        o: ta.Dict[str, str] = {}
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if strict:
                check.state(os.path.islink(fp))
            o[f] = abs_real_path(fp)
        return o

    async def sync_systemd(
            self,
            spec: ta.Optional[DeploySystemdSpec],
            home: DeployHome,
            conf_dir: str,
    ) -> None:
        check.non_empty_str(home)

        if not spec:
            return

        #

        if not (ud := spec.unit_dir):
            return

        ud = abs_real_path(os.path.expanduser(ud))

        os.makedirs(ud, exist_ok=True)

        #

        uld = {
            n: p
            for n, p in self._scan_link_dir(ud).items()
            if is_path_in_dir(home, p)
        }

        if os.path.exists(conf_dir):
            cld = self._scan_link_dir(conf_dir, strict=True)
        else:
            cld = {}

        #

        ns = sorted(set(uld) | set(cld))

        for n in ns:
            cl = cld.get(n)
            if cl is None:
                os.unlink(os.path.join(ud, n))
            else:
                with self._atomics(home).begin_atomic_path_swap(  # noqa
                        'file',
                        os.path.join(ud, n),
                        auto_commit=True,
                        skip_root_dir_check=True,
                ) as dst_swap:
                    os.unlink(dst_swap.tmp_path)
                    os.symlink(
                        os.path.relpath(cl, os.path.dirname(dst_swap.dst_path)),
                        dst_swap.tmp_path,
                    )

        #

        if sys.platform == 'linux' and shutil.which('systemctl') is not None:
            async def reload() -> None:
                await asyncio_subprocesses.check_call('systemctl', '--user', 'daemon-reload')

            await reload()

            num_deleted = 0
            for n in ns:
                if n.endswith('.service'):
                    cl = cld.get(n)
                    ul = uld.get(n)
                    if cl is not None:
                        if ul is None:
                            cs = ['enable', 'start']
                        else:
                            cs = ['restart']
                    else:  # noqa
                        if ul is not None:
                            cs = ['stop']
                            num_deleted += 1
                        else:
                            cs = []

                    for c in cs:
                        await asyncio_subprocesses.check_call('systemctl', '--user', c, n)

            if num_deleted:
                await reload()
