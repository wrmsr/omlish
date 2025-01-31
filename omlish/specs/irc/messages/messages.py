"""
TODO:
 - PONG - optional *before* required ...
 - CAPABILITIES - ':' last param

==

https://datatracker.ietf.org/doc/html/rfc2812
https://modern.ircdocs.horse/
"""
import typing as ta

from .... import check
from .... import dataclasses as dc
from ..numerics import numerics as nr
from .base import Message
from .base import MessageFormat
from .base import list_pair_params_unpacker


#


_REGISTERED_IRC_MESSAGES_BY_NAME: dict[str, list[type['Message']]] = {}


def _register_irc_message(cls):
    check.issubclass(cls, Message)
    _REGISTERED_IRC_MESSAGES_BY_NAME.setdefault(cls.FORMAT.name, []).append(cls)
    return cls


##
# Connection Messages


@_register_irc_message
class CapMessage(Message):
    FORMAT = MessageFormat.of(
        'CAP',
        'subcommand',
        'capabilities',
    )

    subcommand: str
    capabilities: ta.Sequence[str]


@_register_irc_message
class AuthenticateMessage(Message):
    FORMAT = MessageFormat.of('AUTHENTICATE')


@_register_irc_message
class PassMessage(Message):
    FORMAT = MessageFormat.of(
        'PASS',
        'password',
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_ALREADYREGISTERED,
        nr.ERR_PASSWDMISMATCH,
    )

    password: str


@_register_irc_message
class NickMessage(Message):
    FORMAT = MessageFormat.of(
        'NICK',
        'nickname',
    )

    REPLIES = (
        nr.ERR_NONICKNAMEGIVEN,
        nr.ERR_ERRONEUSNICKNAME,
        nr.ERR_NICKNAMEINUSE,
        nr.ERR_NICKCOLLISION,
    )

    nickname: str


class UserMessage(Message):
    FORMAT = MessageFormat.of(
        'USER',
        'username',
        'param1',  # 0
        'param2',  # *
        'realname',
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_ALREADYREGISTERED,
    )

    username: str
    realname: str

    param1: str = '8'
    param2: str = '*'


@_register_irc_message
class PingMessage(Message):
    FORMAT = MessageFormat.of(
        'PING',
        'token',
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOORIGIN,
        nr.ERR_NOSUCHSERVER,
    )

    token: str


@_register_irc_message
class PongMessage(Message):
    FORMAT = MessageFormat.of(
        'PONG',
        '?server',
        'token',
    )

    token: str
    server: str | None = None


@_register_irc_message
class OperMessage(Message):
    FORMAT = MessageFormat.of(
        'OPER',
        'name',
        'password',
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_PASSWDMISMATCH,
        nr.ERR_NOOPERHOST,
        nr.RPL_YOUREOPER,
    )

    name: str
    password: str


@_register_irc_message
class QuitMessage(Message):
    FORMAT = MessageFormat.of(
        'QUIT',
        '?reason',
    )

    reason: str | None = None


@_register_irc_message
class ErrorMessage(Message):
    FORMAT = MessageFormat.of(
        'ERROR',
        '?reason',
    )

    reason: str | None = None


##
# Channel Operations


@_register_irc_message
class JoinMessage(Message):
    FORMAT = MessageFormat.of(
        'JOIN',
        ','
        'channels', '?,keys',
        unpack_params=list_pair_params_unpacker(
            'channels',
            'channels',
            'keys',
        ),
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOSUCHCHANNEL,
        nr.ERR_TOOMANYCHANNELS,
        nr.ERR_BADCHANNELKEY,
        nr.ERR_BANNEDFROMCHAN,
        nr.ERR_CHANNELISFULL,
        nr.ERR_INVITEONLYCHAN,
        nr.ERR_BADCHANMASK,
        nr.RPL_TOPIC,
        nr.RPL_TOPICWHOTIME,
        nr.RPL_NAMREPLY,
        nr.RPL_ENDOFNAMES,
    )

    channels: ta.Sequence[str | tuple[str, str]]

    @property
    def has_keys(self) -> bool:
        return check.single({isinstance(e, tuple) for e in self.channels})

    @dc.init
    def _validate_channels(self) -> None:
        check.not_isinstance(self.channels, str)
        if self.has_keys:
            for c, _ in self.channels:  # type: ignore[misc]
                check.non_empty_str(c)
        else:
            for c in self.channels:
                check.non_empty_str(c)  # type: ignore


