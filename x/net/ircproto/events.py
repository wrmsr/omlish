import codecs
import typing as ta

from . import constants as consts
from .exceptions import ProtocolError
from .exceptions import UnknownCommandError


class IrcEvent:
    """
    Base class for all IRC events.

    :ivar sender: either a server host name or nickname!username@host
    """

    def __init__(self, sender: str | None) -> None:
        super().__init__()

        self.sender = sender

    def encode(self, *params: ta.Any) -> str:
        """
        Encode the event into a string.

        :return: a unicode string ending in CRLF
        :raises ProtocolError: if any parameter save the last one contains spaces
        """

        buffer = ''
        if self.sender:
            buffer += ':' + self.sender + ' '

        for i, param in enumerate(params):
            if not param:
                continue

            if ' ' in param:
                if i == len(params) - 1:
                    param = ':' + param
                else:
                    raise ProtocolError('only the last parameter can contain spaces')

            if i > 0:
                buffer += ' '
            buffer += param

        return buffer + '\r\n'


class Command(IrcEvent):
    """
    Base class for all command events.

    :var str command: the associated command word
    :var bool privileged: ``True`` if this command requires IRC operator privileges
    :var tuple allowed_replies: allowed reply codes for this command
    """

    command: str | None = None
    privileged: bool = False
    allowed_replies: frozenset[int] = ()

    def process_reply(self, code):
        if code not in consts.REPLY_NAMES:
            raise ProtocolError(f'{code} is not a known reply code')

        if code not in self.allowed_replies:
            code_name = consts.REPLY_NAMES[code]
            raise ProtocolError(f'reply code {code_name} is not allowed for {self.command}')

        return True

    @classmethod
    def decode(cls, sender, *params):
        try:
            return cls(sender, *params)
        except TypeError:
            raise ProtocolError(f'wrong number of arguments for {cls.command}')  # noqa

    def encode(self, *params):
        return super().encode(self.command, *params)


class Reply(IrcEvent):
    """
    Represents a numeric reply from a server to a client.

    :ivar int code: a numeric reply code
    :ivar str message: the reply message
    """

    def __init__(self, sender, code, message):
        super().__init__(sender)
        self.code = int(code)
        self.message = message

    @property
    def is_error(self):
        """Return ``True`` if this is an error reply, ``False`` otherwise."""
        return self.code >= 400

    def encode(self):
        return super().encode(str(self.code), self.message)


# Section 3.1.1
class Password(Command):
    command = 'PASS'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_ALREADYREGISTRED,
    ])

    def __init__(self, sender, password):
        super().__init__(sender)
        self.password = password

    def encode(self):
        return super().encode(self.password)


# Section 3.1.2
class Nick(Command):
    command = 'NICK'
    allowed_replies = frozenset([
        consts.ERR_NONICKNAMEGIVEN,
        consts.ERR_ERRONEUSNICKNAME,
        consts.ERR_NICKNAMEINUSE,
        consts.ERR_NICKCOLLISION,
        consts.ERR_UNAVAILRESOURCE,
        consts.ERR_RESTRICTED,
    ])

    def __init__(self, sender, nickname):
        super().__init__(sender)
        self.nickname = nickname

    def encode(self):
        return super().encode(self.nickname)


# Section 3.1.3
class User(Command):
    command = 'USER'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_ALREADYREGISTRED,
    ])

    def __init__(self, sender, user, mode, realname):
        super().__init__(sender)
        self.user = user
        self.mode = mode
        self.realname = realname

    @classmethod
    def decode(cls, sender, *params):
        return super().decode(sender, params[0], params[1], params[3])

    def encode(self):
        return super().encode(self.user, self.mode, '*', self.realname)


# Section 3.1.4
class Oper(Command):
    command = 'OPER'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_NOOPERHOST,
        consts.ERR_PASSWDMISMATCH,
        consts.RPL_YOUREOPER,
    ])

    def __init__(self, sender, name, password):
        super().__init__(sender)
        self.name = name
        self.password = password

    def encode(self):
        return super().encode(self.name, self.password)


# Section 3.1.5 / 3.2.3
class Mode(Command):
    command = 'MODE'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_USERSDONTMATCH,
        consts.ERR_UMODEUNKNOWNFLAG,
        consts.RPL_UMODEIS,
    ])

    def __init__(self, sender, target, modes, *modeparams):
        super().__init__(sender)
        self.target = target
        self.modes = modes
        self.modeparams = modeparams

    def encode(self):
        return super().encode(self.target, self.modes, *self.modeparams)


