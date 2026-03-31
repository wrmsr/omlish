import os.path

from ..parsing import parse_skill
from ..types import Skill
from ..types import SkillHeader


def test_parsing():
    with open(os.path.join(os.path.dirname(__file__), 'my_skill.md')) as f:
        s = f.read()

    sk = parse_skill(s)

    assert sk == Skill(
        header=SkillHeader(
            name='my-skill',
            description='A test skill',
        ),
        body='# My Skill\n\nInstructions here.',
    )
