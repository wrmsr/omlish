# ruff: noqa: UP006 UP007
"""
~/.config/systemd/user/

verify - systemd-analyze

sudo loginctl enable-linger "$USER"

cat ~/.config/systemd/user/sleep-infinity.service
    [Unit]
    Description=User-specific service to run 'sleep infinity'
    After=default.target

    [Service]
    ExecStart=/bin/sleep infinity
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=default.target

systemctl --user daemon-reload

systemctl --user enable sleep-infinity.service
systemctl --user start sleep-infinity.service

systemctl --user status sleep-infinity.service
"""
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.os.paths import abs_real_path
from omlish.os.paths import is_path_in_dir

from .specs import DeploySystemdSpec
from .tmp import DeployHomeAtomics
from .types import DeployHome


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

        if not (ud := spec.unit_dir):
            return

        ud = abs_real_path(os.path.expanduser(ud))

        os.makedirs(ud, exist_ok=True)

        uld = {
            n: p
            for n, p in self._scan_link_dir(ud).items()
            if is_path_in_dir(home, p)
        }

        if os.path.exists(conf_dir):
            cld = self._scan_link_dir(conf_dir, strict=True)
        else:
            cld = {}

        for n in sorted(set(uld) | set(cld)):
            ul = uld.get(n)  # noqa
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