# Section 3.1.6
class Service(Command):
    command = 'SERVICE'
    allowed_replies = frozenset([
        consts.ERR_ALREADYREGISTRED,
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_ERRONEUSNICKNAME,
        consts.RPL_YOURESERVICE,
        consts.RPL_YOURHOST,
        consts.RPL_MYINFO,
    ])

    def __init__(self, sender, nickname, distribution, type_, info):
        super().__init__(sender)
        self.nickname = nickname
        self.distribution = distribution
        self.type = type_
        self.info = info

    def encode(self):
        return super().encode(self.nickname, '*', self.distribution, self.type, '*', self.info)


# Section 3.1.7
class Quit(Command):
    command = 'QUIT'

    def __init__(self, sender, message=None):
        super().__init__(sender)
        self.message = message

    def encode(self):
        return super().encode(self.message)


# Section 3.1.8
class SQuit(Command):
    command = 'SQUIT'
    privileged = True
    allowed_replies = frozenset([
        consts.ERR_NOPRIVILEGES,
        consts.ERR_NOSUCHSERVER,
        consts.ERR_NEEDMOREPARAMS,
    ])

    def __init__(self, sender, server, comment):
        super().__init__(sender)
        self.server = server
        self.comment = comment

    def encode(self):
        return super().encode(self.server, self.comment)


# Section 3.2.1
class Join(Command):
    command = 'JOIN'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_BANNEDFROMCHAN,
        consts.ERR_INVITEONLYCHAN,
        consts.ERR_BADCHANNELKEY,
        consts.ERR_CHANNELISFULL,
        consts.ERR_BADCHANMASK,
        consts.ERR_NOSUCHCHANNEL,
        consts.ERR_TOOMANYCHANNELS,
        consts.ERR_TOOMANYTARGETS,
        consts.ERR_UNAVAILRESOURCE,
        consts.RPL_TOPIC,
    ])

    def __init__(self, sender, channel, key=None):
        super().__init__(sender)
        self.channel = channel
        self.key = key

    def encode(self):
        return super().encode(self.channel, self.key)


# Section 3.2.2
class Part(Command):
    command = 'PART'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_NOSUCHCHANNEL,
        consts.ERR_NOTONCHANNEL,
    ])

    def __init__(self, sender, channel, message=None):
        super().__init__(sender)
        self.channel = channel
        self.message = message

    def encode(self):
        return super().encode(self.channel, self.message)


# Section 3.2.4
class Topic(Command):
    command = 'TOPIC'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_NOTONCHANNEL,
        consts.RPL_NOTOPIC,
        consts.RPL_TOPIC,
        consts.ERR_CHANOPRIVSNEEDED,
        consts.ERR_NOCHANMODES,
    ])

    def __init__(self, sender, channel, topic):
        super().__init__(sender)
        self.channel = channel
        self.topic = topic

    def encode(self, *params):
        return super().encode(self.channel, self.topic)


# Section 3.2.5
class Names(Command):
    command = 'NAMES'
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.RPL_NAMREPLY,
        consts.RPL_ENDOFNAMES,
    ])


# Section 3.2.6
class List(Command):
    command = 'LIST'
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.RPL_LIST,
        consts.RPL_LISTEND,
    ])


# Section 3.2.7
class Invite(Command):
    command = 'INVITE'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_NOSUCHNICK,
        consts.ERR_NOTONCHANNEL,
        consts.ERR_USERONCHANNEL,
        consts.ERR_CHANOPRIVSNEEDED,
        consts.RPL_INVITING,
        consts.RPL_AWAY,
    ])

    def __init__(self, sender, nickname, channel):
        super().__init__(sender)
        self.nickname = nickname
        self.channel = channel

    def encode(self):
        return super().encode(self.nickname, self.channel)


# Section 3.2.8
class Kick(Command):
    command = 'KICK'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_NOSUCHCHANNEL,
        consts.ERR_BADCHANMASK,
        consts.ERR_CHANOPRIVSNEEDED,
        consts.ERR_USERNOTINCHANNEL,
        consts.ERR_NOTONCHANNEL,
    ])

    def __init__(self, sender, channel, nickname, comment=None):
        super().__init__(sender)
        self.channel = channel
        self.nickname = nickname
        self.comment = comment

    def encode(self):
        return super().encode(self.channel, self.nickname, self.comment)


