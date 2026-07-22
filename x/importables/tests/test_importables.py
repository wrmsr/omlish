"""
Tests for importables.py.

Every fixture module body writes to a sentinel file and then raises - so anything that actually imports (or even
execs) discovered code fails loudly, twice over: the autouse `no_execution` fixture checks the sentinel after every
test, and the zero-import tests additionally assert (via `no_imports`) that nothing new appeared in sys.modules. The
benign tree (used for parity against traversal.py, which *does* import) is separate.
"""
import contextlib
import os.path
import sys
import zipfile

import pytest

from .. import importables
from .. import traversal


##


TRAP = (
    "with open({sentinel!r}, 'a') as f:\n"
    "    f.write(__name__ + '\\n')\n"
    "raise AssertionError('EXECUTED: ' + __name__)\n"
)


def build_fixtures(td: str) -> dict:
    sentinel = os.path.join(td, 'SENTINEL')
    trap = TRAP.format(sentinel=sentinel)

    def mk(rel: str, content: str = '') -> None:
        path = os.path.join(td, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)

    # trapped tree
    mk('root1/toppkg/__init__.py', trap)
    mk('root1/toppkg/amod.py', trap)
    mk('root1/toppkg/bmod.py', trap)
    mk('root1/toppkg/__main__.py', trap)
    mk('root1/toppkg/_priv.py', trap)
    mk('root1/toppkg/foo-bar.py', trap)
    mk('root1/toppkg/data.txt', 'not python\n')
    mk('root1/toppkg/__pycache__/junk.py', trap)
    mk('root1/toppkg/subpkg/__init__.py', trap)
    mk('root1/toppkg/subpkg/cmod.py', trap)
    mk('root1/toppkg/subpkg/subsub/__init__.py', trap)
    mk('root1/toppkg/subpkg/subsub/dmod.py', trap)
    mk('root1/toppkg/nsdir/nmod.py', trap)
    mk('root1/topmod.py', trap)

    # namespace package split across two roots
    mk('root1/nspkg/p1mod.py', trap)
    mk('root2/nspkg/p2mod.py', trap)
    mk('root2/nspkg/nsub/__init__.py', trap)
    mk('root2/nspkg/nsub/inner.py', trap)

    # benign, deliberately imported, __path__ mutated at runtime
    mk('root1/livepkg/__init__.py', '')
    mk('root1/livepkg/lm1.py', trap)
    mk('extra_live/lm2.py', trap)

    # benign fs package colliding with a package inside the pyz
    mk('root_collide/collider/__init__.py', '')
    mk('root_collide/collider/fsonly.py', trap)

    # benign tree for parity with traversal.py (which imports)
    mk('root_benign/bpkg/__init__.py', '')
    mk('root_benign/bpkg/m1.py', '')
    mk('root_benign/bpkg/m2.py', '')
    mk('root_benign/bpkg/__main__.py', 'pass\n')
    mk('root_benign/bpkg/sub/__init__.py', '')
    mk('root_benign/bpkg/sub/m3.py', '')
    mk('root_benign/bpkg/sub/deeper/__init__.py', '')
    mk('root_benign/bpkg/sub/deeper/m4.py', '')
    mk('root_benign/bpkg/ignored_dir/x.py', '')

    # trapped pyz with multiple top-level packages/modules
    pyz = os.path.join(td, 'app.pyz')
    with zipfile.ZipFile(pyz, 'w') as zf:
        zf.writestr('__main__.py', trap)
        zf.writestr('topzmod.py', trap)
        zf.writestr('alpha/__init__.py', trap)
        zf.writestr('alpha/aa.py', trap)
        zf.writestr('alpha/sub/__init__.py', trap)
        zf.writestr('alpha/sub/deep.py', trap)
        zf.writestr('alpha/nsd/leaf.py', trap)
        zf.writestr('alpha/__pycache__/junk.py', trap)
        zf.writestr('beta/__init__.py', trap)
        zf.writestr('collider/__init__.py', trap)
        zf.writestr('collider/zmod.py', trap)

    return {
        'td': td,
        'sentinel': sentinel,
        'pyz': pyz,
        'sys_path': [
            os.path.join(td, 'root1'),
            os.path.join(td, 'root2'),
            os.path.join(td, 'root_collide'),
            pyz,
            os.path.join(td, 'root_benign'),
        ],
    }


##


