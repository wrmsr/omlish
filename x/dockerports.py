import os.path
import re
import typing as ta

from omlish import check
from omlish import lang
from omlish.formats import yaml


_PORT_PAT = re.compile(r'(?P<l>\d+):(?P<r>\d+)')
_PORT_LINE_PAT = re.compile(r"(  )+- '(?P<l>\d+):(?P<r>\d+)'\s*")


def _main():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    docker_dir = os.path.join(base_dir, 'docker')
    yml_file = os.path.join(docker_dir, 'compose.yml')

    with open(yml_file) as f:
        yml_src = f.read()

    #

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
                port = check.isinstance(port_w.value, str)
                if not re.fullmatch(_PORT_PAT, port):
                    raise Exception(f'Bad port: {port}')

                lst.append(PortEntry(
                    l=port_w.node.start_mark.line,
                    s=port,
                ))

            dct[name] = lst

    #

    base_port = 35220

    #

    src_lines = yml_src.splitlines(keepends=True)
    cur_port = base_port

    for ps in dct.values():
        for p in ps:
            l = src_lines[p.l]
            if not (m := _PORT_LINE_PAT.fullmatch(l)):
                raise Exception(f'Bad port line: {p} {l!r}')

            p_l, p_r = map(int, p.s.split(':'))
            l_l, l_r = map(int, [(gd := m.groupdict())['l'], gd['r']])
            if p_l != l_l or p_r != l_r:
                raise Exception(f'Port mismatch: {p}')

            new_l = l.partition("'")[0] + f"{cur_port}:{l_r}'\n"
            src_lines[p.l] = new_l

            cur_port += 1

    new_src = ''.join(src_lines)
    print(new_src)


if __name__ == '__main__':
    _main()