# Section 3.3.1
class PrivateMessage(Command):
    command = 'PRIVMSG'
    allowed_replies = frozenset([
        consts.ERR_NORECIPIENT,
        consts.ERR_NOTEXTTOSEND,
        consts.ERR_CANNOTSENDTOCHAN,
        consts.ERR_NOTOPLEVEL,
        consts.ERR_WILDTOPLEVEL,
        consts.ERR_TOOMANYTARGETS,
        consts.ERR_NOSUCHNICK,
        consts.RPL_AWAY,
    ])

    def __init__(self, sender, recipient, message):
        super().__init__(sender)
        self.recipient = recipient
        self.message = message

    def encode(self):
        return super().encode(self.recipient, self.message)


# Section 3.3.2
class Notice(Command):
    command = 'NOTICE'
    allowed_replies = frozenset([
        consts.ERR_NORECIPIENT,
        consts.ERR_NOTEXTTOSEND,
        consts.ERR_CANNOTSENDTOCHAN,
        consts.ERR_NOTOPLEVEL,
        consts.ERR_WILDTOPLEVEL,
        consts.ERR_TOOMANYTARGETS,
        consts.ERR_NOSUCHNICK,
    ])

    def __init__(self, sender, recipient, message):
        super().__init__(sender)
        self.recipient = recipient
        self.message = message

    @classmethod
    def decode(cls, sender, *params):
        recipient, message = params
        if message.startswith('\x01'):
            return CTCPMessage(sender, recipient, message[1:-1])
        else:
            return Notice(sender, *params)

    def encode(self):
        return super().encode(self.recipient, self.message)


class CTCPMessage(IrcEvent):
    """
    Represents a client-to-client protocol message.

    :ivar str recipient:
    """

    def __init__(self, sender, recipient, message):
        super().__init__(sender)
        self.recipient = recipient
        self.message = message

    def encode(self):
        return super().encode(self.recipient, '\x01' + self.message + '\x01')


# Section 3.4.1
class Motd(Command):
    command = 'MOTD'
    allowed_replies = frozenset([
        consts.RPL_MOTDSTART,
        consts.RPL_MOTD,
        consts.RPL_ENDOFMOTD,
        consts.ERR_NOMOTD,
    ])

    def __init__(self, sender, target=None):
        super().__init__(sender)
        self.target = target

    def encode(self):
        return super().encode(self.target)


# Section 3.4.2
class Lusers(Command):
    command = 'LUSERS'
    allowed_replies = frozenset([
        consts.RPL_LUSERCLIENT,
        consts.RPL_LUSEROP,
        consts.RPL_LUSERUNKNOWN,
        consts.RPL_LUSERCHANNELS,
        consts.RPL_LUSERME,
        consts.ERR_NOSUCHSERVER,
    ])

    def __init__(self, sender, mask=None, target=None):
        super().__init__(sender)
        self.mask = mask
        self.target = target

    def encode(self):
        return super().encode(self.mask, self.target)


# Section 3.4.3
class Version(Command):
    command = 'VERSION'
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.RPL_VERSION,
    ])

    def __init__(self, sender, target=None):
        super().__init__(sender)
        self.target = target

    def encode(self):
        return super().encode(self.target)


# Section 3.4.4
class Stats(Command):
    command = 'STATS'
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.RPL_STATSLINKINFO,
        consts.RPL_STATSUPTIME,
        consts.RPL_STATSCOMMANDS,
        consts.RPL_STATSOLINE,
        consts.RPL_ENDOFSTATS,
    ])

    def __init__(self, sender, query=None, target=None):
        super().__init__(sender)
        self.query = query
        self.target = target

    def encode(self):
        return super().encode(self.query, self.target)


# Section 3.4.5
class Links(Command):
    command = 'LINKS'
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.RPL_STATSLINKINFO,
        consts.RPL_STATSUPTIME,
        consts.RPL_STATSCOMMANDS,
        consts.RPL_STATSOLINE,
        consts.RPL_ENDOFSTATS,
    ])

    def __init__(self, sender, remote_server=None, server_mask=None):
        super().__init__(sender)
        self.remote_server = remote_server
        self.server_mask = server_mask

    def encode(self):
        return super().encode(self.remote_server, self.server_mask)


