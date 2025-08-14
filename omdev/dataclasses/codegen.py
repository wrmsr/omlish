import logging
import os.path
import typing as ta

from omlish import check
from omlish import lang
from omlish.formats.toml.parser import toml_loads


log = logging.getLogger(__name__)


##


CONFIG_FILE_NAME = '.dataclasses.toml'


class DataclassCodeGen:
    def __init__(self) -> None:
        super().__init__()

    def run_config_file(self, config_file: str) -> None:
        with open(config_file) as f:
            config_toml = f.read()
        config_obj = toml_loads(config_toml)

        should_codegen = check.isinstance(config_obj.get('codegen', False), bool)
        if not should_codegen:
            return

        pkg_root = os.path.dirname(config_file).replace(os.sep, '.')

        log.info('Running codegen on package: %s', pkg_root)

        sub_pkgs = sorted(lang.yield_importable(
            pkg_root,
            recursive=True,
            include_special=True,
        ))

        for sub_pkg in sub_pkgs:
            print(f'{sub_pkg=}')

    def run(
            self,
            root_dirs: ta.Iterable[str],
    ) -> None:
        check.not_isinstance(root_dirs, str)

        config_files: set[str] = set()
        for root_dir in root_dirs:
            for dp, _, fns in os.walk(root_dir):
                if CONFIG_FILE_NAME in fns:
                    config_files.add(os.path.join(dp, CONFIG_FILE_NAME))

        for config_file in sorted(config_files):
            self.run_config_file(config_file)
