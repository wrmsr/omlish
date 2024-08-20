from .base import Deploy
from .base import DeployConcern


class DeployImpl(Deploy):
    concern_cls = DeployConcern

    def run(self) -> None:
        for c in self._concerns:
            c.run()
