import concurrent.futures as cf
import functools
import os.path

from omdev.pyproject.pkg import PyprojectPackageGenerator


##


def _main() -> None:
    if not os.path.isfile('pyproject.toml'):
        raise RuntimeError('must run in project root')

    build_root = os.path.join('.pkg')
    build_output_dir = 'dist'

    run_build = True
    num_threads = 8

    if run_build:
        os.makedirs(build_output_dir, exist_ok=True)

    dir_names = [
        'omdev',
        'ominfra',
        'omlish',
        'omml',
        'omserv',
    ]

    with cf.ThreadPoolExecutor(num_threads) as ex:
        futs = [
            ex.submit(functools.partial(
                PyprojectPackageGenerator(
                    dir_name,
                    build_root,
                ).gen,
                run_build=run_build,
                build_output_dir=build_output_dir,
            ))
            for dir_name in dir_names
        ]
        for fut in futs:
            fut.result()


if __name__ == '__main__':
    _main()
