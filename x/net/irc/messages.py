import typing as ta

from ... import check
from ... import dataclasses as dc


MESSAGES: ta.Sequence['Message'] = []
MESSAGES_BY_NAME: ta.Mapping[str, 'Message'] = {}


class Message(dc.Pure):
    name: str
    parameters: str
    replies: ta.Iterable[str]

    def __post_init__(self) -> None:
        check.not_in(self.name, MESSAGES_BY_NAME)
        MESSAGES.append(self)
        MESSAGES_BY_NAME[self.name] = self


PASS = Message(
    'PASS',
    '<password>',
    {
        'ERR_NEEDMOREPARAMS',
        'ERR_ALREADYREGISTRED',
    },
)

NICK = Message(
    'NICK',
    '<nickname>',
    {
        'ERR_NONICKNAMEGIVEN',
        'ERR_ERRONEUSNICKNAME',
        'ERR_NICKNAMEINUSE',
        'ERR_NICKCOLLISION',
        'ERR_UNAVAILRESOURCE',
        'ERR_RESTRICTED',
    },
)

USER = Message(
    'USER',
    '<user> <mode> <unused> <realname>',
    {
        'ERR_NEEDMOREPARAMS',
        'ERR_ALREADYREGISTRED',
    },
)

OPER = Message(
    'OPER',
    '<name> <password>',
    {
        'ERR_NEEDMOREPARAMS',
        'RPL_YOUREOPER',
        'ERR_NOOPERHOST',
        'ERR_PASSWDMISMATCH',
    },
)

MODE = Message(
    'MODE',
    '(<nickname> *( ( "+" / "-" ) *( "i" / "w" / "o" / "O" / "r" ) )) | '  # nick
    '(<channel> *( ( "-" / "+" ) *<modes> *<modeparams> ))',  # chan
    {  # nick
        'ERR_NEEDMOREPARAMS',
        'ERR_USERSDONTMATCH',
        'ERR_UMODEUNKNOWNFLAG',
        'RPL_UMODEIS',
    } |
    {  # chan
        'ERR_NEEDMOREPARAMS',
        'ERR_KEYSET',
        'ERR_NOCHANMODES',
        'ERR_CHANOPRIVSNEEDED',
        'ERR_USERNOTINCHANNEL',
        'ERR_UNKNOWNMODE',
        'RPL_CHANNELMODEIS',
        'RPL_BANLIST',
        'RPL_ENDOFBANLIST',
        'RPL_EXCEPTLIST',
        'RPL_ENDOFEXCEPTLIST',
        'RPL_INVITELIST',
        'RPL_ENDOFINVITELIST',
        'RPL_UNIQOPIS',
    },
)

SERVICE = Message(
    'SERVICE',
    '<nickname> <reserved> <distribution> <type> <reserved> <info>',
    {
        'ERR_ALREADYREGISTRED',
        'ERR_NEEDMOREPARAMS',
        'ERR_ERRONEUSNICKNAME',
        'RPL_YOURESERVICE',
        'RPL_YOURHOST',
        'RPL_MYINFO',
    },
)

QUIT = Message(
    'QUIT',

    '[ <Quit Message> ]',
    set(),
)

SQUIT = Message(
    'SQUIT',
    '<server> <comment>',
    {
        'ERR_NOPRIVILEGES',
        'ERR_NOSUCHSERVER',
        'ERR_NEEDMOREPARAMS',
    },
)

JOIN = Message(
    'JOIN',
    '( <channel> *( "," <channel> ) [ <key> *( "," <key> ) ] ) / "0"',
    {
        'ERR_NEEDMOREPARAMS',
        'ERR_BANNEDFROMCHAN',
        'ERR_INVITEONLYCHAN',
        'ERR_BADCHANNELKEY',
        'ERR_CHANNELISFULL',
        'ERR_BADCHANMASK',
        'ERR_NOSUCHCHANNEL',
        'ERR_TOOMANYCHANNELS',
        'ERR_TOOMANYTARGETS',
        'ERR_UNAVAILRESOURCE',
        'RPL_TOPIC',
    },
)

PART = Message(
    'PART',
    '<channel> *( "," <channel> ) [ <Part Message> ]',
    {
        'ERR_NEEDMOREPARAMS',
        'ERR_NOSUCHCHANNEL',
        'ERR_NOTONCHANNEL',
    },
)

