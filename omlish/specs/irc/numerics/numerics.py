from .types import NumericReplies
from .types import NumericReply


##


_REGISTERED_NUMERIC_REPLIES: list[NumericReply] = []


def _register_numeric_reply(
        name: str,
        num: int,
        *formats: str,
) -> NumericReply:
    nr = NumericReply(
        name,
        num,
        formats,
    )
    _REGISTERED_NUMERIC_REPLIES.append(nr)
    return nr


##


RPL_WELCOME = _register_numeric_reply(
    'RPL_WELCOME',
    1,
    '<client> :Welcome to the <networkname> Network, <nick>[!<user>@<host>]',
)

RPL_YOURHOST = _register_numeric_reply(
    'RPL_YOURHOST',
    2,
    '<client> :Your host is <servername>, running version <version>',
)

RPL_CREATED = _register_numeric_reply(
    'RPL_CREATED',
    3,
    '<client> :This server was created <datetime>',
)

RPL_MYINFO = _register_numeric_reply(
    'RPL_MYINFO',
    4,
    '<client> <servername> <version> <available user modes> <available channel modes> [<channel modes with a parameter>]',  # noqa
    # noqa
)

RPL_ISUPPORT = _register_numeric_reply(
    'RPL_ISUPPORT',
    5,
    '<client> <1-13 tokens> :are supported by this server',
)

RPL_BOUNCE = _register_numeric_reply(
    'RPL_BOUNCE',
    10,
    '<client> <hostname> <port> :<info>',
)

RPL_STATSLINKINFO = _register_numeric_reply(
    'RPL_STATSLINKINFO',
    211,
    '<linkname> <sendq> <sent messages> <sent Kbytes> <received messages> <received Kbytes> <time open>',
)

RPL_STATSCOMMANDS = _register_numeric_reply(
    'RPL_STATSCOMMANDS',
    212,
    '<client> <command> <count> [<byte count> <remote count>]',
)

RPL_STATSCLINE = _register_numeric_reply('RPL_STATSCLINE', 213)

RPL_STATSNLINE = _register_numeric_reply('RPL_STATSNLINE', 214)

RPL_STATSILINE = _register_numeric_reply('RPL_STATSILINE', 215)

RPL_STATSKLINE = _register_numeric_reply('RPL_STATSKLINE', 216)

RPL_STATSQLINE = _register_numeric_reply('RPL_STATSQLINE', 217)

RPL_STATSYLINE = _register_numeric_reply('RPL_STATSYLINE', 218)

RPL_ENDOFSTATS = _register_numeric_reply(
    'RPL_ENDOFSTATS',
    219,
    '<client> <stats letter> :End of /STATS report',
)

RPL_UMODEIS = _register_numeric_reply(
    'RPL_UMODEIS',
    221,
    '<client> <user modes>',
)

RPL_STATSVLINE = _register_numeric_reply('RPL_STATSVLINE', 240)

RPL_STATSLLINE = _register_numeric_reply('RPL_STATSLLINE', 241)

RPL_STATSUPTIME = _register_numeric_reply(
    'RPL_STATSUPTIME',
    242,
    '<client> :Server Up <days> days <hours>:<minutes>:<seconds>',
)

RPL_STATSOLINE = _register_numeric_reply(
    'RPL_STATSOLINE',
    243,
    'O <hostmask> * <name>',
)

RPL_STATSHLINE = _register_numeric_reply('RPL_STATSHLINE', 244)

RPL_STATSPING = _register_numeric_reply('RPL_STATSPING', 246)

RPL_STATSBLINE = _register_numeric_reply('RPL_STATSBLINE', 247)

RPL_STATSDLINE = _register_numeric_reply('RPL_STATSDLINE', 250)

RPL_LUSERCLIENT = _register_numeric_reply(
    'RPL_LUSERCLIENT',
    251,
    '<client> :There are <u> users and <i> invisible on <s> servers',
)

RPL_LUSEROP = _register_numeric_reply(
    'RPL_LUSEROP',
    252,
    '<client> <ops> :operator(s) online',
)

