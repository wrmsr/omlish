import dataclasses as dc
import json
import os.path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import typing as ta

from omlish.diag._pycharm import runhack  # noqa


@dc.dataclass(frozen=True, kw_only=True)
class DummyPackages:
    tmp_dir: str
    packages_dir: str
    subprocess_kwargs: ta.Mapping[str, ta.Any]


def build_dummy_packages(request) -> DummyPackages:
    tmp_dir = tempfile.mkdtemp()
    request.addfinalizer(lambda: shutil.rmtree(tmp_dir))

    src_packages_dir = os.path.join(os.path.dirname(__file__), 'packages')
    packages_dir = os.path.join(tmp_dir, 'packages')
    shutil.copytree(src_packages_dir, packages_dir)

    for dp, dns, fns in os.walk(packages_dir, topdown=True):
        if '__pycache__' in dns:
            dns.remove('__pycache__')
            shutil.rmtree(os.path.join(dp, '__pycache__'))
        for fn in fns:
            if fn.endswith('.py'):
                fp = os.path.join(dp, fn)
                with open(fp) as f:
                    src = f.read()
                src = src.replace('@test-omlish-manifest', '@omlish-manifest')
                with open(fp, 'w') as f:
                    f.write(src)

    python_path = ':'.join([
        os.getcwd(),
        *(pp.split(':') if (pp := os.environ.get('PYTHONPATH')) else []),
    ])

    subprocess_kwargs = dict(
        cwd=packages_dir,
        env={
            **os.environ,
            'PYTHONPATH': python_path,
            runhack.ENABLED_ENV_VAR: '0',
        },
    )

    return DummyPackages(
        tmp_dir=tmp_dir,
        packages_dir=packages_dir,
        subprocess_kwargs=subprocess_kwargs,
    )


def test_main(request):
    dummy = build_dummy_packages(request)

    out_str = subprocess.check_output(
        [
            sys.executable,
            '-m',
            __package__.rpartition('.')[0],
            'gen',
            'foo',
        ],
        **dummy.subprocess_kwargs,
    ).decode()
    out = json.loads(out_str)

    assert out == [
        {
            'module': '.nargles.thingy',
            'attr': None,
            'file': 'foo/nargles/thingy.py',
            'line': 1,
            'value': {
                '$.thingies.manifests.ThingyManifest': {
                    'mod_name': 'foo.nargles.thingy',
                    'attr_name': 'NargleThingy',
                    'name': 'nargle',
                    'aliases': None,
                },
            },
        },
    ]


def test_dumping(request):
    dummy = build_dummy_packages(request)

    sp_src = textwrap.dedent(f"""
        import json
        from {__package__.rpartition('.')[0]}.building import ManifestBuilder
        mb = ManifestBuilder({dummy.packages_dir!r})
        fm = mb.build_file_module('foo/nargles/thingy.py')
        tgts = mb.collect_module_manifest_targets(fm)
        print(json.dumps(tgts))
    """)

    out_str = subprocess.check_output(
        [
            sys.executable,
            '-c',
            sp_src,
        ],
        **dummy.subprocess_kwargs,
    ).decode()
    targets = json.loads(out_str)

    sp_src = textwrap.dedent(f"""
        from {__package__.rpartition('.')[0]}.dumping import _ModuleManifestDumper
        _ModuleManifestDumper('foo.nargles.thingy')({", ".join(repr(tgt) for tgt in targets)})
    """)
    out_str = subprocess.check_output(
        [
            sys.executable,
            '-c',
            sp_src,
        ],
        **dummy.subprocess_kwargs,
    ).decode()
    out = json.loads(out_str)

    assert out == [
        {
            'module': '.nargles.thingy',
            'attr': None,
            'file': 'foo/nargles/thingy.py',
            'line': 1,
            'value': {
                '$foo.thingies.manifests.ThingyManifest': {
                    'mod_name': 'foo.nargles.thingy',
                    'attr_name': 'NargleThingy',
                    'name': 'nargle',
                    'aliases': None,
                },
            },
        },
    ]
