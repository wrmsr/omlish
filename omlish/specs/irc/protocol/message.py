"""
TODO:
 - https://github.com/ergochat/irctest/blob/master/irctest/irc_utils/message_parser.py ?
"""
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class Message:
    source: str | None
    command: str
    params: ta.Sequence[str]

    force_trailing: bool = False

    tags: ta.Mapping[str, str] | None = None
    client_only_tags: ta.Mapping[str, str] | None = None
