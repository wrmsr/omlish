from ..base import Concern
from ..base import Phase
from ..base import run_in_phase


class RepoConcern(Concern):
    @run_in_phase(Phase.ENV)
    def clone_repo(self) -> None:
        clone_submodules = False
        self._d.ush(
            'cd ~/app',
            f'git clone --depth 1 {self._d.cfg.repo_url} {self._d.cfg.app_name}',
            *([
                f'cd {self._d.cfg.app_name}',
                'git submodule update --init',
            ] if clone_submodules else []),
        )
