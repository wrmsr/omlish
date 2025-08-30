"""
TODO:
 - https://github.com/webserver-llc/angie ?
"""
import multiprocessing as mp
import os.path
import shutil
import subprocess
import sys
import tempfile
import urllib.request

from omlish import check
from omlish import lang


##


NGINX_VERSION = '1.28.0'
NGINX_SRC_URL = f'https://nginx.org/download/nginx-{NGINX_VERSION}.tar.gz'

NGINX_VTS_VERSION = '0.2.4'
NGINX_VTS_SRC_URL = f'https://github.com/vozlt/nginx-module-vts/archive/refs/tags/v{NGINX_VTS_VERSION}.tar.gz'


def build_nginx() -> None:
    build_dir = tempfile.mkdtemp('-omlish-nginx-build')
    print(f'{build_dir=}')

    #

    nginx_src_file = urllib.request.urlretrieve(NGINX_SRC_URL)[0]  # noqa
    print(f'{nginx_src_file=}')

    nginx_vts_src_file = urllib.request.urlretrieve(NGINX_VTS_SRC_URL)[0]  # noqa
    print(f'{nginx_vts_src_file=}')

    subprocess.check_call(['tar', 'xvzf', nginx_src_file, '-C', build_dir])
    nginx_dir = os.path.join(build_dir, f'nginx-{NGINX_VERSION}')

    subprocess.check_call(['tar', 'xvzf', nginx_vts_src_file, '-C', build_dir])
    nginx_vts_dir = os.path.join(build_dir, f'nginx-module-vts-{NGINX_VTS_VERSION}')

    #

    patch_prefix = f'nginx-{NGINX_VERSION}_'
    for r in lang.get_relative_resources('patches', globals=globals()).values():
        if r.is_file and r.name.startswith(patch_prefix) and r.name.endswith('.patch'):
            print(r.name)

            patch_src = r.read_bytes()
            subprocess.run(
                ['git', 'apply'],
                cwd=nginx_dir,
                input=patch_src,
                check=True,
            )

    #

    cflags = [
        '-g',
        '-O2',
        '-fstack-protector',
    ]
    ldflags: list[str] = []

    if sys.platform == 'darwin':
        openssl_prefix = subprocess.check_output(['brew', '--prefix', 'openssl']).decode().strip()
        pcre_prefix = subprocess.check_output(['brew', '--prefix', 'pcre']).decode().strip()
        cflags.extend([
            f'-I{openssl_prefix}/include',
            f'-I{pcre_prefix}/include',
        ])
        ldflags.extend([
            f'-L{openssl_prefix}/lib',
            f'-L{pcre_prefix}/lib',
        ])

    subprocess.check_call([
        check.not_none(shutil.which('sh')),

        'configure',

        f'--with-cc-opt={" ".join(cflags)}',
        f'--with-ld-opt={" ".join(ldflags)}',

        '--with-compat',
        '--with-threads',
        '--with-debug',
        '--with-ipv6',
        '--with-pcre',
        '--with-pcre-jit',

        '--with-http_auth_request_module',
        '--with-http_gunzip_module',
        '--with-http_gzip_static_module',
        '--with-http_ssl_module',
        '--with-http_stub_status_module',
        '--with-http_v2_module',

        '--with-stream',
        '--with-stream_ssl_module',
        '--with-stream_ssl_preread_module',

        f'--add-module={nginx_vts_dir}',
    ], cwd=nginx_dir)

    #

    make_jobs = max(mp.cpu_count() // 2, 1)
    subprocess.check_call([
        'make',
        f'-j{make_jobs}',
    ], cwd=nginx_dir)

    #

    exe_file = os.path.join(nginx_dir, 'objs', 'nginx')
    print(exe_file)


def _main() -> None:
    build_nginx()


if __name__ == '__main__':
    _main()
