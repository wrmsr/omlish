"""
TODO:
 - streaming vts relay endpoint
"""
import shlex
import subprocess
import typing as ta

from ... import configs
from ... import properties


class NginxProcess(configs.Configurable):

    class Config(configs.Config):

        connect_timeout = 75.
        send_timeout = 15.
        read_timeout = 5.

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    @properties.cached
    def nginx_exe(self) -> str:
        return 'nginx'

    @properties.cached
    def nginx_info(self) -> str:
        (_, stderr) = subprocess.Popen([self.nginx_exe, '-V'], stderr=subprocess.PIPE).communicate()
        return stderr.decode('utf-8').strip()

    @properties.cached
    def nginx_version_str(self) -> ta.Optional[str]:
        for line in self.nginx_info.split('\n'):
            if line.startswith('nginx version: '):
                ver = line.partition(': ')[2]
                if ' ' in ver:
                    ver = ver.partition(' ')[0]
                if ver.startswith('nginx/'):
                    ver = ver.partition('/')[2]
                return ver
        return None

    @properties.cached
    def nginx_version(self) -> ta.Optional[ta.Sequence[int]]:
        if self.nginx_version_str is not None:
            return tuple(map(int, self.nginx_version_str.split('.')))
        else:
            return None

    @properties.cached
    def nginx_cfg_args(self) -> ta.Optional[ta.List[str]]:
        for line in self.nginx_info.split('\n'):
            if line.startswith('configure arguments: '):
                cfg_line = line.partition(': ')[2]
                return shlex.split(cfg_line)
        return None