@pytest.fixture(scope='session')
def fx(tmp_path_factory: pytest.TempPathFactory) -> dict:
    fx = build_fixtures(str(tmp_path_factory.mktemp('yieldimp')))

    # zipfile lazily loads this stdlib codec the first time it reads a zip directory with non-utf8-flagged names
    b'x'.decode('cp437')

    old_dwb = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path[0:0] = fx['sys_path']
    try:
        yield fx
    finally:
        for p in fx['sys_path']:
            with contextlib.suppress(ValueError):
                sys.path.remove(p)
        sys.dont_write_bytecode = old_dwb


@pytest.fixture(autouse=True)
def no_execution(fx: dict) -> None:
    def check() -> None:
        if os.path.exists(fx['sentinel']):
            with open(fx['sentinel']) as f:
                raise AssertionError(f'trapped module(s) executed:\n{f.read()}')

    check()
    yield
    check()


@pytest.fixture
def no_imports() -> None:
    before = set(sys.modules)
    yield
    new = set(sys.modules) - before
    assert not new, f'zero-import backend imported: {sorted(new)}'


##


def test_compat_recursive(fx: dict, no_imports: None) -> None:
    names = set(importables.yield_importable('toppkg', recursive=True))
    assert names == {
        'toppkg._priv',
        'toppkg.amod',
        'toppkg.bmod',
        'toppkg.subpkg.cmod',
        'toppkg.subpkg.subsub.dmod',
    }


def test_compat_include_special(fx: dict, no_imports: None) -> None:
    names = set(importables.yield_importable('toppkg', recursive=True, include_special=True))
    assert names == {
        'toppkg.__init__',
        'toppkg.__main__',
        'toppkg._priv',
        'toppkg.amod',
        'toppkg.bmod',
        'toppkg.subpkg.__init__',
        'toppkg.subpkg.cmod',
        'toppkg.subpkg.subsub.__init__',
        'toppkg.subpkg.subsub.dmod',
    }


def test_compat_filter_prunes(fx: dict, no_imports: None) -> None:
    names = set(importables.yield_importable(
        'toppkg',
        recursive=True,
        filter=lambda n: not n.endswith('.subpkg'),
    ))
    assert names == {'toppkg._priv', 'toppkg.amod', 'toppkg.bmod'}


def test_compat_non_recursive(fx: dict, no_imports: None) -> None:
    names = set(importables.yield_importable('toppkg'))
    assert names == {'toppkg._priv', 'toppkg.amod', 'toppkg.bmod'}


def test_rich_kinds(fx: dict, no_imports: None) -> None:
    yielder = importables.ZeroImportImportableYielder(importables.YieldImportableOptions(recursive=True))
    by_name = {i.name: i for i in yielder.yield_importable('toppkg')}

    assert set(by_name) == {
        'toppkg._priv',
        'toppkg.amod',
        'toppkg.bmod',
        'toppkg.subpkg',
        'toppkg.subpkg.cmod',
        'toppkg.subpkg.subsub',
        'toppkg.subpkg.subsub.dmod',
    }

    assert by_name['toppkg.subpkg'].kind == 'package'
    assert by_name['toppkg.subpkg'].origin.endswith(os.path.join('subpkg', '__init__.py'))
    assert by_name['toppkg.subpkg'].search_locations
    assert by_name['toppkg.amod'].kind == 'module'
    assert by_name['toppkg.amod'].origin.endswith('amod.py')


def test_rich_namespace_dirs(fx: dict, no_imports: None) -> None:
    yielder = importables.ZeroImportImportableYielder(importables.YieldImportableOptions(
        recursive=True,
        include_namespace_packages=True,
    ))
    by_name = {i.name: i for i in yielder.yield_importable('toppkg')}
    assert 'toppkg.nsdir' in by_name and 'toppkg.nsdir.nmod' in by_name
    assert by_name['toppkg.nsdir'].kind == 'namespace_package'
    assert by_name['toppkg.nsdir'].origin is None


def test_rich_non_identifier_names(fx: dict, no_imports: None) -> None:
    # non-identifier names reachable only via importlib, on request
    yielder = importables.ZeroImportImportableYielder(importables.YieldImportableOptions(
        identifiers_only=False,
    ))
    names = {i.name for i in yielder.yield_importable('toppkg')}
    assert 'toppkg.foo-bar' in names