RPL_LUSERUNKNOWN = _register_numeric_reply(
    'RPL_LUSERUNKNOWN',
    253,
    '<client> <connections> :unknown connection(s)',
)

RPL_LUSERCHANNELS = _register_numeric_reply(
    'RPL_LUSERCHANNELS',
    254,
    '<client> <channels> :channels formed',
)

RPL_LUSERME = _register_numeric_reply(
    'RPL_LUSERME',
    255,
    '<client> :I have <c> clients and <s> servers',
)

RPL_ADMINME = _register_numeric_reply(
    'RPL_ADMINME',
    256,
    '<client> [<server>] :Administrative info',
)

RPL_ADMINLOC1 = _register_numeric_reply(
    'RPL_ADMINLOC1',
    257,
    '<client> :<info>',
)

RPL_ADMINLOC2 = _register_numeric_reply(
    'RPL_ADMINLOC2',
    258,
    '<client> :<info>',
)

RPL_ADMINEMAIL = _register_numeric_reply(
    'RPL_ADMINEMAIL',
    259,
    '<client> :<info>',
)

RPL_TRYAGAIN = _register_numeric_reply(
    'RPL_TRYAGAIN',
    263,
    '<client> <command> :Please wait a while and try again.',
)

RPL_LOCALUSERS = _register_numeric_reply(
    'RPL_LOCALUSERS',
    265,
    '<client> [<u> <m>] :Current local users <u>, max <m>',
)

RPL_GLOBALUSERS = _register_numeric_reply(
    'RPL_GLOBALUSERS',
    266,
    '<client> [<u> <m>] :Current global users <u>, max <m>',
)

RPL_WHOISCERTFP = _register_numeric_reply(
    'RPL_WHOISCERTFP',
    276,
    '<client> <nick> :has client certificate fingerprint <fingerprint>',
)

RPL_NONE = _register_numeric_reply(
    'RPL_NONE',
    300,
)

RPL_AWAY = _register_numeric_reply(
    'RPL_AWAY',
    301,
    '<client> <nick> :<message>',
)

RPL_USERHOST = _register_numeric_reply(
    'RPL_USERHOST',
    302,
    '<client> :[<reply>{ <reply>}]',
)

RPL_UNAWAY = _register_numeric_reply(
    'RPL_UNAWAY',
    305,
    '<client> :You are no longer marked as being away',
)

RPL_NOWAWAY = _register_numeric_reply(
    'RPL_NOWAWAY',
    306,
    '<client> :You have been marked as being away',
)

RPL_WHOISREGNICK = _register_numeric_reply(
    'RPL_WHOISREGNICK',
    307,
    '<client> <nick> :has identified for this nick',
)

RPL_WHOISUSER = _register_numeric_reply(
    'RPL_WHOISUSER',
    311,
    '<client> <nick> <username> <host> * :<realname>',
)

RPL_WHOISSERVER = _register_numeric_reply(
    'RPL_WHOISSERVER',
    312,
    '<client> <nick> <server> :<server info>',
)

RPL_WHOISOPERATOR = _register_numeric_reply(
    'RPL_WHOISOPERATOR',
    313,
    '<client> <nick> :is an IRC operator',
)

RPL_WHOWASUSER = _register_numeric_reply(
    'RPL_WHOWASUSER',
    314,
    '<client> <nick> <username> <host> * :<realname>',
)

RPL_ENDOFWHO = _register_numeric_reply(
    'RPL_ENDOFWHO',
    315,
    '<client> <mask> :End of WHO list',
)

RPL_WHOISIDLE = _register_numeric_reply(
    'RPL_WHOISIDLE',
    317,
    '<client> <nick> <secs> <signon> :seconds idle, signon time',
)

RPL_ENDOFWHOIS = _register_numeric_reply(
    'RPL_ENDOFWHOIS',
    318,
    '<client> <nick> :End of /WHOIS list',
)

RPL_WHOISCHANNELS = _register_numeric_reply(
    'RPL_WHOISCHANNELS',
    319,
    '<client> <nick> :[prefix]<channel>{ [prefix]<channel>}',
)

