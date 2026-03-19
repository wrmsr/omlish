"""
TODO:
 - per-feature config, obv
 - install pnpm
"""
import io
import typing as ta

from .config import Config
from .content import LazyContent
from .content import Resource
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

    ops.append(Section('locale', [
        Env([
            ('LANG', 'en_US.UTF-8'),
            ('LANGUAGE', 'en_US:en'),
            ('LC_ALL', 'en_US.UTF-8'),
        ]),
    ]))

    ops.append(Section('deps', [
        Run(
            [
                Resource('fragments/apt.sh'),
                LazyContent(lambda: render_apt_install_dep_sets(*(cfg.dep_sets or []))),
            ],
            cache_mounts=APT_CACHE_MOUNTS,
        ),
    ]))

    ops.append(fragment_section(
        'firefox',
        cache_mounts=APT_CACHE_MOUNTS,
    ))

    ops.append(fragment_section(
        'docker',
        cache_mounts=APT_CACHE_MOUNTS,
    ))

    if cfg.jdks:
        ops.append(fragment_section(
            'jdk',
            static_env={'JDKS': cfg.jdks},
            cache_mounts=APT_CACHE_MOUNTS,
        ))

    ops.append(fragment_section('rust'))

    if cfg.go_version is not None:
        ops.append(fragment_section(
            'go',
            static_env={'GO_VERSION': cfg.go_version},
        ))

    if cfg.zig_version is not None:
        ops.append(fragment_section(
            'zig',
            static_env={'ZIG_VERSION': cfg.zig_version},
        ))

    ops.append(fragment_section('vcpkg'))

    if cfg.nvm_versions:
        ops.append(fragment_section(
            'nvm',
            static_env={'NVM_VERSIONS': cfg.nvm_versions},
        ))

    if cfg.rbenv_versions:
        ops.append(fragment_section(
            'rbenv',
            static_env={'RBENV_VERSIONS': cfg.rbenv_versions},
        ))

    ops.append(fragment_section(
        'uv',
        static_env={'UV_PYTHON_VERSIONS': cfg.uv_python_versions or []},
    ))

    if cfg.pyenv_version_keys:
        ops.append(fragment_section(
            'pyenv',
            static_env=lambda: {
                'PYENV_VERSIONS': list(read_versions_file_versions(
                    'resources',
                    '.python-versions.json',
                    cfg.pyenv_version_keys,
                ).values()),
            },
            cache_mounts=['/root/.pyenv_cache'],
        ))

    ops.append(fragment_section('sshd'))

    # ops.append(Section('x11', [
    #     Run('touch /root/.Xauthority'),
    #     Write('/root/xu', Resource('xu')),
    # ]))

    if cfg.config_files:
        ops.append(Section('configs', [
            Write(f'/root/{n}', Resource(f'configs/{n}'))
            for n in cfg.config_files
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