def test_namespace_root(fx: dict, no_imports: None) -> None:
    # unimported namespace package root, portions across two sys.path roots
    names = set(importables.yield_importable('nspkg', recursive=True))
    assert names == {'nspkg.p1mod', 'nspkg.p2mod', 'nspkg.nsub.inner'}
    assert 'nspkg' not in sys.modules

    yielder = importables.ZeroImportImportableYielder(importables.YieldImportableOptions(recursive=True))
    imps = {i.name: i for i in yielder.yield_importable('nspkg')}
    assert imps['nspkg.nsub'].kind == 'package'


def test_zip_named_root(fx: dict, no_imports: None) -> None:
    names = set(importables.yield_importable('alpha', recursive=True, include_special=True))
    assert names == {
        'alpha.__init__',
        'alpha.aa',
        'alpha.sub.__init__',
        'alpha.sub.deep',
    }

    yielder = importables.ZeroImportImportableYielder(importables.YieldImportableOptions(
        recursive=True,
        include_namespace_packages=True,
    ))
    by_name = {i.name: i for i in yielder.yield_importable('alpha')}
    assert 'alpha.nsd' in by_name and 'alpha.nsd.leaf' in by_name
    assert by_name['alpha.aa'].origin == os.path.join(fx['pyz'], 'alpha', 'aa.py')
    assert 'alpha' not in sys.modules


def test_path_entry(fx: dict, no_imports: None) -> None:
    # rooted at the pyz itself - would work identically were it not on sys.path
    names = set(importables.yield_importable_in(fx['pyz'], recursive=True, include_special=True))
    assert names == {
        '__main__',
        'topzmod',
        'alpha.__init__',
        'alpha.aa',
        'alpha.sub.__init__',
        'alpha.sub.deep',
        'beta.__init__',
        'collider.__init__',
        'collider.zmod',
    }

    names = set(importables.yield_importable_in(fx['pyz'], recursive=True))
    assert names == {'topzmod', 'alpha.aa', 'alpha.sub.deep', 'collider.zmod'}


def test_module_root_and_errors(fx: dict, no_imports: None) -> None:
    assert list(importables.yield_importable('topmod')) == []

    with pytest.raises(ModuleNotFoundError):
        list(importables.yield_importable('no_such_pkg_zzz'))

    with pytest.raises(ModuleNotFoundError):
        list(importables.yield_importable('topmod.sub'))

    with pytest.raises(ValueError):
        list(importables.yield_importable(''))


def test_stdlib_smoke(fx: dict, no_imports: None) -> None:
    names = set(importables.yield_importable('email', recursive=True))
    assert 'email.parser' in names and 'email.mime.text' in names


##


def test_live_path_mutation(fx: dict) -> None:
    # an already-imported package's runtime-mutated __path__ is respected
    import livepkg  # noqa
    livepkg.__path__.append(os.path.join(fx['td'], 'extra_live'))

    names = set(importables.yield_importable('livepkg', recursive=True))
    assert names == {'livepkg.lm1', 'livepkg.lm2'}


def test_collision_not_confused(fx: dict) -> None:
    # sys.modules['collider'] is the *filesystem* package; enumerating the pyz must not pick up its live __path__
    import collider  # noqa
    assert collider.__file__.endswith(os.path.join('root_collide', 'collider', '__init__.py'))

    names = set(importables.yield_importable_in(fx['pyz'], recursive=True))
    assert 'collider.zmod' in names
    assert 'collider.fsonly' not in names

    # ...while named lookup *does* prefer the live module
    names = set(importables.yield_importable('collider', recursive=True))
    assert names == {'collider.fsonly'}


@pytest.mark.parametrize('kw', [{}, {'include_special': True}])
def test_parity_with_traversal(fx: dict, kw: dict) -> None:
    # benign tree only - traversal.py imports everything it walks
    old = set(traversal.yield_importable('bpkg', recursive=True, **kw))
    new = set(importables.yield_importable('bpkg', recursive=True, **kw))
    assert old == new


def test_parity_with_importlib_backend(fx: dict) -> None:
    zero = importables.ZeroImportImportableYielder(importables.YieldImportableOptions(recursive=True))
    implib = importables.ImportlibImportableYielder(importables.YieldImportableOptions(recursive=True))
    zs = {(i.name, i.kind) for i in zero.yield_importable('bpkg')}
    ils = {(i.name, i.kind) for i in implib.yield_importable('bpkg')}
    assert zs == ils


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, *sys.argv[1:]]))
