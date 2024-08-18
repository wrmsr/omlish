import dataclasses as dc
import typing as ta

from ... import check
from ... import lang

REPLIES: ta.Sequence['Reply'] = []
REPLIES_BY_CODE: ta.Mapping[int, 'Reply'] = {}
REPLIES_BY_NAME: ta.Mapping[str, 'Reply'] = {}


@dc.dataclass(frozen=True)
class Reply(lang.Final):
    code: int
    name: str
    desc: str

    def __post_init__(self) -> None:
        check.not_in(self.code, REPLIES_BY_CODE)
        check.not_in(self.name, REPLIES_BY_NAME)
        REPLIES.append(self)
        REPLIES_BY_CODE[self.code] = self
        REPLIES_BY_NAME[self.name] = self


RPL_WELCOME = Reply(
    1,
    'RPL_WELCOME',
    'Welcome to the Internet Relay Network <nick>!<user>@<host>',
)

RPL_YOURHOST = Reply(
    2,
    'RPL_YOURHOST',
    'Your host is <servername>, running version <ver>',
)

RPL_CREATED = Reply(
    3,
    'RPL_CREATED',
    'This server was created <date>',
)

RPL_MYINFO = Reply(
    4,
    'RPL_MYINFO',
    '<servername> <version> <available user modes> <available channel modes>',
)

RPL_BOUNCE = Reply(
    5,
    'RPL_BOUNCE',
    'Try server <server name>, port <port number>',
)

RPL_USERHOST = Reply(
    302,
    'RPL_USERHOST',
    ':*1<reply> *( " " <reply> )',
)

RPL_ISON = Reply(
    303,
    'RPL_ISON',
    ':*1<nick> *( " " <nick> )',
)

RPL_AWAY = Reply(
    301,
    'RPL_AWAY',
    '<nick> :<away message>',
)

RPL_UNAWAY = Reply(
    305,
    'RPL_UNAWAY',
    ':You are no longer marked as being away',
)

RPL_NOWAWAY = Reply(
    306,
    'RPL_NOWAWAY',
    ':You have been marked as being away',
)

RPL_WHOISUSER = Reply(
    311,
    'RPL_WHOISUSER',
    '<nick> <user> <host> * :<real name>',
)

RPL_WHOISSERVER = Reply(
    312,
    'RPL_WHOISSERVER',
    '<nick> <server> :<server info>',
)

RPL_WHOISOPERATOR = Reply(
    313,
    'RPL_WHOISOPERATOR',
    '<nick> :is an IRC operator',
)

RPL_WHOISIDLE = Reply(
    317,
    'RPL_WHOISIDLE',
    '<nick> <integer> :seconds idle',
)

RPL_ENDOFWHOIS = Reply(
    318,
    'RPL_ENDOFWHOIS',
    '<nick> :End of WHOIS list',
)

RPL_WHOISCHANNELS = Reply(
    319,
    'RPL_WHOISCHANNELS',
    '<nick> :*( ( " @ " / " + " ) <channel> " " )',
)

RPL_WHOWASUSER = Reply(
    314,
    'RPL_WHOWASUSER',
    '<nick> <user> <host> * :<real name>',
)

RPL_ENDOFWHOWAS = Reply(
    369,
    'RPL_ENDOFWHOWAS',
    '<nick> :End of WHOWAS',
)

RPL_LISTSTART = Reply(
    321,
    'RPL_LISTSTART',
    'Obsolete. Not used.',
)

RPL_LIST = Reply(
    322,
    'RPL_LIST',
    '<channel> <# visible> :<topic>',
)

RPL_LISTEND = Reply(
    323,
    'RPL_LISTEND',
    ':End of LIST',
)

RPL_UNIQOPIS = Reply(
    325,
    'RPL_UNIQOPIS',
    '<channel> <nickname>',
)

RPL_CHANNELMODEIS = Reply(
    324,
    'RPL_CHANNELMODEIS',
    '<channel> <mode> <mode params>',
)

RPL_NOTOPIC = Reply(
    331,
    'RPL_NOTOPIC',
    '<channel> :No topic is set',
)

RPL_TOPIC = Reply(
    332,
    'RPL_TOPIC',
    '<channel> :<topic>',
)