# Section 3.4.6
class Time(Command):
    command = 'TIME'
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.RPL_TIME,
    ])

    def __init__(self, sender, target=None):
        super().__init__(sender)
        self.target = target

    def encode(self):
        return super().encode(self.target)


# Section 3.4.7
class Connect(Command):
    command = 'CONNECT'
    privileged = True
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.ERR_NOPRIVILEGES,
        consts.ERR_NEEDMOREPARAMS,
    ])

    def __init__(self, sender, target_server, port, remote_server=None):
        super().__init__(sender)
        self.target_server = target_server
        self.port = int(port)
        self.remote_server = remote_server

    def encode(self):
        return super().encode(self.target_server, self.port, self.remote_server)


# Section 3.4.8
class Trace(Command):
    command = 'TRACE'
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.RPL_TRACELINK,
        consts.RPL_TRACECONNECTING,
        consts.RPL_TRACEHANDSHAKE,
        consts.RPL_TRACEUNKNOWN,
        consts.RPL_TRACEOPERATOR,
        consts.RPL_TRACEUSER,
        consts.RPL_TRACESERVER,
        consts.RPL_TRACESERVICE,
        consts.RPL_TRACENEWTYPE,
        consts.RPL_TRACECLASS,
        consts.RPL_TRACELOG,
        consts.RPL_TRACEEND,
    ])

    def __init__(self, sender, target=None):
        super().__init__(sender)
        self.target = target

    def encode(self):
        return super().encode(self.target)


# Section 3.4.9
class Admin(Command):
    command = 'ADMIN'
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.RPL_ADMINME,
        consts.RPL_ADMINLOC1,
        consts.RPL_ADMINLOC2,
        consts.RPL_ADMINEMAIL,
    ])

    def __init__(self, sender, target=None):
        super().__init__(sender)
        self.target = target

    def encode(self):
        return super().encode(self.target)


# Section 3.4.10
class Info(Command):
    command = 'INFO'
    allowed_replies = frozenset([
        consts.ERR_NOSUCHSERVER,
        consts.RPL_INFO,
        consts.RPL_ENDOFINFO,
    ])

    def __init__(self, sender, target=None):
        super().__init__(sender)
        self.target = target

    def encode(self):
        return super().encode(self.target)


# Section 3.7.1
class Kill(Command):
    command = 'KILL'
    privileged = True
    allowed_replies = frozenset([
        consts.ERR_NOPRIVILEGES,
        consts.ERR_NEEDMOREPARAMS,
        consts.ERR_NOSUCHNICK,
        consts.ERR_CANTKILLSERVER,
    ])

    def __init__(self, sender, nickname, comment):
        super().__init__(sender)
        self.nickname = nickname
        self.comment = comment

    def encode(self):
        return super().encode(self.nickname, self.comment)


# Section 3.7.2
class Ping(Command):
    command = 'PING'
    allowed_replies = frozenset([
        consts.ERR_NOORIGIN,
        consts.ERR_NOSUCHSERVER,
    ])

    def __init__(self, sender, server1, server2=None):
        super().__init__(sender)
        self.server1 = server1
        self.server2 = server2

    def encode(self):
        return super().encode(self.server1, self.server2)


# Section 3.7.3
class Pong(Command):
    command = 'PONG'
    allowed_replies = frozenset([
        consts.ERR_NOORIGIN,
        consts.ERR_NOSUCHSERVER,
    ])

    def __init__(self, sender, server1, server2=None):
        super().__init__(sender)
        self.server1 = server1
        self.server2 = server2

    def encode(self):
        return super().encode(self.server1, self.server2)


# Section 3.7.4
class Error(Command):
    command = 'ERROR'

    def __init__(self, sender, message):
        super().__init__(sender)
        self.message = message

    def encode(self):
        return super().encode(self.message)


# Section 4.1
class Away(Command):
    command = 'AWAY'
    allowed_replies = frozenset([
        consts.RPL_UNAWAY,
        consts.RPL_NOWAWAY,
    ])

    def __init__(self, sender, text=None):
        super().__init__(sender)
        self.text = text

    def encode(self):
        return super().encode(self.text)


# Section 4.2
class Rehash(Command):
    command = 'REHASH'
    privileged = True
    allowed_replies = frozenset([
        consts.RPL_REHASHING,
        consts.ERR_NOPRIVILEGES,
    ])