RPL_WHOISSPECIAL = _register_numeric_reply(
    'RPL_WHOISSPECIAL',
    320,
    '<client> <nick> :blah blah blah',
)

RPL_LISTSTART = _register_numeric_reply(
    'RPL_LISTSTART',
    321,
    '<client> Channel :Users  Name',
)

RPL_LIST = _register_numeric_reply(
    'RPL_LIST',
    322,
    '<client> <channel> <client count> :<topic>',
)

RPL_LISTEND = _register_numeric_reply(
    'RPL_LISTEND',
    323,
    '<client> :End of /LIST',
)

RPL_CHANNELMODEIS = _register_numeric_reply(
    'RPL_CHANNELMODEIS',
    324,
    '<client> <channel> <modestring> <mode arguments>...',
)

RPL_CREATIONTIME = _register_numeric_reply(
    'RPL_CREATIONTIME',
    329,
    '<client> <channel> <creationtime>',
)

RPL_WHOISACCOUNT = _register_numeric_reply(
    'RPL_WHOISACCOUNT',
    330,
    '<client> <nick> <account> :is logged in as',
)

RPL_NOTOPIC = _register_numeric_reply(
    'RPL_NOTOPIC',
    331,
    '<client> <channel> :No topic is set',
)

RPL_TOPIC = _register_numeric_reply(
    'RPL_TOPIC',
    332,
    '<client> <channel> :<topic>',
)

RPL_TOPICWHOTIME = _register_numeric_reply(
    'RPL_TOPICWHOTIME',
    333,
    '<client> <channel> <nick> <setat>',
)

RPL_INVITELIST = _register_numeric_reply(
    'RPL_INVITELIST',
    336,
    '<client> <channel>',
)

RPL_ENDOFINVITELIST = _register_numeric_reply(
    'RPL_ENDOFINVITELIST',
    337,
    '<client> :End of /INVITE list',
)

RPL_WHOISACTUALLY = _register_numeric_reply(
    'RPL_WHOISACTUALLY',
    338,
    '<client> <nick> :is actually ...',
    '<client> <nick> <host|ip> :Is actually using host',
    '<client> <nick> <username>@<hostname> <ip> :Is actually using host',
)

RPL_INVITING = _register_numeric_reply(
    'RPL_INVITING',
    341,
    '<client> <nick> <channel>',
)

RPL_INVEXLIST = _register_numeric_reply(
    'RPL_INVEXLIST',
    346,
    '<client> <channel> <mask>',
)

RPL_ENDOFINVEXLIST = _register_numeric_reply(
    'RPL_ENDOFINVEXLIST',
    347,
    '<client> <channel> :End of Channel Invite Exception List',
)
RPL_EXCEPTLIST = _register_numeric_reply(
    'RPL_EXCEPTLIST',
    348,
    '<client> <channel> <mask>',
)

RPL_ENDOFEXCEPTLIST = _register_numeric_reply(
    'RPL_ENDOFEXCEPTLIST',
    349,
    '<client> <channel> :End of channel exception list',
)

RPL_VERSION = _register_numeric_reply(
    'RPL_VERSION',
    351,
    '<client> <version> <server> :<comments>',
)

RPL_WHOREPLY = _register_numeric_reply(
    'RPL_WHOREPLY',
    352,
    '<client> <channel> <username> <host> <server> <nick> <flags> :<hopcount> <realname>',
)
RPL_NAMREPLY = _register_numeric_reply(
    'RPL_NAMREPLY',
    353,
    '<client> <symbol> <channel> :[prefix]<nick>{ [prefix]<nick>}',
)

RPL_LINKS = _register_numeric_reply(
    'RPL_LINKS',
    364,
    '<client> * <server> :<hopcount> <server info>',
)

RPL_ENDOFLINKS = _register_numeric_reply(
    'RPL_ENDOFLINKS',
    365,
    '<client> * :End of /LINKS list',
)

RPL_ENDOFNAMES = _register_numeric_reply(
    'RPL_ENDOFNAMES',
    366,
    '<client> <channel> :End of /NAMES list',
)