RPL_INVITING = Reply(
    341,
    'RPL_INVITING',
    '<channel> <nick>',
)

RPL_SUMMONING = Reply(
    342,
    'RPL_SUMMONING',
    '<user> :Summoning user to IRC',
)

RPL_INVITELIST = Reply(
    346,
    'RPL_INVITELIST',
    '<channel> <invitemask>',
)

RPL_ENDOFINVITELIST = Reply(
    347,
    'RPL_ENDOFINVITELIST',
    '<channel> :End of channel invite list',
)

RPL_EXCEPTLIST = Reply(
    348,
    'RPL_EXCEPTLIST',
    '<channel> <exceptionmask>',
)

RPL_ENDOFEXCEPTLIST = Reply(
    349,
    'RPL_ENDOFEXCEPTLIST',
    '<channel> :End of channel exception list',
)

RPL_VERSION = Reply(
    351,
    'RPL_VERSION',
    '<version>.<debuglevel> <server> :<comments>',
)

RPL_WHOREPLY = Reply(
    352,
    'RPL_WHOREPLY',
    '<channel> <user> <host> <server> <nick> ( "H" / "G" > ["*"] [ ( "@" / "+" ) ] :<hopcount> <real name>',
)

RPL_ENDOFWHO = Reply(
    315,
    'RPL_ENDOFWHO',
    '<name> :End of WHO list',
)

RPL_NAMREPLY = Reply(
    353,
    'RPL_NAMREPLY',
    '( "=" / "*" / "@" ) <channel> :[ "@" / "+" ] <nick> *( " " [ "@" / "+" ] <nick> )',
)

RPL_ENDOFNAMES = Reply(
    366,
    'RPL_ENDOFNAMES',
    '<channel> :End of NAMES list',
)

RPL_LINKS = Reply(
    364,
    'RPL_LINKS',
    '<mask> <server> :<hopcount> <server info>',
)

RPL_ENDOFLINKS = Reply(
    365,
    'RPL_ENDOFLINKS',
    '<mask> :End of LINKS list',
)

RPL_BANLIST = Reply(
    367,
    'RPL_BANLIST',
    '<channel> <banmask>',
)

RPL_ENDOFBANLIST = Reply(
    368,
    'RPL_ENDOFBANLIST',
    '<channel> :End of channel ban list',
)

RPL_INFO = Reply(
    371,
    'RPL_INFO',
    ':<string>',
)

RPL_ENDOFINFO = Reply(
    374,
    'RPL_ENDOFINFO',
    ':End of INFO list',
)

RPL_MOTDSTART = Reply(
    375,
    'RPL_MOTDSTART',
    ':- <server> Message of the day - ',
)

RPL_MOTD = Reply(
    372,
    'RPL_MOTD',
    ':- <text>',
)

RPL_ENDOFMOTD = Reply(
    376,
    'RPL_ENDOFMOTD',
    ':End of MOTD command',
)

RPL_YOUREOPER = Reply(
    381,
    'RPL_YOUREOPER',
    ':You are now an IRC operator',
)

RPL_REHASHING = Reply(
    382,
    'RPL_REHASHING',
    '<config file> :Rehashing',
)

RPL_YOURESERVICE = Reply(
    383,
    'RPL_YOURESERVICE',
    'You are service <servicename>',
)

RPL_TIME = Reply(
    391,
    'RPL_TIME',
    '<server> :<string showing server\'s local time>',
)

RPL_USERSSTART = Reply(
    392,
    'RPL_USERSSTART',
    ':UserID   Terminal  Host',
)

RPL_USERS = Reply(
    393,
    'RPL_USERS',
    ':<username> <ttyline> <hostname>',
)

RPL_ENDOFUSERS = Reply(
    394,
    'RPL_ENDOFUSERS',
    ':End of users',
)

RPL_NOUSERS = Reply(
    395,
    'RPL_NOUSERS',
    ':Nobody logged in',
)

RPL_TRACELINK = Reply(
    200,
    'RPL_TRACELINK',
    'Link <version & debug level> <destination> <next server> V<protocol version> <link uptime in seconds> <backstream sendq> <upstream sendq>',  # noqa
)

