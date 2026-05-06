"""
====

./om dockerdev run -CG --user=0:0 --env=TARGET_UID=1000 --env=TARGET_GID=1000 --rm -it bash

if [ "$TARGET_UID" != "0" ] && [ "$TARGET_UID" != "$(id -u omlish)" ]; then
  # 1. Evict any existing user squatting on our target UID
  CONFLICT_USER=$(getent passwd "$TARGET_UID" | cut -d: -f1)
  if [ -n "$CONFLICT_USER" ] && [ "$CONFLICT_USER" != "omlish" ]; then
      userdel "$CONFLICT_USER"
  fi

  # 2. Ensure the target group exists
  getent group "$TARGET_GID" >/dev/null 2>&1 || groupadd -g "$TARGET_GID" hostgroup

  # 3. DECOY: Temporarily point home dir away to bypass the automatic large chown
  usermod -d /tmp omlish

  # 4. Shift omlish's primary UID and GID to match the host, keeping original group
  usermod -u "$TARGET_UID" -g "$TARGET_GID" -aG 4317 omlish

  # 5. RESTORE: Point the home directory back
  usermod -d /omlish omlish
fi

# TODO: unset TARGET_UID, TARGET_GID, dynamically get 4317/'omlish'

exec gosu omlish bash  # "$@"
"""
import os.path
import platform
import shutil
import sys
import tempfile
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish.os.paths import is_path_in_dir

from ..home.paths import get_cache_dir
from .build import build_image
from .config import Config


##


@dc.dataclass(frozen=True, kw_only=True)
class RunArgs:
    verbose: bool = False

    mounts: ta.Sequence[str] | None = None
    mount_caches: bool = False
    mount_docker_sock: bool = False
    mount_git: bool = False

    privileged: bool = False

    offline: bool = False

    no_host_platform: bool = False

    autoexecs: ta.Sequence[str] | None = None

    x11: bool = False

    unknown_args: ta.Sequence[str] | None = None
    extra_args: ta.Sequence[str] | None = None


def process_run_args(
        cfg: Config,
        args: RunArgs,
        sha: str,
) -> list[str]:
    run_args: list[str] = []

    if args.unknown_args:
        run_args.extend(args.unknown_args)
    else:
        run_args.extend([
            '--rm',
            '-it',
        ])

    if args.privileged:
        run_args.append('--privileged')

    if args.offline:
        run_args.append('--pull=never')

    if args.mounts:
        run_args.extend([f'--mount={m}' for m in args.mounts])

    if args.mount_docker_sock:
        run_args.append('--mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock')

    if args.mount_caches:
        cache_dir = os.path.join(get_cache_dir(), 'dockerdev')
        for cl, cr in (cfg.cache_mounts or {}).items():
            cld = os.path.join(cache_dir, cl)
            check.state(is_path_in_dir(cache_dir, cld))
            os.makedirs(cld, exist_ok=True)
            run_args.append(f'--mount=type=bind,src={cld},dst={cr}')

    if args.mount_git:
        git_path = os.path.join(os.getcwd(), '.git')
        check.state(os.path.isdir(git_path))
        run_args.append(f'--mount=type=bind,src={git_path},dst=/git,ro')

    if not args.no_host_platform:
        run_args.extend([f'--env=DOCKER_HOST_PLATFORM={platform.system().lower()}'])

    if args.autoexecs:
        tmp_dir = tempfile.mkdtemp()
        tmp_ep = os.path.join(tmp_dir, 'entrypoint.sh')
        with open(tmp_ep, 'w') as f:
            f.write('\n'.join([
                '#!/bin/sh',
                'set -e',
                *args.autoexecs,
                'exec "$@"',
            ]))
        os.chmod(tmp_ep, 0o755)  # noqa
        run_args.extend([
            f'--mount=type=bind,src={tmp_dir},dst=/dockerdev,readonly',
            f'--entrypoint=/dockerdev/entrypoint.sh',
        ])

    if args.x11:
        sys_platform = getattr(sys, 'platform')  # shuts up mypy
        if sys_platform.startswith('linux'):
            run_args.extend([
                f'--env=DISPLAY',
                '--volume=/tmp/.X11-unix:/tmp/.X11-unix:rw',
                f'--volume={os.environ["HOME"]}/.Xauthority:/tmp/.Xauthority:ro',
                '--env=XAUTHORITY=/tmp/.Xauthority',
            ])
        elif sys_platform == 'darwin':
            run_args.extend([
                '--env=DISPLAY=host.docker.internal:0',
            ])
        else:
            raise OSError(sys_platform)

    run_args.append(sha)

    if args.extra_args:
        run_args.extend(check.not_empty(args.extra_args))
    else:
        run_args.append('bash')

    return run_args


def run_image(
        cfg: Config,
        args: RunArgs = RunArgs(),
        sha: str | None = None,
) -> None:
    if sha is None:
        sha = build_image(
            cfg,
            offline=args.offline,
            verbose=args.verbose,
        )

    #

    run_args = process_run_args(
        cfg,
        args,
        sha,
    )

    #

    os.execl(
        docker := check.not_none(shutil.which('docker')),
        docker,
        'run',
        *run_args,
    )
