from ...envs import Env
from ..messages import SystemMessage
from ..messages import UserMessage
from ..templating import ChatTemplater
from ..templating import MessageTemplate


def test_templating():
    print(ChatTemplater([
        MessageTemplate(SystemMessage('You know {{name}}.')),
        MessageTemplate(UserMessage('Hi, {{name}}!')),
    ]).render(Env(name='Frank')))