RPL_TRACECONNECTING = Reply(
    201,
    'RPL_TRACECONNECTING',
    'Try. <class> <server>',
)

RPL_TRACEHANDSHAKE = Reply(
    202,
    'RPL_TRACEHANDSHAKE',
    'H.S. <class> <server>',
)

RPL_TRACEUNKNOWN = Reply(
    203,
    'RPL_TRACEUNKNOWN',
    '???? <class> [<client IP address in dot form>]',
)

RPL_TRACEOPERATOR = Reply(
    204,
    'RPL_TRACEOPERATOR',
    'Oper <class> <nick>',
)

RPL_TRACEUSER = Reply(
    205,
    'RPL_TRACEUSER',
    'User <class> <nick>',
)

RPL_TRACESERVER = Reply(
    206,
    'RPL_TRACESERVER',
    'Serv <class> <int>S <int>C <server> <nick!user|*!*>@<host|server> V<protocol version>',
)

RPL_TRACESERVICE = Reply(
    207,
    'RPL_TRACESERVICE',
    'Service <class> <name> <type> <active type>',
)

RPL_TRACENEWTYPE = Reply(
    208,
    'RPL_TRACENEWTYPE',
    '<newtype> 0 <client name>',
)

RPL_TRACECLASS = Reply(
    209,
    'RPL_TRACECLASS',
    'Class <class> <count>',
)

RPL_TRACERECONNECT = Reply(
    210,
    'RPL_TRACERECONNECT',
    'Unused.',
)

RPL_TRACELOG = Reply(
    261,
    'RPL_TRACELOG',
    'File <logfile> <debug level>',
)

RPL_TRACEEND = Reply(
    262,
    'RPL_TRACEEND',
    '<server name> <version & debug level> :End of TRACE',
)

RPL_STATSLINKINFO = Reply(
    211,
    'RPL_STATSLINKINFO',
    '<linkname> <sendq> <sent messages> <sent Kbytes> <received messages> <received Kbytes> <time open>',
)

RPL_STATSCOMMANDS = Reply(
    212,
    'RPL_STATSCOMMANDS',
    '<command> <count> <byte count> <remote count>',
)

RPL_ENDOFSTATS = Reply(
    219,
    'RPL_ENDOFSTATS',
    '<stats letter> :End of STATS report',
)

RPL_STATSUPTIME = Reply(
    242,
    'RPL_STATSUPTIME',
    ':Server Up %d days %d:%02d:%02d',
)

RPL_STATSOLINE = Reply(
    243,
    'RPL_STATSOLINE',
    'O <hostmask> * <name>',
)

RPL_UMODEIS = Reply(
    221,
    'RPL_UMODEIS',
    '<user mode string>',
)

RPL_SERVLIST = Reply(
    234,
    'RPL_SERVLIST',
    '<name> <server> <mask> <type> <hopcount> <info>',
)

RPL_SERVLISTEND = Reply(
    235,
    'RPL_SERVLISTEND',
    '<mask> <type> :End of service listing',
)

RPL_LUSERCLIENT = Reply(
    251,
    'RPL_LUSERCLIENT',
    ':There are <integer> users and <integer> services on <integer> servers',
)

RPL_LUSEROP = Reply(
    252,
    'RPL_LUSEROP',
    '<integer> :operator(s) online',
)

RPL_LUSERUNKNOWN = Reply(
    253,
    'RPL_LUSERUNKNOWN',
    '<integer> :unknown connection(s)',
)

RPL_LUSERCHANNELS = Reply(
    254,
    'RPL_LUSERCHANNELS',
    '<integer> :channels formed',
)

RPL_LUSERME = Reply(
    255,
    'RPL_LUSERME',
    ':I have <integer> clients and <integer> servers',
)

RPL_ADMINME = Reply(
    256,
    'RPL_ADMINME',
    '<server> :Administrative info',
)

RPL_ADMINLOC1 = Reply(
    257,
    'RPL_ADMINLOC1',
    ':<admin info>',
)

RPL_ADMINLOC2 = Reply(
    258,
    'RPL_ADMINLOC2',
    ':<admin info>',
)

