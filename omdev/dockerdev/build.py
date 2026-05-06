import json
import os.path
import re
import subprocess
import tempfile

from omlish import check

from .config import Config
from .gen import gen_src
from .utils import run_and_tee


##


SHA_PAT = re.compile(r'sha256:[0-9a-f]{64}')


def build_image(
        cfg: Config,
        *,
        offline: bool = False,
        verbose: bool = False,
) -> str:
    bim = cfg.base_image
    for sep in ':@':
        bim = bim.split(sep, maxsplit=1)[0]

    def run_insp() -> str:
        return subprocess.check_output(  # type: ignore
            ['docker', 'image', 'inspect', cfg.base_image],
            **(dict(stderr=subprocess.DEVNULL) if not verbose else {}),
        ).decode()

    try:
        insp_out = run_insp()
    except subprocess.CalledProcessError:
        if offline:
            raise
        subprocess.check_output(['docker', 'pull', '-q', cfg.base_image])
        insp_out = run_insp()

    insp_out_obj = json.loads(insp_out)
    insp_out_dct = check.not_empty(insp_out_obj)[0]

    # TODO: really want to rewrite Dockerfile on the fly to directly use this local image as a base to avoid any
    #       network hit, but docker is *really hostile* to that idea
    #  cfg = dc.replace(cfg, base_image=tag)
    obi = check.non_empty_str(insp_out_dct['Id'])  # noqa

    src = gen_src(cfg)

    tmp_dir = tempfile.mkdtemp()
    df = os.path.join(tmp_dir, 'Dockerfile')
    with open(df, 'w') as f:
        f.write(src)

    build_args = [
        '-f',
        df,
    ]

    if offline:
        build_args.append('--pull=false')

    build_args.append('.')

    if not verbose:
        out = subprocess.check_output(['docker', 'build', '-q', *build_args]).decode()
        if (m := SHA_PAT.search(out)) is not None:
            return m.group(0)
        raise RuntimeError("Can't find sha256 in output")

    else:
        proc, out = run_and_tee(['docker', 'build', *build_args])
        check.state(proc.returncode == 0)
        for line in reversed(out.splitlines()):
            if (m := SHA_PAT.search(line)) is not None:
                return m.group(0)
        raise RuntimeError("Can't find sha256 in output")
