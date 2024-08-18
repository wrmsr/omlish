import importlib.machinery
import re
import sys


def _is_instance_or_subclass(obj, cls):
    return (isinstance(obj, type) and issubclass(obj, cls)) or isinstance(obj, cls)


class MypyDebugPathFinder(importlib.machinery.PathFinder):

    @classmethod
    def _get_spec(cls, fullname, path, target=None):  # noqa
        namespace_path = []
        for entry in path:
            if not isinstance(entry, (str, bytes)):
                continue
            finder = cls._path_importer_cache(entry)  # type: ignore  # noqa
            if finder is not None:
                if isinstance(finder, importlib.machinery.FileFinder):
                    finder = importlib.machinery.FileFinder(
                        finder.path,
                        *[
                            (i, [s]) for s, i in finder._loaders  # type: ignore  # noqa
                            if not _is_instance_or_subclass(i, importlib.machinery.ExtensionFileLoader)
                        ],
                    )
                if hasattr(finder, 'find_spec'):
                    spec = finder.find_spec(fullname, target)
                else:
                    spec = cls._legacy_get_spec(fullname, finder)  # type: ignore  # noqa
                if spec is None:
                    continue
                if spec.loader is not None:
                    return spec
                portions = spec.submodule_search_locations
                if portions is None:
                    raise ImportError('spec missing loader')
                namespace_path.extend(portions)
        return None

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):  # noqa
        if not fullname.startswith('mypy.') and fullname != 'mypy':
            return None
        if path is None:
            path = sys.path
        spec = cls._get_spec(fullname, path, target)
        if spec is None:
            return None
        elif spec.loader is None:
            namespace_path = spec.submodule_search_locations
            if namespace_path:
                spec.origin = None
                spec.submodule_search_locations = importlib.machinery._NamespacePath(  # type: ignore  # noqa
                    fullname,
                    namespace_path,
                    cls._get_spec,
                )
                return spec
            else:
                return None
        else:
            return spec


def _main():
    for i, e in enumerate(sys.meta_path):  # noqa
        if _is_instance_or_subclass(e, importlib.machinery.PathFinder):
            break
    sys.meta_path.insert(i, MypyDebugPathFinder)  # noqa
    sys.path_importer_cache.clear()
    importlib.invalidate_caches()

    from mypy.__main__ import console_entry  # noqa

    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])

    if not any(k in sys.argv[1:] for k in ['--show-traceback', '--tb']):
        sys.argv.insert(1, '--show-traceback')

    console_entry()


if __name__ == '__main__':
    _main()
