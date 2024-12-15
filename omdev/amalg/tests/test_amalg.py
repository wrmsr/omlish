import os.path

from ..amalg import AmalgGenerator


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
    ]:
        main_path = os.path.abspath(os.path.join(src_base_dir, main_file))

        src = AmalgGenerator(
            main_path,
            mounts=mounts,
        ).gen_amalg()

        assert '_foo_main' not in src
        lit = iter(src.splitlines()[1:])
        while (l := next(lit)) and l.startswith('#'):
            pass
        for l in lit:
            assert not l.startswith('# @omlish-lite')

        out_path = os.path.join(src_base_dir, 'out', os.path.basename(main_file))
        mod = compile(src, out_path, 'exec')
        print(mod)