@_register_irc_message
class LeaveAllJoinMessage(Message):
    FORMAT = MessageFormat.of(
        'JOIN',
        MessageFormat.LiteralParam('0'),
    )

    REPLIES = JoinMessage.REPLIES


@_register_irc_message
class PartMessage(Message):
    FORMAT = MessageFormat.of(
        'PART',
        ',channels',
        '?reason',
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOSUCHCHANNEL,
        nr.ERR_NOTONCHANNEL,
    )

    channels: ta.Sequence[str] = dc.xfield(validate=check.of_not_isinstance(str))
    reason: str | None = None


@_register_irc_message
class TopicMessage(Message):
    FORMAT = MessageFormat.of(
        'TOPIC',
        'channel',
        '?topic',
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOSUCHCHANNEL,
        nr.ERR_NOTONCHANNEL,
        nr.ERR_CHANOPRIVSNEEDED,
        nr.RPL_NOTOPIC,
        nr.RPL_TOPIC,
        nr.RPL_TOPICWHOTIME,
    )

    channel: str
    topic: str | None = None


@_register_irc_message
class NamesMessage(Message):
    FORMAT = MessageFormat.of(
        'NAMES',
        ',channels',
    )

    REPLIES = (
        nr.RPL_NAMREPLY,
        nr.RPL_ENDOFNAMES,
    )

    channels: ta.Sequence[str] = dc.xfield(validate=check.of_not_isinstance(str))


@_register_irc_message
class ListMessage(Message):
    FORMAT = MessageFormat.of(
        'LIST',
        '?,channels',
        '?,elistconds',
    )

    REPLIES = (
        nr.RPL_LISTSTART,
        nr.RPL_LIST,
        nr.RPL_LISTEND,
    )

    channels: ta.Sequence[str]
    elistconds: ta.Sequence[str]


@_register_irc_message
class InviteMessage(Message):
    FORMAT = MessageFormat.of(
        'INVITE',
        'nickname',
        'channel',
    )

    REPLIES = (
        nr.RPL_INVITING,
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOSUCHCHANNEL,
        nr.ERR_NOTONCHANNEL,
        nr.ERR_CHANOPRIVSNEEDED,
        nr.ERR_USERONCHANNEL,
    )

    nickname: str
    channel: str


@_register_irc_message
class KickMessage(Message):
    FORMAT = MessageFormat.of(
        'KICK',
        'channel',
        ',users',
        '?comment',
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOSUCHCHANNEL,
        nr.ERR_CHANOPRIVSNEEDED,
        nr.ERR_USERNOTINCHANNEL,
        nr.ERR_NOTONCHANNEL,
        nr.ERR_BADCHANMASK,
    )

    channel: str
    users: ta.Sequence[str]
    comment: str | None = None


##
# Server Queries and Commands


@_register_irc_message
class MotdMessage(Message):
    FORMAT = MessageFormat.of(
        'MOTD',
        '?target',
    )

    REPLIES = (
        nr.ERR_NOSUCHSERVER,
        nr.ERR_NOMOTD,
        nr.RPL_MOTDSTART,
        nr.RPL_MOTD,
        nr.RPL_ENDOFMOTD,
    )

    target: str | None = None


@_register_irc_message
class VersionMessage(Message):
    FORMAT = MessageFormat.of(
        'VERSION',
        '?target',
    )

    REPLIES = (
        nr.ERR_NOSUCHSERVER,
        nr.RPL_ISUPPORT,
        nr.RPL_VERSION,
    )

    target: str | None = None


@_register_irc_message
class AdminMessage(Message):
    FORMAT = MessageFormat.of(
        'ADMIN',
        '?target',
    )

    REPLIES = (
        nr.ERR_NOSUCHSERVER,
        nr.RPL_ADMINME,
        nr.RPL_ADMINLOC1,
        nr.RPL_ADMINLOC2,
        nr.RPL_ADMINEMAIL,
    )

    target: str | None = None


