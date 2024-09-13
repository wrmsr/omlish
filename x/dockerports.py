import os.path
import typing as ta

from omlish import check
from omlish import lang
from omlish.formats import yaml


def _main():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    docker_dir = os.path.join(base_dir, 'docker')
    yml_file = os.path.join(docker_dir, 'compose.yml')

    with open(yml_file) as f:
        yml_src = f.read()

    class PortEntry(ta.NamedTuple):
        l: int
        s: str

    dct: dict[str, list[PortEntry]] = {}

    with lang.disposing(yaml.WrappedLoaders.base(yml_src)) as loader:
        val = check.not_none(loader.get_single_data())
        root = check.isinstance(val.value, ta.Mapping)

        services = check.isinstance(check.single(v.value for k, v in root.items() if k.value == 'services'), ta.Mapping)
        for name_w, cfg_w in services.items():
            name = check.isinstance(name_w.value, str)
            cfg = check.isinstance(cfg_w.value, ta.Mapping)

            ports = check.opt_single(v.value for k, v in cfg.items() if k.value == 'ports')
            if not ports:
                continue

            lst: list[PortEntry] = []
            for port_w in ports:
                lst.append(PortEntry(
                    l=port_w.node.start_mark.line,
                    s=check.isinstance(port_w.value, str),
                ))

            dct[name] = lst

    print(dct)


if __name__ == '__main__':
    _main()