RPL_BANLIST = _register_numeric_reply(
    'RPL_BANLIST',
    367,
    '<client> <channel> <mask> [<who> <set-ts>]',
)

RPL_ENDOFBANLIST = _register_numeric_reply(
    'RPL_ENDOFBANLIST',
    368,
    '<client> <channel> :End of channel ban list',
)

RPL_ENDOFWHOWAS = _register_numeric_reply(
    'RPL_ENDOFWHOWAS',
    369,
    '<client> <nick> :End of WHOWAS',
)

RPL_INFO = _register_numeric_reply(
    'RPL_INFO',
    371,
    '<client> :<string>',
)

RPL_MOTD = _register_numeric_reply(
    'RPL_MOTD',
    372,
    '<client> :<line of the motd>',
)

RPL_ENDOFINFO = _register_numeric_reply(
    'RPL_ENDOFINFO',
    374,
    '<client> :End of INFO list',
)

RPL_MOTDSTART = _register_numeric_reply(
    'RPL_MOTDSTART',
    375,
    '<client> :- <server> Message of the day - ',
)

RPL_ENDOFMOTD = _register_numeric_reply(
    'RPL_ENDOFMOTD',
    376,
    '<client> :End of /MOTD command.',
)

RPL_WHOISHOST = _register_numeric_reply(
    'RPL_WHOISHOST',
    378,
    '<client> <nick> :is connecting from *@localhost 127.0.0.1',
)

RPL_WHOISMODES = _register_numeric_reply(
    'RPL_WHOISMODES',
    379,
    '<client> <nick> :is using modes +ailosw',
)

RPL_YOUREOPER = _register_numeric_reply(
    'RPL_YOUREOPER',
    381,
    '<client> :You are now an IRC operator',
)

RPL_REHASHING = _register_numeric_reply(
    'RPL_REHASHING',
    382,
    '<client> <config file> :Rehashing',
)

RPL_TIME = _register_numeric_reply(
    'RPL_TIME',
    391,
    '<client> <server> [<timestamp> [<TS offset>]] :<human-readable time>',
)

#

ERR_UNKNOWNERROR = _register_numeric_reply(
    'ERR_UNKNOWNERROR',
    400,
    '<client> <command>{ <subcommand>} :<info>',
)

ERR_NOSUCHNICK = _register_numeric_reply(
    'ERR_NOSUCHNICK',
    401,
    '<client> <nickname> :No such nick/channel',
)

ERR_NOSUCHSERVER = _register_numeric_reply(
    'ERR_NOSUCHSERVER',
    402,
    '<client> <server name> :No such server',
)

ERR_NOSUCHCHANNEL = _register_numeric_reply(
    'ERR_NOSUCHCHANNEL',
    403,
    '<client> <channel> :No such channel',
)

ERR_CANNOTSENDTOCHAN = _register_numeric_reply(
    'ERR_CANNOTSENDTOCHAN',
    404,
    '<client> <channel> :Cannot send to channel',
)

ERR_TOOMANYCHANNELS = _register_numeric_reply(
    'ERR_TOOMANYCHANNELS',
    405,
    '<client> <channel> :You have joined too many channels',
)

ERR_WASNOSUCHNICK = _register_numeric_reply(
    'ERR_WASNOSUCHNICK',
    406,
    '<client> <nickname> :There was no such nickname',
)

ERR_TOOMANYTARGETS = _register_numeric_reply(
    'ERR_TOOMANYTARGETS',
    407,
    '<target> :<error code> recipients. <abort message>',
)

ERR_NOORIGIN = _register_numeric_reply(
    'ERR_NOORIGIN',
    409,
    '<client> :No origin specified',
)

ERR_NORECIPIENT = _register_numeric_reply(
    'ERR_NORECIPIENT',
    411,
    '<client> :No recipient given (<command>)',
)

ERR_NOTEXTTOSEND = _register_numeric_reply(
    'ERR_NOTEXTTOSEND',
    412,
    '<client> :No text to send',
)

ERR_NOTOPLEVEL = _register_numeric_reply(
    'ERR_NOTOPLEVEL',
    413,
    '<mask> :No toplevel domain specified',
)

