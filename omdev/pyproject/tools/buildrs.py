import argparse
import os.path
import shlex
import shutil
import subprocess
import sys
import zipfile

from omlish.lite.check import check


##


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('rs_pkg', nargs='*')
    args = parser.parse_args()

    pkgs_dir = '.pkg'
    if not os.path.isdir(pkgs_dir):
        raise RuntimeError(f'{pkgs_dir=} does not exist')

    if not (rs_pkgs := args.rs_pkg):
        rs_pkgs = sorted(
            n
            for n in os.listdir(pkgs_dir)
            if os.path.isdir(p := os.path.join(pkgs_dir, n))
            and n.endswith('-rs')
        )

    for rs_pkg in rs_pkgs:
        print(rs_pkg)

        rs_pkg_dir = os.path.join(pkgs_dir, rs_pkg)

        for n in os.listdir(rs_pkg_dir):
            p = os.path.join(rs_pkg_dir, n)
            if not os.path.isdir(p):
                continue
            if n == 'dist' or n.endswith('.egg-info'):
                shutil.rmtree(p)

        subprocess.run(
            [
                'sh', '-c', f'{shlex.quote(sys.executable)} "$@"', '--',  # sys.executable,
                '-m',
                'build',
            ],
            cwd=rs_pkg_dir,
            env={
                **os.environ,
                'OMLISH_PYCHARM_RUNHACK_ENABLED': '0',
            },
            check=True,
        )

        dist_dir = os.path.join(rs_pkg_dir, 'dist')
        whl_ns = [
            n
            for n in os.listdir(dist_dir)
            if os.path.isfile(os.path.join(dist_dir, n))
            and n.endswith('.whl')
        ]
        whl_n = check.single(whl_ns)
        whl_path = os.path.join(dist_dir, whl_n)

        with zipfile.ZipFile(whl_path) as zf:
            for zn in zf.namelist():
                if not zn.endswith('.so'):
                    continue

                zi = zf.getinfo(zn)
                if zi.is_dir():
                    continue

                print(zn)

                zf.extract(zi)

        print()


if __name__ == '__main__':
    _main()
