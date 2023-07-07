import contextlib
import shutil
import tempfile
import typing as ta


@contextlib.contextmanager
def tmp_dir(root_dir: str = None, cleanup: bool = True) -> ta.Iterator[str]:
    path = tempfile.mkdtemp(dir=root_dir)
    try:
        yield path
    finally:
        if cleanup:
            shutil.rmtree(path, ignore_errors=True)


@contextlib.contextmanager
def tmp_file(root_dir: str = None, cleanup: bool = True) -> ta.Iterator[tempfile._TemporaryFileWrapper]:  # type: ignore  # noqa
    with tempfile.NamedTemporaryFile(dir=root_dir, delete=False) as f:
        try:
            yield f
        finally:
            if cleanup:
                shutil.rmtree(f.name, ignore_errors=True)


