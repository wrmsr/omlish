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
import typing as ta
import os.path

from omlish.lite.check import check
from omlish.os.paths import abs_real_path
from omlish.os.paths import is_path_in_dir
from omlish.os.paths import relative_symlink

from .specs import DeploySystemdSpec
from .types import DeployHome


class DeploySystemdManager:
    def _unlink_all(
            self,
            home: DeployHome,
            unit_dir: str,
    ) -> None:
        for f in os.listdir(unit_dir):
            fp = os.path.join(unit_dir, f)
            if os.path.islink(fp):
                if is_path_in_dir(home, fp):
                    os.unlink(fp)


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

        # FIXME: don't unlink unnecessarily
        self._unlink_all(home, ud)

        if os.path.exists(conf_dir):
            for f in os.listdir(conf_dir):
                fp = abs_real_path(os.path.join(conf_dir, f))
                check.state(os.path.isfile(fp))
                relative_symlink(fp, os.path.join(ud, f))
