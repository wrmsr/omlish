import os.path

from omlish.lite.check import check
from omlish.os.paths import is_path_in_dir

from .specs import DeployConfSpec


class DeployConfManager:
    async def write_conf(
            self,
            spec: DeployConfSpec,
            conf_dir: str,
    ) -> None:
        conf_dir = os.path.abspath(conf_dir)
        os.makedirs(conf_dir)

        for cf in spec.files or []:
            conf_file = os.path.join(conf_dir, cf.path)
            check.arg(is_path_in_dir(conf_dir, conf_file))

            os.makedirs(os.path.dirname(conf_file), exist_ok=True)

            with open(conf_file, 'w') as f:  # noqa
                f.write(cf.body)
