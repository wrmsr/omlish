import argparse
import dataclasses as dc


@dc.dataclass(frozen=True)
class CliModule:
    cmd_name: str
    mod_name: str


def _main() -> None:
    parser = argparse.ArgumentParser()


if __name__ == '__main__':
    _main()
