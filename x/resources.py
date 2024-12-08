def read_package_resource_bytes(package: str, resource: str) -> bytes:
    import importlib.resources
    return importlib.resources.read_binary(package, resource)


def _main() -> None:
    print(read_package_resource_bytes(__package__, 'mph.py'))


if __name__ == '__main__':
    _main()
