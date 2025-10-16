"""
input: interactive, oneshot
completion: immediate, stream
rendering: raw, markdown
tools: list
prompt: yes/no
"""
import abc
import typing as ta

from omlish import lang
from ommlds import minichain as mc


##


class ToolConfirmation(lang.Abstract):
    pass


class InteractiveToolConfirmation(lang.Abstract):
    pass


##


class ChatStorage(lang.Abstract):
    pass


class InMemoryChatStorage(ChatStorage):
    pass


class JsonFileChatStorage(ChatStorage):
    pass
