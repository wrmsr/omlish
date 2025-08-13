import json
import os.path
import shutil
import subprocess
import sys
import tempfile

from omlish.diag._pycharm import runhack  # noqa


def test_dumping(request):
    tmp_dir = tempfile.mkdtemp()
    request.addfinalizer(lambda: shutil.rmtree(tmp_dir))
    print(tmp_dir)

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

    out_str = subprocess.check_output(
        [
            sys.executable,
            '-m',
            __package__.rpartition('.')[0],
            'gen',
            'foo',
        ],
        cwd=packages_dir,
        env={
            **os.environ,
            'PYTHONPATH': python_path,
            runhack.ENABLED_ENV_VAR: '0',
        },
    ).decode()
    print(out_str)

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
