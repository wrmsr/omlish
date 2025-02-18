import dataclasses as dc
import time

from ..services import Service


##


class HiService(Service['HiService.Config']):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config(Service.Config):
        num_reps: int = 10
        rep_sleep_s: float = .1

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    def _run(self) -> None:
        for i in range(self._config.num_reps):
            print(i)
            time.sleep(self._config.rep_sleep_s)


##


def _main() -> None:
    hi_cfg = HiService.Config()
    Service.run_config(hi_cfg)


if __name__ == '__main__':
    _main()