ERR_WILDTOPLEVEL = _register_numeric_reply(
    'ERR_WILDTOPLEVEL',
    414,
    '<mask> :Wildcard in toplevel domain',
)

ERR_INPUTTOOLONG = _register_numeric_reply(
    'ERR_INPUTTOOLONG',
    417,
    '<client> :Input line was too long',
)

ERR_UNKNOWNCOMMAND = _register_numeric_reply(
    'ERR_UNKNOWNCOMMAND',
    421,
    '<client> <command> :Unknown command',
)

ERR_NOMOTD = _register_numeric_reply(
    'ERR_NOMOTD',
    422,
    '<client> :MOTD File is missing',
)

ERR_NONICKNAMEGIVEN = _register_numeric_reply(
    'ERR_NONICKNAMEGIVEN',
    431,
    '<client> :No nickname given',
)

ERR_ERRONEUSNICKNAME = _register_numeric_reply(
    'ERR_ERRONEUSNICKNAME',
    432,
    '<client> <nick> :Erroneus nickname',
)

ERR_NICKNAMEINUSE = _register_numeric_reply(
    'ERR_NICKNAMEINUSE',
    433,
    '<client> <nick> :Nickname is already in use',
)

ERR_NICKCOLLISION = _register_numeric_reply(
    'ERR_NICKCOLLISION',
    436,
    '<client> <nick> :Nickname collision KILL from <user>@<host>',
)

ERR_USERNOTINCHANNEL = _register_numeric_reply(
    'ERR_USERNOTINCHANNEL',
    441,
    "<client> <nick> <channel> :They aren't on that channel",
)

ERR_NOTONCHANNEL = _register_numeric_reply(
    'ERR_NOTONCHANNEL',
    442,
    "<client> <channel> :You're not on that channel",
)

ERR_USERONCHANNEL = _register_numeric_reply(
    'ERR_USERONCHANNEL',
    443,
    '<client> <nick> <channel> :is already on channel',
)

ERR_NOTREGISTERED = _register_numeric_reply(
    'ERR_NOTREGISTERED',
    451,
    '<client> :You have not registered',
)

ERR_NEEDMOREPARAMS = _register_numeric_reply(
    'ERR_NEEDMOREPARAMS',
    461,
    '<client> <command> :Not enough parameters',
)

ERR_ALREADYREGISTERED = _register_numeric_reply(
    'ERR_ALREADYREGISTERED',
    462,
    '<client> :You may not reregister',
)

ERR_PASSWDMISMATCH = _register_numeric_reply(
    'ERR_PASSWDMISMATCH',
    464,
    '<client> :Password incorrect',
)

ERR_YOUREBANNEDCREEP = _register_numeric_reply(
    'ERR_YOUREBANNEDCREEP',
    465,
    '<client> :You are banned from this server.',
)

ERR_CHANNELISFULL = _register_numeric_reply(
    'ERR_CHANNELISFULL',
    471,
    '<client> <channel> :Cannot join channel (+l)',
)

ERR_UNKNOWNMODE = _register_numeric_reply(
    'ERR_UNKNOWNMODE',
    472,
    '<client> <modechar> :is unknown mode char to me',
)

ERR_INVITEONLYCHAN = _register_numeric_reply(
    'ERR_INVITEONLYCHAN',
    473,
    '<client> <channel> :Cannot join channel (+i)',
)

ERR_BANNEDFROMCHAN = _register_numeric_reply(
    'ERR_BANNEDFROMCHAN',
    474,
    '<client> <channel> :Cannot join channel (+b)',
)

ERR_BADCHANNELKEY = _register_numeric_reply(
    'ERR_BADCHANNELKEY',
    475,
    '<client> <channel> :Cannot join channel (+k)',
)

ERR_BADCHANMASK = _register_numeric_reply(
    'ERR_BADCHANMASK',
    476,
    '<channel> :Bad Channel Mask',
)

ERR_NOPRIVILEGES = _register_numeric_reply(
    'ERR_NOPRIVILEGES',
    481,
    "<client> :Permission Denied- You're not an IRC operator",
)

