def read_package_resource_binary(package: str, resource: str) -> bytes:
    import importlib.resources
    return importlib.resources.read_binary(package, resource)


def read_package_resource_text(package: str, resource: str) -> str:
    import importlib.resources
    return importlib.resources.read_text(package, resource)