@_register_irc_message
class ConnectMessage(Message):
    FORMAT = MessageFormat.of(
        'CONNECT',
        'target_server',
        '?port',
        '?remote_server',
    )

    REPLIES = (
        nr.ERR_NOSUCHSERVER,
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOPRIVILEGES,
        nr.ERR_NOPRIVS,
    )

    target_server: str
    port: str | None = None
    remote_server: str | None = None


@_register_irc_message
class LusersMessage(Message):
    FORMAT = MessageFormat.of('LUSERS')

    REPLIES = (
        nr.RPL_LUSERCLIENT,
        nr.RPL_LUSEROP,
        nr.RPL_LUSERUNKNOWN,
        nr.RPL_LUSERCHANNELS,
        nr.RPL_LUSERME,
        nr.RPL_LOCALUSERS,
        nr.RPL_GLOBALUSERS,
    )


@_register_irc_message
class TimeMessage(Message):
    FORMAT = MessageFormat.of(
        'TIME',
        '?server',
    )

    REPLIES = (
        nr.ERR_NOSUCHSERVER,
        nr.RPL_TIME,
    )

    server: str | None = None


@_register_irc_message
class StatsMessage(Message):
    FORMAT = MessageFormat.of(
        'STATS',
        'query',
        '?server',
    )

    REPLIES = (
        nr.ERR_NOSUCHSERVER,
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOPRIVILEGES,
        nr.ERR_NOPRIVS,
        nr.RPL_STATSCLINE,
        nr.RPL_STATSHLINE,
        nr.RPL_STATSILINE,
        nr.RPL_STATSKLINE,
        nr.RPL_STATSLLINE,
        nr.RPL_STATSOLINE,
        nr.RPL_STATSLINKINFO,
        nr.RPL_STATSUPTIME,
        nr.RPL_STATSCOMMANDS,
        nr.RPL_ENDOFSTATS,
    )

    query: str
    server: str | None = None


@_register_irc_message
class HelpMessage(Message):
    FORMAT = MessageFormat.of(
        'HELP',
        '?subject',
    )

    REPLIES = (
        nr.ERR_HELPNOTFOUND,
        nr.RPL_HELPSTART,
        nr.RPL_HELPTXT,
        nr.RPL_ENDOFHELP,
    )

    subject: str | None = None


@_register_irc_message
class InfoMessage(Message):
    FORMAT = MessageFormat.of('INFO')

    REPLIES = (
        nr.RPL_INFO,
        nr.RPL_ENDOFINFO,
    )


@_register_irc_message
class ModeMessage(Message):
    FORMAT = MessageFormat.of(
        'MODE',
        'target',
        '?modestring',
        '*mode_arguments',
    )

    REPLIES = (
        nr.ERR_NOSUCHCHANNEL,
        nr.RPL_CHANNELMODEIS,
        nr.RPL_CREATIONTIME,
        nr.RPL_CHANNELMODEIS,
        nr.ERR_CHANOPRIVSNEEDED,
        nr.RPL_BANLIST,
        nr.RPL_ENDOFBANLIST,
        nr.RPL_EXCEPTLIST,
        nr.RPL_ENDOFEXCEPTLIST,
        nr.RPL_INVITELIST,
        nr.RPL_ENDOFINVITELIST,
    )

    target: str
    modestring: str | None = None
    mode_arguments: ta.Sequence[str] | None = None


##
# Sending Messages


@_register_irc_message
class PrivmsgMessage(Message):
    FORMAT = MessageFormat.of(
        'PRIVMSG',
        ',targets',
        'text',
    )

    REPLIES = (
        nr.ERR_NOSUCHNICK,
        nr.ERR_NOSUCHSERVER,
        nr.ERR_CANNOTSENDTOCHAN,
        nr.ERR_TOOMANYTARGETS,
        nr.ERR_NORECIPIENT,
        nr.ERR_NOTEXTTOSEND,
        nr.ERR_NOTOPLEVEL,
        nr.ERR_WILDTOPLEVEL,
        nr.RPL_AWAY,
    )

    targets: ta.Sequence[str]
    text: str


@_register_irc_message
class NoticeMessage(Message):
    FORMAT = MessageFormat.of(
        'NOTICE',
        ',targets',
        'text',
    )

    targets: ta.Sequence[str]
    text: str


##
# User-Based Queries

