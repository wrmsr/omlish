import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish.formats.yaml import all as yaml

from .types import Skill
from .types import SkillHeader


##


class SkillParseError(Exception):
    pass


def parse_skill(content: str) -> Skill:
    check.arg(content.startswith('---'))

    parts = content.split('---', 2)
    check.arg(len(parts) >= 3)

    hdr_str = parts[1]
    body = parts[2].strip()

    hdr_dct = check.isinstance(yaml.safe_load(hdr_str), ta.Mapping)
    hdr = msh.unmarshal(hdr_dct, SkillHeader)

    return Skill(
        hdr,
        body,
    )
