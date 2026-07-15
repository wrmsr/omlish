"""
====

./om dockerdev run -CG \
    --user=0:0 \
    --env=EXTERNAL_UID=1000 \
    --env=EXTERNAL_GID=1000 \
    --env=INTERNAL_USER=om \
    --rm -it bash

====

INTERNAL_UID=$(id -u "$INTERNAL_USER")

if [ "$EXTERNAL_UID" != "$INTERNAL_UID" ]; then
  # 1. Evict any existing user squatting on our target UID
  CONFLICT_USER=$(getent passwd "$EXTERNAL_UID" | cut -d: -f1)
  if [ -n "$CONFLICT_USER" ] && [ "$CONFLICT_USER" != "$INTERNAL_USER" ]; then
      userdel "$CONFLICT_USER"
  fi

  # 2. Ensure the target group exists
  getent group "$EXTERNAL_GID" >/dev/null 2>&1 || groupadd -g "$EXTERNAL_GID" shift-uid

  # 3. DECOY: Temporarily point home dir away to bypass the automatic large chown
  INTERNAL_HOME=$(getent passwd "$INTERNAL_USER" | cut -d: -f6)
  usermod -d /tmp "$INTERNAL_USER"

  # 4. Shift user's primary UID and GID to match the host, keeping original group
  usermod -u "$EXTERNAL_UID" -g "$EXTERNAL_GID" -aG "$INTERNAL_UID" "$INTERNAL_USER"

  # 5. Point the home directory back
  usermod -d "$INTERNAL_HOME" "$INTERNAL_USER"
fi

unset EXTERNAL_UID
unset EXTERNAL_GID
unset INTERNAL_USER

unset INTERNAL_UID
unset INTERNAL_HOME

exec gosu om bash  # "$@"
"""
import os.path
import platform
import re
import shutil
import sys
import tempfile
import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang
from omcore.os.paths import is_path_in_dir
from omcore.secrets import all as sec

from ..home.paths import get_cache_dir
from ..home.secrets import load_secrets
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
    clone_mount_git: bool = False

    privileged: bool = False

    offline: bool = False

    no_host_platform: bool = False

    autoexecs: ta.Sequence[str] | None = None

    x11: bool = False

    no_default_labels: bool = False

    # TODO: k=v? currently hardcodes env key as `sk.upper()`
    inject_secrets_pats: ta.Sequence[str | re.Pattern[str]] | None = None

    shift_uid: tuple[int, int] | None = None

    unknown_args: ta.Sequence[str] | None = None
    extra_args: ta.Sequence[str] | None = None


LABEL_PREFIX = 'om.dockerdev'


@dc.dataclass(frozen=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class ProcessedRunArgs:
    args: list[str]

    _: dc.KW_ONLY

    env: dict[str, str | sec.Secret] | None = None


def process_run_args(
        cfg: Config,
        args: RunArgs,
        sha: str,
) -> ProcessedRunArgs:
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

    autoexecs: list[str] = []

    if args.mount_git or args.clone_mount_git:
        git_path = os.path.join(os.getcwd(), '.git')
        check.state(os.path.isdir(git_path))
        run_args.append(f'--mount=type=bind,src={git_path},dst=/git,ro')

        if args.clone_mount_git:
            autoexecs.append('git clone -q /git /work/git')

    if not args.no_host_platform:
        run_args.extend([f'--env=DOCKER_HOST_PLATFORM={platform.system().lower()}'])

    @lang.cached_function
    def tmp_dir() -> str:
        d = tempfile.mkdtemp()
        run_args.extend([
            f'--mount=type=bind,src={d},dst=/dockerdev,readonly',
        ])
        return d

    entrypoint: str | None = None

    autoexecs.extend(args.autoexecs or [])

    if autoexecs:
        tmp_ep = os.path.join(tmp_dir(), 'autoexec.sh')
        with open(tmp_ep, 'w') as f:
            f.write('\n'.join([
                '#!/bin/sh',
                'set -e',
                *autoexecs,
                'exec "$@"',
            ]))
        os.chmod(tmp_ep, 0o755)  # noqa
        entrypoint = '/dockerdev/autoexec.sh'

    if args.shift_uid is not None:
        su_uid, su_gid = args.shift_uid
        su_src = lang.get_relative_resources('.resources', globals=globals())['shift-uid.sh'].read_text()
        tmp_su_ep = os.path.join(tmp_dir(), 'shift-uid.sh')
        with open(tmp_su_ep, 'w') as f:
            f.write(su_src)
        os.chmod(tmp_su_ep, 0o755)  # noqa
        run_args.extend([
            '--user=0:0',
        ])
        run_args.extend([
            f'--env={k}={v}' for k, v in {
                'SHIFTUID_EXTERNAL_UID': str(su_uid),
                'SHIFTUID_EXTERNAL_GID': str(su_gid),
                'SHIFTUID_INTERNAL_USER': check.non_empty_str(cfg.user),
                'SHIFTUID_INTERNAL_ENTRYPOINT': entrypoint or '',
            }.items()
        ])
        entrypoint = '/dockerdev/shift-uid.sh'

    if entrypoint is not None:
        run_args.extend([
            f'--entrypoint={entrypoint}',
        ])

    if args.x11:
        sys_platform = getattr(sys, 'platform')  # shuts up mypy
        if sys_platform.startswith('linux'):
            run_args.extend([
                '--env=DISPLAY',
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

    if not args.no_default_labels:
        run_args.append(f'--label={LABEL_PREFIX}')

    env: dict[str, str | sec.Secret] = {}

    if isp_lst := args.inject_secrets_pats:
        secrets = check.isinstance(load_secrets(), sec.IterableSecrets)

        isp_pats: list[re.Pattern[str]] = [x if isinstance(x, re.Pattern) else re.compile(x) for x in isp_lst]

        for sk in secrets:
            if any(xp.fullmatch(sk) for xp in isp_pats):
                ek = sk.upper()
                env[ek] = secrets.get(sk)
                run_args.append(f'--env={ek}')
                break

    run_args.append(sha)

    if args.extra_args:
        run_args.extend(check.not_empty(args.extra_args))
    else:
        run_args.append('bash')

    return ProcessedRunArgs(
        run_args,
        env=env or None,
    )


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

    p_args = process_run_args(
        cfg,
        args,
        sha,
    )

    #

    os.execle(
        docker := check.not_none(shutil.which('docker')),
        docker,
        'run',
        *p_args.args,
        {
            **os.environ,
            **({
                ek: ev.reveal() if isinstance(ev, sec.Secret) else ev
                for ek, ev in p_args.env.items()
            } if p_args.env else {}),
        },
    )