@_register_irc_message
class WhoMessage(Message):
    FORMAT = MessageFormat.of(
        'WHO',
        'mask',
    )

    REPLIES = (
        nr.RPL_WHOREPLY,
        nr.RPL_ENDOFWHO,
    )

    mask: str


@_register_irc_message
class WhoisMessage(Message):
    FORMAT = MessageFormat.of(
        'WHOIS',
        '?target',
        'nick',
    )

    REPLIES = (
        nr.ERR_NOSUCHNICK,
        nr.ERR_NOSUCHSERVER,
        nr.ERR_NONICKNAMEGIVEN,
        nr.RPL_WHOISCERTFP,
        nr.RPL_WHOISREGNICK,
        nr.RPL_WHOISUSER,
        nr.RPL_WHOISSERVER,
        nr.RPL_WHOISOPERATOR,
        nr.RPL_WHOISIDLE,
        nr.RPL_WHOISCHANNELS,
        nr.RPL_WHOISSPECIAL,
        nr.RPL_WHOISACCOUNT,
        nr.RPL_WHOISACTUALLY,
        nr.RPL_WHOISHOST,
        nr.RPL_WHOISMODES,
        nr.RPL_WHOISSECURE,
        nr.RPL_AWAY,
    )

    nick: str
    target: str | None = None


@_register_irc_message
class WhowasMessage(Message):
    FORMAT = MessageFormat.of(
        'WHOWAS',
        'nick',
        '?count',
    )

    REPLIES = (
        nr.ERR_WASNOSUCHNICK,
        nr.RPL_ENDOFWHOWAS,
        nr.RPL_WHOWASUSER,
        nr.RPL_WHOISACTUALLY,
        nr.RPL_WHOISSERVER,
        nr.RPL_WHOWASUSER,
        nr.ERR_NONICKNAMEGIVEN,
        nr.ERR_NEEDMOREPARAMS,
    )

    nick: str
    count: str | None = None


##
# Operator Messages


@_register_irc_message
class KillMessage(Message):
    FORMAT = MessageFormat.of(
        'KILL',
        'nickname',
        'comment',
    )

    REPLIES = (
        nr.ERR_NOSUCHSERVER,
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOPRIVILEGES,
        nr.ERR_NOPRIVS,
    )

    nickname: str
    comment: str


@_register_irc_message
class RehashMessage(Message):
    FORMAT = MessageFormat.of('REHASH')

    REPLIES = (
        nr.RPL_REHASHING,
        nr.ERR_NOPRIVILEGES,
    )


@_register_irc_message
class RestartMessage(Message):
    FORMAT = MessageFormat.of('RESTART')

    REPLIES = (
        nr.ERR_NOPRIVILEGES,
    )


@_register_irc_message
class SquitMessage(Message):
    FORMAT = MessageFormat.of(
        'SQUIT',
        'server',
        'comment',
    )

    REPLIES = (
        nr.ERR_NOSUCHSERVER,
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOPRIVILEGES,
        nr.ERR_NOPRIVS,
    )

    server: str
    comment: str


##
# Optional Messages


@_register_irc_message
class AwayMessage(Message):
    FORMAT = MessageFormat.of(
        'AWAY',
        '?text',
    )

    REPLIES = (
        nr.RPL_AWAY,
        nr.RPL_UNAWAY,
        nr.RPL_NOWAWAY,
    )

    text: str | None = None


@_register_irc_message
class LinksMessage(Message):
    FORMAT = MessageFormat.of('LINKS')

    REPLIES = (
        nr.RPL_LINKS,
        nr.RPL_ENDOFLINKS,
    )


@_register_irc_message
class UserhostMessage(Message):
    FORMAT = MessageFormat.of(
        'USERHOST',
        '*nicknames',
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.RPL_USERHOST,
    )

    nicknames: ta.Sequence[str] | None = dc.xfield(default=None, validate=check.of_not_isinstance(str))


@_register_irc_message
class WallopsMessage(Message):
    FORMAT = MessageFormat.of(
        'WALLOPS',
        'text',
    )

    REPLIES = (
        nr.ERR_NEEDMOREPARAMS,
        nr.ERR_NOPRIVILEGES,
        nr.ERR_NOPRIVS,
    )

    text: str