ERR_CHANOPRIVSNEEDED = _register_numeric_reply(
    'ERR_CHANOPRIVSNEEDED',
    482,
    "<client> <channel> :You're not channel operator",
)

ERR_CANTKILLSERVER = _register_numeric_reply(
    'ERR_CANTKILLSERVER',
    483,
    '<client> :You cant kill a server!',
)

ERR_NOOPERHOST = _register_numeric_reply(
    'ERR_NOOPERHOST',
    491,
    '<client> :No O-lines for your host',
)

ERR_NOSERVICEHOST = _register_numeric_reply('ERR_NOSERVICEHOST', 492)

ERR_UMODEUNKNOWNFLAG = _register_numeric_reply(
    'ERR_UMODEUNKNOWNFLAG',
    501,
    '<client> :Unknown MODE flag',
)

ERR_USERSDONTMATCH = _register_numeric_reply(
    'ERR_USERSDONTMATCH',
    502,
    '<client> :Cant change mode for other users',
)

ERR_HELPNOTFOUND = _register_numeric_reply(
    'ERR_HELPNOTFOUND',
    524,
    '<client> <subject> :No help available on this topic',
)

ERR_INVALIDKEY = _register_numeric_reply(
    'ERR_INVALIDKEY',
    525,
)

RPL_STARTTLS = _register_numeric_reply(
    'RPL_STARTTLS',
    670,
    '<client> :STARTTLS successful, proceed with TLS handshake',
)

RPL_WHOISSECURE = _register_numeric_reply(
    'RPL_WHOISSECURE',
    671,
    '<client> <nick> :is using a secure connection',
)

ERR_STARTTLS = _register_numeric_reply(
    'ERR_STARTTLS',
    691,
    '<client> :STARTTLS failed (Wrong moon phase)',
)

ERR_INVALIDMODEPARAM = _register_numeric_reply(
    'ERR_INVALIDMODEPARAM',
    696,
)

RPL_HELPSTART = _register_numeric_reply(
    'RPL_HELPSTART',
    704,
)

RPL_HELPTXT = _register_numeric_reply(
    'RPL_HELPTXT',
    705,
)

RPL_ENDOFHELP = _register_numeric_reply(
    'RPL_ENDOFHELP',
    706,
)

ERR_NOPRIVS = _register_numeric_reply(
    'ERR_NOPRIVS',
    723,
    '<client> <priv> :Insufficient oper privileges.',
)

RPL_LOGGEDIN = _register_numeric_reply(
    'RPL_LOGGEDIN',
    900,
    '<client> <nick>!<user>@<host> <account> :You are now logged in as <username>',
)

RPL_LOGGEDOUT = _register_numeric_reply(
    'RPL_LOGGEDOUT',
    901,
    '<client> <nick>!<user>@<host> :You are now logged out',
)

ERR_NICKLOCKED = _register_numeric_reply(
    'ERR_NICKLOCKED',
    902,
    '<client> :You must use a nick assigned to you',
)

RPL_SASLSUCCESS = _register_numeric_reply(
    'RPL_SASLSUCCESS',
    903,
    '<client> :SASL authentication successful',
)

ERR_SASLFAIL = _register_numeric_reply(
    'ERR_SASLFAIL',
    904,
    '<client> :SASL authentication failed',
)

ERR_SASLTOOLONG = _register_numeric_reply(
    'ERR_SASLTOOLONG',
    905,
    '<client> :SASL message too long',
)

ERR_SASLABORTED = _register_numeric_reply(
    'ERR_SASLABORTED',
    906,
    '<client> :SASL authentication aborted',
)

ERR_SASLALREADY = _register_numeric_reply(
    'ERR_SASLALREADY',
    907,
    '<client> :You have already authenticated using SASL',
)

RPL_SASLMECHS = _register_numeric_reply(
    'RPL_SASLMECHS',
    908,
    '<client> <mechanisms> :are available SASL mechanisms',
)


##


NUMERIC_REPLIES = NumericReplies(_REGISTERED_NUMERIC_REPLIES)