RPL_ADMINEMAIL = Reply(
    259,
    'RPL_ADMINEMAIL',
    ':<admin info>',
)

RPL_TRYAGAIN = Reply(
    263,
    'RPL_TRYAGAIN',
    '<command> :Please wait a while and try again.',
)

ERR_NOSUCHNICK = Reply(
    401,
    'ERR_NOSUCHNICK',
    '<nickname> :No such nick/channel',
)

ERR_NOSUCHSERVER = Reply(
    402,
    'ERR_NOSUCHSERVER',
    '<server name> :No such server',
)

ERR_NOSUCHCHANNEL = Reply(
    403,
    'ERR_NOSUCHCHANNEL',
    '<channel name> :No such channel',
)

ERR_CANNOTSENDTOCHAN = Reply(
    404,
    'ERR_CANNOTSENDTOCHAN',
    '<channel name> :Cannot send to channel',
)

ERR_TOOMANYCHANNELS = Reply(
    405,
    'ERR_TOOMANYCHANNELS',
    '<channel name> :You have joined too many channels',
)

ERR_WASNOSUCHNICK = Reply(
    406,
    'ERR_WASNOSUCHNICK',
    '<nickname> :There was no such nickname',
)

ERR_TOOMANYTARGETS = Reply(
    407,
    'ERR_TOOMANYTARGETS',
    '<target> :<error code> recipients. <abort message>',
)

ERR_NOSUCHSERVICE = Reply(
    408,
    'ERR_NOSUCHSERVICE',
    '<service name> :No such service',
)

ERR_NOORIGIN = Reply(
    409,
    'ERR_NOORIGIN',
    ':No origin specified',
)

ERR_NORECIPIENT = Reply(
    411,
    'ERR_NORECIPIENT',
    ':No recipient given (<command>)',
)

ERR_NOTEXTTOSEND = Reply(
    412,
    'ERR_NOTEXTTOSEND',
    ':No text to send',
)

ERR_NOTOPLEVEL = Reply(
    413,
    'ERR_NOTOPLEVEL',
    '<mask> :No toplevel domain specified',
)

ERR_WILDTOPLEVEL = Reply(
    414,
    'ERR_WILDTOPLEVEL',
    '<mask> :Wildcard in toplevel domain',
)

ERR_BADMASK = Reply(
    415,
    'ERR_BADMASK',
    '<mask> :Bad Server/host mask',
)

ERR_UNKNOWNCOMMAND = Reply(
    421,
    'ERR_UNKNOWNCOMMAND',
    '<command> :Unknown command',
)

ERR_NOMOTD = Reply(
    422,
    'ERR_NOMOTD',
    ':MOTD File is missing',
)

ERR_NOADMININFO = Reply(
    423,
    'ERR_NOADMININFO',
    '<server> :No administrative info available',
)

ERR_FILEERROR = Reply(
    424,
    'ERR_FILEERROR',
    ':File error doing <file op> on <file>',
)

ERR_NONICKNAMEGIVEN = Reply(
    431,
    'ERR_NONICKNAMEGIVEN',
    ':No nickname given',
)

ERR_ERRONEUSNICKNAME = Reply(
    432,
    'ERR_ERRONEUSNICKNAME',
    '<nick> :Erroneous nickname',
)

ERR_NICKNAMEINUSE = Reply(
    433,
    'ERR_NICKNAMEINUSE',
    '<nick> :Nickname is already in use',
)

ERR_NICKCOLLISION = Reply(
    436,
    'ERR_NICKCOLLISION',
    '<nick> :Nickname collision KILL from <user>@<host>',
)

ERR_UNAVAILRESOURCE = Reply(
    437,
    'ERR_UNAVAILRESOURCE',
    '<nick/channel> :Nick/channel is temporarily unavailable',
)

ERR_USERNOTINCHANNEL = Reply(
    441,
    'ERR_USERNOTINCHANNEL',
    '<nick> <channel> :They aren\'t on that channel',
)

ERR_NOTONCHANNEL = Reply(
    442,
    'ERR_NOTONCHANNEL',
    '<channel> :You\'re not on that channel',
)

ERR_USERONCHANNEL = Reply(
    443,
    'ERR_USERONCHANNEL',
    '<user> <channel> :is already on channel',
)

