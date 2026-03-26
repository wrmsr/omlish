"""
TODO:
 - per-feature config, obv
 - install pnpm
"""
import io
import typing as ta

from omlish import lang

from .config import Config
from .content import LazyContent
from .content import Resource
from .content import WithStaticEnv
from .helpers import APT_CACHE_MOUNTS
from .helpers import fragment_section
from .helpers import read_versions_file_versions
from .helpers import render_apt_install_dep_sets
from .ops import Cmd
from .ops import Entrypoint
from .ops import Env
from .ops import From
from .ops import Op
from .ops import Run
from .ops import Section
from .ops import User
from .ops import Workdir
from .ops import Write
from .rendering import render_op


##


def gen_ops(cfg: Config) -> ta.Sequence[Op]:
    ops: list[Op] = [
        From(cfg.base_image),
    ]

    # ops.append(Section('timestamp', [
    #     Copy(src='docker/.timestamp', dst='/'),
    # ]))

    home = f'/{cfg.user or "root"}'

    ops.append(Section('locale', [
        Env([
            ('LANG', 'en_US.UTF-8'),
            ('LANGUAGE', 'en_US:en'),
            ('LC_ALL', 'en_US.UTF-8'),
        ]),
    ]))

    ##
    # apt

    ops.append(Section('deps', [
        Run(
            [
                Resource('fragments/apt.sh'),
                LazyContent(lambda: render_apt_install_dep_sets(*(cfg.dep_sets or []))),
            ],
            cache_mounts=APT_CACHE_MOUNTS,
        ),
    ]))

    if cfg.user is not None:
        ops.append(Section('user', [
            Run(
                WithStaticEnv(
                    Resource('fragments/user.sh'),
                    {
                        'NEWUSER': cfg.user,
                        'NEWUID': str(cfg.uid),
                        'NEWGID': str(cfg.gid),
                    },
                ),
            ),
            User(cfg.user),
        ]))

    ops.append(fragment_section(
        'firefox',
        cache_mounts=APT_CACHE_MOUNTS,
    ))

    ops.append(fragment_section(
        'docker',
        cache_mounts=APT_CACHE_MOUNTS,
    ))

    ops.append(fragment_section(
        'jdk',
        static_env={'JDKS': cfg.jdks or []},
        cache_mounts=APT_CACHE_MOUNTS,
    ))

    ops.append(fragment_section('man'))

    ##
    # langs

    ops.append(fragment_section('rust'))

    ops.append(fragment_section('go'))

    ops.append(fragment_section('zig'))

    ops.append(fragment_section('vcpkg'))

    ops.append(fragment_section(
        'nvm',
        static_env={'NVM_VERSIONS': cfg.nvm_versions or []},
    ))

    ops.append(fragment_section(
        'rbenv',
        static_env={'RBENV_VERSIONS': cfg.rbenv_versions or []},
    ))

    ops.append(fragment_section(
        'uv',
        static_env={'UV_PYTHON_VERSIONS': cfg.uv_python_versions or []},
    ))

    ops.append(fragment_section(
        'pyenv',
        static_env=lambda: {
            'PYENV_VERSIONS': list(read_versions_file_versions(
                'resources',
                '.python-versions.json',
                cfg.pyenv_version_keys or [],
            ).values()),
        },
        cache_mounts=[f'{home}/.pyenv_cache'],
        cache_mount_args=[f'uid={cfg.uid}', f'gid={cfg.gid}'],
    ))

    ##
    # config

    ops.append(fragment_section('sshd'))

    ops.append(Section('configs', [
        Write(f'{home}/{n}', r.read_text())
        for n, r in sorted(lang.get_relative_resources('resources.configs', globals=globals()).items())
        if r.is_file
    ]))

    ops.append(Section('scripts', [
        Run(f'mkdir {home}/scripts ;'),
        *[
            Write(f'{home}/scripts/{n}', r.read_text())
            for n, r in sorted(lang.get_relative_resources('resources.scripts', globals=globals()).items())
            if r.is_file
        ],
        Run(f'chmod a+x {home}/scripts/* ;'),
        Run(f"""echo '\\n\\nexport PATH="$HOME/scripts:$PATH"' >> {home}/.bashrc ;"""),
    ]))

    ops.append(Section('entrypoint', [
        *([Workdir(cfg.workdir)] if cfg.workdir is not None else []),
        Entrypoint(['dumb-init', '--']),
        Cmd(['sh', '-c', 'echo "Ready" && sleep infinity']),
    ]))

    return ops


def gen_src(cfg: Config) -> str:
    ops = gen_ops(cfg)

    out = io.StringIO()
    for i, section in enumerate(ops):
        if i:
            out.write('\n\n\n')
        out.write(render_op(section))

    return out.getvalue()