TOPIC = Message(
    'TOPIC',
    '<channel> [ <topic> ]',
    {
        'ERR_NEEDMOREPARAMS',
        'ERR_NOTONCHANNEL',
        'RPL_NOTOPIC',
        'RPL_TOPIC',
        'ERR_CHANOPRIVSNEEDED',
        'ERR_NOCHANMODES',
    },
)

NAMES = Message(
    'NAMES',
    '[ <channel> *( "," <channel> ) [ <target> ] ]',
    {
        'ERR_TOOMANYMATCHES',
        'ERR_NOSUCHSERVER',
        'RPL_NAMREPLY',
        'RPL_ENDOFNAMES',
    },
)

LIST = Message(
    'LIST',
    '[ <channel> *( "," <channel> ) [ <target> ] ]',
    {
        'ERR_TOOMANYMATCHES',
        'ERR_NOSUCHSERVER',
        'RPL_LIST',
        'RPL_LISTEND',
    },
)

INVITE = Message(
    'INVITE',
    '<nickname> <channel>',
    {
        'ERR_NEEDMOREPARAMS',
        'ERR_NOSUCHNICK',
        'ERR_NOTONCHANNEL',
        'ERR_USERONCHANNEL',
        'ERR_CHANOPRIVSNEEDED',
        'RPL_INVITING',
        'RPL_AWAY',
    },
)

KICK = Message(
    'KICK',
    '<channel> *( "," <channel> ) <user> *( "," <user> ) [<comment>]',
    {
        'ERR_NEEDMOREPARAMS',
        'ERR_NOSUCHCHANNEL',
        'ERR_BADCHANMASK',
        'ERR_CHANOPRIVSNEEDED',
        'ERR_USERNOTINCHANNEL',
        'ERR_NOTONCHANNEL',
    },
)

PRIVMSG = Message(
    'PRIVMSG',
    '<msgtarget> <text to be sent>',
    {
        'ERR_NORECIPIENT',
        'ERR_NOTEXTTOSEND',
        'ERR_CANNOTSENDTOCHAN',
        'ERR_NOTOPLEVEL',
        'ERR_WILDTOPLEVEL',
        'ERR_TOOMANYTARGETS',
        'ERR_NOSUCHNICK',
        'RPL_AWAY',
    },
)

NOTICE = Message(
    'NOTICE',
    '<msgtarget> <text>',
    {
        'RPL_MOTDSTART',
        'RPL_MOTD',
        'RPL_ENDOFMOTD',
        'ERR_NOMOTD',
    },
)

LUSERS = Message(
    'LUSERS',
    '[ <mask> [ <target> ] ]',
    {
        'RPL_LUSERCLIENT',
        'RPL_LUSEROP',
        'RPL_LUSERUNKOWN',
        'RPL_LUSERCHANNELS',
        'RPL_LUSERME',
        'ERR_NOSUCHSERVER',
    },
)

VERSION = Message(
    'VERSION',
    '[ <target> ]',
    {
        'ERR_NOSUCHSERVER',
        'RPL_VERSION',
    },
)

STATS = Message(
    'STATS',
    '[ <query> [ <target> ] ]',
    {
        'ERR_NOSUCHSERVER',
        'RPL_STATSLINKINFO',
        'RPL_STATSUPTIME',
        'RPL_STATSCOMMANDS',
        'RPL_STATSOLINE',
        'RPL_ENDOFSTATS',
    },
)

LINKS = Message(
    'LINKS',
    '[ [ <remote server> ] <server mask> ]',
    {
        'ERR_NOSUCHSERVER',
        'RPL_LINKS',
        'RPL_ENDOFLINKS',
    },
)

TIME = Message(
    'TIME',
    '[ <target> ]',
    {
        'ERR_NOSUCHSERVER',
        'RPL_TIME',
    },
)

CONNECT = Message(
    'CONNECT',
    '<target server> <port> [ <remote server> ]',
    {
        'ERR_NOSUCHSERVER',
        'ERR_NOPRIVILEGES',
        'ERR_NEEDMOREPARAMS',
    },
)

TRACE = Message(
    'TRACE',
    '[ <target> ]',
    {
        'ERR_NOSUCHSERVER',
    },
)

ADMIN = Message(
    'ADMIN',
    '[ <target> ]',
    {
        'ERR_NOSUCHSERVER',
        'RPL_ADMINME',
        'RPL_ADMINLOC1',
        'RPL_ADMINLOC2',
        'RPL_ADMINEMAIL',
    },
)

INFO = Message(
    'INFO',
    '[ <target> ]',
    {
        'ERR_NOSUCHSERVER',
        'RPL_INFO',
        'RPL_ENDOFINFO',
    },
)

