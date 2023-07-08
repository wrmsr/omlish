import contextlib
import shutil
import tempfile
import typing as ta


@contextlib.contextmanager
def tmp_dir(
        root_dir: ta.Optional[str] = None,
        cleanup: bool = True,
        **kwargs: ta.Any
) -> ta.Iterator[str]:
    path = tempfile.mkdtemp(dir=root_dir, **kwargs)
    try:
        yield path
    finally:
        if cleanup:
            shutil.rmtree(path, ignore_errors=True)


@contextlib.contextmanager
def tmp_file(
        root_dir: ta.Optional[str] = None,
        cleanup: bool = True,
        **kwargs: ta.Any
) -> ta.Iterator[tempfile._TemporaryFileWrapper]:  # noqa
    with tempfile.NamedTemporaryFile(dir=root_dir, delete=False, **kwargs) as f:
        try:
            yield f
        finally:
            if cleanup:
                shutil.rmtree(f.name, ignore_errors=True)
