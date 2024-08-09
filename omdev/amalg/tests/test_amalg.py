import os.path

from ..amalg import gen_amalg


def test_amalg() -> None:
    prj_dir = os.getcwd()
    if not os.path.isfile(os.path.join(prj_dir, 'pyproject.toml')):
        raise Exception('Not in project root')

    mounts = {
        n: os.path.abspath(os.path.join(prj_dir, n))
        for n in [
            'ominfra',
            'omlish',
            'omml',
            'omserv',
        ]
    }

    src_base_dir = os.path.dirname(__file__)
    for main_file in [
        'demo/demo.py',
        'demo/deploy/deploy.py',
        'demo/interp/interp.py',
        'demo/pyproject/pyproject.py',
    ]:
        main_path = os.path.abspath(os.path.join(src_base_dir, main_file))

        src = gen_amalg(
            main_path,
            mounts=mounts,
        )

        out_path = os.path.join(src_base_dir, 'out', os.path.basename(main_file))
        with open(out_path, 'w') as f:
            f.write(src)
        os.chmod(out_path, os.stat(main_path).st_mode)