SERVLIST = Message(
    'SERVLIST',
    '[ <mask> [ <type> ] ]',
    {
        'RPL_SERVLIST',
        'RPL_SERVLISTEND',
    },
)

SQUERY = Message(
    'SQUERY',
    '<servicename> <text>',
    {
        'ERR_NORECIPIENT',
        'ERR_NOTEXTTOSEND',
        'ERR_CANNOTSENDTOCHAN',
        'ERR_NOTOPLEVEL',
        'ERR_WILDTOPLEVEL',
        'ERR_TOOMANYTARGETS',
        'ERR_NOSUCHNICK',
        'RPL_AWAY',
    },
)

WHO = Message(
    'WHO',
    '[ <mask> [ "o" ] ]',
    {
        'ERR_NOSUCHSERVER',
        'RPL_WHOREPLY',
        'RPL_ENDOFWHO',
    },
)

WHOIS = Message(
    'WHOIS',
    '[ <target> ] <mask> *( "," <mask> )',
    {
        'ERR_NOSUCHSERVER',
        'ERR_NONICKNAMEGIVEN',
        'RPL_WHOISUSER',
        'RPL_WHOISCHANNELS',
        'RPL_WHOISCHANNELS',
        'RPL_WHOISSERVER',
        'RPL_AWAY',
        'RPL_WHOISOPERATOR',
        'RPL_WHOISIDLE',
        'ERR_NOSUCHNICK',
        'RPL_ENDOFWHOIS',
    },
)

WHOWAS = Message(
    'WHOWAS',
    '<nickname> *( "," <nickname> ) [ <count> [ <target> ] ]',
    {
        'ERR_NONICKNAMEGIVEN',
        'ERR_WASNOSUCHNICK',
        'RPL_WHOWASUSER',
        'RPL_WHOISSERVER',
        'RPL_ENDOFWHOWAS',
    },
)

KILL = Message(
    'KILL',
    '<nickname> <comment>',
    {
        'ERR_NOPRIVILEGES',
        'ERR_NEEDMOREPARAMS',
        'ERR_NOSUCHNICK',
        'ERR_CANTKILLSERVER',
    },
)

PING = Message(
    'PING',
    '<server1> [ <server2> ]',
    {
        'ERR_NOORIGIN',
        'ERR_NOSUCHSERVER',
    },
)

PONG = Message(
    'PONG',
    '<server> [ <server2> ]',
    {
        'ERR_NOORIGIN',
        'ERR_NOSUCHSERVER',
    },
)

ERROR = Message(
    'ERROR',
    '<error message>',
    set(),
)

AWAY = Message(
    'AWAY',
    '[ <text> ]',
    {
        'RPL_UNAWAY',
        'RPL_NOWAWAY',
    },
)

REHASH = Message(
    'REHASH',
    '',
    {
        'RPL_REHASHING',
        'ERR_NOPRIVILEGES',
    },
)

DIE = Message(
    'DIE',
    '',
    {
        'ERR_NOPRIVILEGES',
    },
)

RESTART = Message(
    'RESTART',
    '',
    {
        'ERR_NOPRIVILEGES',
    },
)

SUMMON = Message(
    'SUMMON',
    '<user> [ <target> [ <channel> ] ]',
    {
        'ERR_NORECIPIENT',
        'ERR_FILEERROR',
        'ERR_NOLOGIN',
        'ERR_NOSUCHSERVER',
        'ERR_SUMMONDISABLED',
        'RPL_SUMMONING',
    },
)

USERS = Message(
    'USERS',
    '[ <target> ]',
    {
        'ERR_NOSUCHSERVER',
        'ERR_FILEERROR',
        'RPL_USERSSTART',
        'RPL_USERS',
        'RPL_NOUSERS',
        'RPL_ENDOFUSERS',
        'ERR_USERSDISABLED',
    },
)

WALLOPS = Message(
    'WALLOPS',
    '<Text to be sent>',
    {
        'ERR_NEEDMOREPARAMS',
    },
)

USERHOST = Message(
    'USERHOST',
    '<nickname> *( SPACE <nickname> )',
    {
        'RPL_USERHOST',
        'ERR_NEEDMOREPARAMS',
    },
)

ISON = Message(
    'ISON',
    '<nickname> *( SPACE <nickname> )',
    {
        'RPL_ISON',
        'ERR_NEEDMOREPARAMS',
    },
)
