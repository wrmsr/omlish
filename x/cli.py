import argparse
import dataclasses as dc

from omdev.manifests import ManifestLoader
from omlish import check


@dc.dataclass(frozen=True)
class CliModule:
    cmd_name: str
    mod_name: str


def _main() -> None:
    cms: list[CliModule] = []

    ldr = ManifestLoader.from_module(__name__, __spec__)  # noqa
    for m in ldr.load('x', only=[CliModule]):
        cms.append(check.isinstance(m.value, CliModule))

    parser = argparse.ArgumentParser()


if __name__ == '__main__':
    _main()