ERR_NOLOGIN = Reply(
    444,
    'ERR_NOLOGIN',
    '<user> :User not logged in',
)

ERR_SUMMONDISABLED = Reply(
    445,
    'ERR_SUMMONDISABLED',
    ':SUMMON has been disabled',
)

ERR_USERSDISABLED = Reply(
    446,
    'ERR_USERSDISABLED',
    ':USERS has been disabled',
)

ERR_NOTREGISTERED = Reply(
    451,
    'ERR_NOTREGISTERED',
    ':You have not registered',
)

ERR_NEEDMOREPARAMS = Reply(
    461,
    'ERR_NEEDMOREPARAMS',
    '<command> :Not enough parameters',
)

ERR_ALREADYREGISTRED = Reply(
    462,
    'ERR_ALREADYREGISTRED',
    ':Unauthorized command (already registered)',
)

ERR_NOPERMFORHOST = Reply(
    463,
    'ERR_NOPERMFORHOST',
    ':Your host isn\'t among the privileged',
)

ERR_PASSWDMISMATCH = Reply(
    464,
    'ERR_PASSWDMISMATCH',
    ':Password incorrect',
)

ERR_YOUREBANNEDCREEP = Reply(
    465,
    'ERR_YOUREBANNEDCREEP',
    ':You are banned from this server',
)

ERR_YOUWILLBEBANNED = Reply(
    466,
    'ERR_YOUWILLBEBANNED',
    '',
)

ERR_KEYSET = Reply(
    467,
    'ERR_KEYSET',
    '<channel> :Channel key already set',
)

ERR_CHANNELISFULL = Reply(
    471,
    'ERR_CHANNELISFULL',
    '<channel> :Cannot join channel (+l)',
)

ERR_UNKNOWNMODE = Reply(
    472,
    'ERR_UNKNOWNMODE',
    '<char> :is unknown mode char to me for <channel>',
)

ERR_INVITEONLYCHAN = Reply(
    473,
    'ERR_INVITEONLYCHAN',
    '<channel> :Cannot join channel (+i)',
)

ERR_BANNEDFROMCHAN = Reply(
    474,
    'ERR_BANNEDFROMCHAN',
    '<channel> :Cannot join channel (+b)',
)

ERR_BADCHANNELKEY = Reply(
    475,
    'ERR_BADCHANNELKEY',
    '<channel> :Cannot join channel (+k)',
)

ERR_BADCHANMASK = Reply(
    476,
    'ERR_BADCHANMASK',
    '<channel> :Bad Channel Mask',
)

ERR_NOCHANMODES = Reply(
    477,
    'ERR_NOCHANMODES',
    '<channel> :Channel doesn\'t support modes',
)

ERR_BANLISTFULL = Reply(
    478,
    'ERR_BANLISTFULL',
    '<channel> <char> :Channel list is full',
)

ERR_NOPRIVILEGES = Reply(
    481,
    'ERR_NOPRIVILEGES',
    ':Permission Denied- You\'re not an IRC operator',
)

ERR_CHANOPRIVSNEEDED = Reply(
    482,
    'ERR_CHANOPRIVSNEEDED',
    '<channel> :You\'re not channel operator',
)

ERR_CANTKILLSERVER = Reply(
    483,
    'ERR_CANTKILLSERVER',
    ':You can\'t kill a server!',
)

ERR_RESTRICTED = Reply(
    484,
    'ERR_RESTRICTED',
    ':Your connection is restricted!',
)

ERR_UNIQOPPRIVSNEEDED = Reply(
    485,
    'ERR_UNIQOPPRIVSNEEDED',
    ':You\'re not the original channel operator',
)

ERR_NOOPERHOST = Reply(
    491,
    'ERR_NOOPERHOST',
    ':No O-lines for your host',
)

ERR_UMODEUNKNOWNFLAG = Reply(
    501,
    'ERR_UMODEUNKNOWNFLAG',
    ':Unknown MODE flag',
)

ERR_USERSDONTMATCH = Reply(
    502,
    'ERR_USERSDONTMATCH',
    ':Cannot change mode for other users',
)