# Section 4.3
class Die(Command):
    command = 'DIE'
    privileged = True
    allowed_replies = frozenset([
        consts.ERR_NOPRIVILEGES,
    ])


# Section 4.3
class Restart(Command):
    command = 'RESTART'
    privileged = True
    allowed_replies = frozenset([
        consts.ERR_NOPRIVILEGES,
    ])


# Section 4.5
class Summon(Command):
    command = 'SUMMON'
    allowed_replies = frozenset([
        consts.ERR_NORECIPIENT,
        consts.ERR_FILEERROR,
        consts.ERR_NOLOGIN,
        consts.ERR_NOSUCHSERVER,
        consts.ERR_SUMMONDISABLED,
        consts.RPL_SUMMONING,
    ])

    def __init__(self, sender, user, target=None, channel=None):
        super().__init__(sender)
        self.user = user
        self.target = target
        self.channel = channel

    def encode(self):
        return super().encode(self.user, self.target, self.channel)


# Section 4.6
class Users(Command):
    command = 'USERS'
    allowed_replies = frozenset([
        consts.ERR_NORECIPIENT,
        consts.ERR_FILEERROR,
        consts.ERR_NOLOGIN,
        consts.ERR_NOSUCHSERVER,
        consts.ERR_SUMMONDISABLED,
        consts.RPL_SUMMONING,
    ])

    def __init__(self, sender, target=None):
        super().__init__(sender)
        self.target = target

    def encode(self):
        return super().encode(self.target)


# Section 4.7
class Operwall(Command):
    command = 'WALLOPS'
    allowed_replies = frozenset([
        consts.ERR_NEEDMOREPARAMS,
    ])

    def __init__(self, sender, text=None):
        super().__init__(sender)
        self.text = text

    def encode(self):
        return super().encode(self.text)


# Section 4.8
class Userhost(Command):
    command = 'USERHOST'
    allowed_replies = frozenset([
        consts.RPL_USERHOST,
        consts.ERR_NEEDMOREPARAMS,
    ])

    def __init__(self, sender, nickname, *nicknames):
        super().__init__(sender)
        self.nicknames = (nickname, *nicknames)

    def encode(self):
        return super().encode(*self.nicknames)


# Section 4.9
class Ison(Command):
    command = 'ISON'
    allowed_replies = frozenset([
        consts.RPL_ISON,
        consts.ERR_NEEDMOREPARAMS,
    ])

    def __init__(self, sender, nickname, *nicknames):
        super().__init__(sender)
        self.nicknames = (nickname, *nicknames)

    def encode(self):
        return super().encode(*self.nicknames)


COMMANDS: ta.Mapping[str, type[Command]] = {
    cls.command: cls
    for cls in Command.__subclasses__()
}


Decoder: ta.TypeAlias = ta.Callable[[bytes | bytearray], tuple[str, int]]


def decode_event(
        buffer: bytearray,
        decoder: Decoder = codecs.getdecoder('utf-8'),
        fallback_decoder: Decoder = codecs.getdecoder('iso-8859-1'),
) -> IrcEvent | None:
    end_index = buffer.find(b'\r\n')
    if end_index == -1:
        return None
    elif end_index > 510:
        # Section 2.3
        raise ProtocolError(f'received oversized message ({end_index + 2} bytes)')

    try:
        message = decoder(buffer[:end_index])[0]
    except UnicodeDecodeError:
        message = fallback_decoder(buffer[:end_index], 'replace')[0]

    del buffer[:end_index + 2]

    if message[0] == ':':
        prefix, _, rest = message[1:].partition(' ')
        command, _, rest = rest.partition(' ')
    else:
        prefix = None
        command, _, rest = message.partition(' ')

    if command.isdigit():
        return Reply(prefix, command, rest)

    try:
        command_class = COMMANDS[command]
    except KeyError:
        raise UnknownCommandError(command)  # noqa

    params = []
    if rest:
        parts = rest.split(' ')
        for i, param in enumerate(parts):
            if param.startswith(':'):
                param = param[1:]
                if parts[i + 1:]:
                    param += ' ' + ' '.join(parts[i + 1:])

                params.append(param)
                break
            elif param:
                params.append(param)

    return command_class.decode(prefix, *params)
