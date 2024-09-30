"""
TODO:
 - detect
  - uv-receipt.toml: [tool]
  - pipx_metadata.json
  - sys.prefix
 - cache manifests
 - ** .pth hack :| **
  - import site, sys; sys.path[0:0] = list(site.getsitepackages())
"""

"""
[tool]
requirements = [
    { name = "omdev-cli", path = "/Users/spinlock/src/wrmsr/omlish/dist/omdev_cli-0.0.0.dev44.tar.gz" },
    { name = "omdev", path = "/Users/spinlock/src/wrmsr/omlish/dist/omdev-0.0.0.dev44.tar.gz" },
    { name = "omlish", path = "/Users/spinlock/src/wrmsr/omlish/dist/omlish-0.0.0.dev44.tar.gz" },
    { name = "ommlx", path = "/Users/spinlock/src/wrmsr/omlish/dist/ommlx-0.0.0.dev44.tar.gz" },
    { name = "openai" },
    { name = "pip" },
]
entrypoints = [
    { name = "om", install-path = "/Users/spinlock/.local/bin/om" },
]
"""

"""
{
    "injected_packages": {},
    "main_package": {
        "app_paths": [
            {
                "__Path__": "/Users/spinlock/.local/pipx/venvs/omdev-cli/bin/om",
                "__type__": "Path"
            }
        ],
        "app_paths_of_dependencies": {},
        "apps": [
            "om"
        ],
        "apps_of_dependencies": [],
        "include_apps": true,
        "include_dependencies": false,
        "man_pages": [],
        "man_pages_of_dependencies": [],
        "man_paths": [],
        "man_paths_of_dependencies": {},
        "package": "omdev-cli",
        "package_or_url": "omdev-cli",
        "package_version": "0.0.0.dev43",
        "pinned": false,
        "pip_args": [],
        "suffix": ""
    },
    "pipx_metadata_version": "0.5",
    "python_version": "Python 3.12.6",
    "source_interpreter": {
        "__Path__": "/opt/homebrew/bin/python3.12",
        "__type__": "Path"
    },
    "venv_args": []
}
"""
