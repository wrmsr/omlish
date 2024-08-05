"""
    process_group_configs: list[ProcessGroupConfig]
"""
import configparser
import errno
import fcntl
import getopt
import glob
import grp
import io
import logging
import os
import platform
import pwd
import re
import resource
import signal
import stat
import sys
import tempfile
import typing as ta
import warnings

from omlish import dataclasses as dc

from . import poller
from . import states
from .compat import SignalReceiver
from .compat import close_fd
from .compat import expand
from .compat import import_spec
from .compat import mktempfile
from .compat import real_exit
from .compat import try_unlink
from .configs import EventListenerConfig
from .configs import EventListenerPoolConfig
from .configs import ProcessConfig
from .configs import ProcessGroupConfig
from .datatypes import Automatic
from .datatypes import Syslog
from .datatypes import auto_restart
from .datatypes import boolean
from .datatypes import byte_size
from .datatypes import dict_of_key_value_pairs
from .datatypes import existing_directory
from .datatypes import existing_dirpath
from .datatypes import gid_for_uid
from .datatypes import integer
from .datatypes import list_of_exitcodes
from .datatypes import list_of_strings
from .datatypes import logfile_name
from .datatypes import logging_level
from .datatypes import name_to_uid
from .datatypes import octal_type
from .datatypes import process_or_group_name
from .datatypes import signal_number

if ta.TYPE_CHECKING:
    from . import process


@dc.dataclass(frozen=True)
class ProcessConfigData:
    name: str
    command: str

    uid: int | None = None
    directory: str | None = None
    umask: int | None = None
    priority: int = 999

    autostart: bool = True
    autorestart: str = 'unexpected'

    startsecs: int = 1
    startretries: int = 3

    numprocs: int = 1
    numprocs_start: int = 0

    @dc.dataclass(frozen=True)
    class Log:
        file: str | None = None
        capture_maxbytes: int | None = None
        events_enabled: bool = False
        syslog: bool = False
        backups: int | None = None
        maxbytes: int | None = None

    stdout: Log = Log()
    stderr: Log = Log()

    stopsignal: str = 'TERM'
    stopwaitsecs: int = 10
    stopasgroup: bool = False

    killasgroup: bool = False

    exitcodes: ta.Iterable[int] = (0,)

    redirect_stderr: bool = False

    environment: ta.Mapping[str, str] | None = None


@dc.dataclass(frozen=True)
class ServerOptionsData:
    def add(
            self,
            name=None,  # attribute name on self
            confname=None,  # dotted config path name
            short=None,  # short option name
            long=None,  # long option name

            handler=None,  # handler (defaults to string)
            default=None,  # default value
            required=None,  # message if not provided
            flag=None,  # if not None, flag value
            env=None,  # if not None, environment variable
    ):
        pass

    user: str | None = None
    nodaemon: bool = False
    umask: int = dc.xfield(0o22, coerce=octal_type)
    directory: str | None = dc.xfield(None, coerce=existing_directory)
    logfile: str = dc.xfield('supervisord.log', coerce=existing_dirpath)
    logfile_maxbytes: int = dc.xfield(50 * 1024 * 1024, coerce=byte_size)
    logfile_backups: int = dc.xfield(10)
    loglevel: int = dc.xfield(logging.INFO, coerce=logging_level)
    pidfile: str = dc.xfield('supervisord.pid', coerce=existing_dirpath)
    identifier: str = dc.xfield('supervisor')
    child_logdir = dc.xfield(default_factory=lambda: tempfile.gettempdir(), coerce=existing_directory)
    minfds: int = 1024
    minprocs: int = 200
    nocleanup: bool = False
    strip_ansi: bool = False
    silent: bool = False


log = logging.getLogger(__name__)


class ServerContext:
    first = False
    test = False

    options: ServerOptionsData

    uid: int
    gid: int

    poller: poller.Poller

    mood: states.SupervisorStates = states.SupervisorStates.RUNNING
    pid_history: dict[int, 'process.Subprocess'] = {}

    signal_receiver: SignalReceiver

    unlink_pidfile: bool = False

    ##

    def setsignals(self) -> None:
        self.signal_receiver.install(
            signal.SIGTERM,
            signal.SIGINT,
            signal.SIGQUIT,
            signal.SIGHUP,
            signal.SIGCHLD,
            signal.SIGUSR2,
        )

    def waitpid(self) -> tuple[int | None, int | None]:
        # Need pthread_sigmask here to avoid concurrent sigchld, but Python doesn't offer in Python < 3.4.  There is
        # still a race condition here; we can get a sigchld while we're sitting in the waitpid call. However, AFAICT, if
        # waitpid is interrupted by SIGCHLD, as long as we call waitpid again (which happens every so often during the
        # normal course in the mainloop), we'll eventually reap the child that we tried to reap during the interrupted
        # call. At least on Linux, this appears to be true, or at least stopping 50 processes at once never left zombies
        # laying around.
        try:
            pid, sts = os.waitpid(-1, os.WNOHANG)
        except OSError as exc:
            code = exc.args[0]
            if code not in (errno.ECHILD, errno.EINTR):
                log.critical('waitpid error %r; a process may not be cleaned up properly' % code)
            if code == errno.EINTR:
                log.debug('EINTR during reap')
            pid, sts = None, None
        return pid, sts

    def set_uid_or_exit(self) -> None:
        """
        Set the uid of the supervisord process.  Called during supervisord startup only.  No return value.  Exits the
        process via usage() if privileges could not be dropped.
        """
        if self.uid is None:
            if os.getuid() == 0:
                warnings.warn(
                    'Supervisor is running as root.  Privileges were not dropped because no user is specified in the '
                    'config file.  If you intend to run as root, you can set user=root in the config file to avoid '
                    'this message.'
                )
        else:
            msg = drop_privileges(self.uid)
            if msg is None:
                log.info('Set uid to user %s succeeded' % self.uid)
            else:  # failed to drop privileges
                raise RuntimeError(msg)

    def set_rlimits_or_exit(self) -> None:
        """
        Set the rlimits of the supervisord process.  Called during supervisord startup only.  No return value.  Exits
        the process via usage() if any rlimits could not be set.
        """
        limits = []
        if hasattr(resource, 'RLIMIT_NOFILE'):
            limits.append({
                'msg': (
                    'The minimum number of file descriptors required to run this process is %(min_limit)s as per the '
                    '"minfds" command-line argument or config file setting. The current environment will only allow '
                    'you to open %(hard)s file descriptors.  Either raise the number of usable file descriptors in '
                    'your environment (see README.rst) or lower the minfds setting in the config file to allow the '
                    'process to start.'
                ),
                'min': self.options.minfds,
                'resource': resource.RLIMIT_NOFILE,
                'name': 'RLIMIT_NOFILE',
            })
        if hasattr(resource, 'RLIMIT_NPROC'):
            limits.append({
                'msg': (
                    'The minimum number of available processes required to run this program is %(min_limit)s as per '
                    'the "minprocs" command-line argument or config file setting. The current environment will only '
                    'allow you to open %(hard)s processes.  Either raise the number of usable processes in your '
                    'environment (see README.rst) or lower the minprocs setting in the config file to allow the '
                    'program to start.'
                ),
                'min': self.options.minprocs,
                'resource': resource.RLIMIT_NPROC,
                'name': 'RLIMIT_NPROC',
            })

        for limit in limits:
            min_limit = limit['min']
            res = limit['resource']
            msg = limit['msg']
            name = limit['name']
            name = name  # name is used below by locals()

            soft, hard = resource.getrlimit(res)

            if (soft < min_limit) and (soft != -1):  # -1 means unlimited
                if (hard < min_limit) and (hard != -1):
                    # setrlimit should increase the hard limit if we are root, if not then setrlimit raises and we print
                    # usage
                    hard = min_limit

                try:
                    resource.setrlimit(res, (min_limit, hard))
                    log.info('Increased %(name)s limit to %(min_limit)s' % locals())
                except (resource.error, ValueError):
                    raise RuntimeError(msg % locals())

    def cleanup(self) -> None:
        if self.unlink_pidfile:
            try_unlink(self.options.pidfile)
        self.poller.close()

    def cleanup_fds(self) -> None:
        # try to close any leaked file descriptors (for reload)
        start = 5
        os.closerange(start, self.options.minfds)

    def clear_auto_child_logdir(self) -> None:
        # must be called after realize()
        child_logdir = self.options.child_logdir
        fnre = re.compile(r'.+?---%s-\S+\.log\.{0,1}\d{0,4}' % self.options.identifier)
        try:
            filenames = os.listdir(child_logdir)
        except OSError:
            log.warn('Could not clear child_log dir')
            return

        for filename in filenames:
            if fnre.match(filename):
                pathname = os.path.join(child_logdir, filename)
                try:
                    os.remove(pathname)
                except OSError:
                    log.warn('Failed to clean up %r' % pathname)

    def daemonize(self) -> None:
        self.poller.before_daemonize()
        self._daemonize()
        self.poller.after_daemonize()

    def _daemonize(self) -> None:
        # To daemonize, we need to become the leader of our own session (process) group.  If we do not, signals sent to
        # our parent process will also be sent to us.   This might be bad because signals such as SIGINT can be sent to
        # our parent process during normal (uninteresting) operations such as when we press Ctrl-C in the parent
        # terminal window to escape from a logtail command. To disassociate ourselves from our parent's session group we
        # use os.setsid.  It means "set session id", which has the effect of disassociating a process from is current
        # session and process group and setting itself up as a new session leader.
        #
        # Unfortunately we cannot call setsid if we're already a session group leader, so we use "fork" to make a copy
        # of ourselves that is guaranteed to not be a session group leader.
        #
        # We also change directories, set stderr and stdout to null, and change our umask.
        #
        # This explanation was (gratefully) garnered from
        # http://www.cems.uwe.ac.uk/~irjohnso/coursenotes/lrc/system/daemons/d3.htm

        pid = os.fork()
        if pid != 0:
            # Parent
            log.debug('supervisord forked; parent exiting')
            real_exit(0)
        # Child
        log.info('daemonizing the supervisord process')
        if self.options.directory:
            try:
                os.chdir(self.options.directory)
            except OSError as err:
                log.critical("can't chdir into %r: %s" % (self.options.directory, err))
            else:
                log.info('set current directory: %r' % (self.options.directory),)
        dn = os.open('/dev/null')
        os.dup2(0, dn)
        os.dup2(1, dn)
        os.dup2(2, dn)
        os.setsid()
        os.umask(self.options.umask)
        # XXX Stevens, in his Advanced Unix book, section 13.3 (page 417) recommends calling umask(0) and closing unused
        # file descriptors.  In his Network Programming book, he additionally recommends ignoring SIGHUP and forking
        # again after the setsid() call, for obscure SVR4 reasons.

    def get_auto_child_log_name(self, name: str, identifier: str, channel: str) -> str:
        prefix = '%s-%s---%s-' % (name, channel, identifier)
        logfile = mktempfile(
            suffix='.log',
            prefix=prefix,
            dir=self.options.child_logdir,
        )
        return logfile

    def get_signal(self) -> int | None:
        return self.signal_receiver.get_signal()

    def write_pidfile(self) -> None:
        pid = os.getpid()
        try:
            with open(self.options.pidfile, 'w') as f:
                f.write('%s\n' % pid)
        except OSError:
            log.critical('could not write pidfile %s' % (self.options.pidfile,))
        else:
            self.unlink_pidfile = True
            log.info('supervisord started with pid %s' % pid)


class ServerOptions:
    uid = gid = None

    progname = sys.argv[0]
    config_file = None
    config_root = None
    here = None

    # Class variable deciding whether positional arguments are allowed. If you want positional arguments, set this to 1
    # in your subclass.
    positional_args_allowed = 0

    user = None
    logfile = None
    loglevel = None
    pidfile = None
    nodaemon = None
    silent = None
    unlink_pidfile = False
    unlink_socketfiles = False
    mood = states.SupervisorStates.RUNNING

    def __init__(self, *, require_config_file=True):
        super().__init__()

        from .options2 import ServerOptionsReader
        ServerOptionsReader()

        self.names_list = []
        self.short_options = []
        self.long_options = []
        self.options_map = {}
        self.default_map = {}
        self.required_map = {}
        self.environ_map = {}
        self.attr_priorities = {}
        self.require_config_file = require_config_file
        self.add(None, None, 'h', 'help', self.help)
        self.add(None, None, '?', None, self.help)
        self.add('config_file', None, 'c:', 'configuration=')
        self.parse_criticals = []
        self.parse_warnings = []
        self.parse_infos = []

        self.search_paths = _get_search_paths()

        self.environ_expansions = {}
        for k, v in os.environ.items():
            self.environ_expansions['ENV_%s' % k] = v

        self.config_root = Dummy()
        self.config_root.supervisord = Dummy()

        self.add(None, None, 'v', 'version', self.version)
        self.add('nodaemon', 'supervisord.nodaemon', 'n', 'nodaemon', flag=1, default=0)
        self.add('user', 'supervisord.user', 'u:', 'user=')
        self.add('umask', 'supervisord.umask', 'm:', 'umask=', octal_type, default='022')
        self.add('directory', 'supervisord.directory', 'd:', 'directory=', existing_directory)  # noqa
        self.add('logfile', 'supervisord.logfile', 'l:', 'logfile=', existing_dirpath, default='supervisord.log')  # noqa
        self.add('logfile_maxbytes', 'supervisord.logfile_maxbytes', 'y:', 'logfile_maxbytes=', byte_size, default=50 * 1024 * 1024)  # 50MB  # noqa
        self.add('logfile_backups', 'supervisord.logfile_backups', 'z:', 'logfile_backups=', integer, default=10)  # noqa
        self.add('loglevel', 'supervisord.loglevel', 'e:', 'loglevel=', logging_level, default='info')  # noqa
        self.add('pidfile', 'supervisord.pidfile', 'j:', 'pidfile=', existing_dirpath, default='supervisord.pid')  # noqa
        self.add('identifier', 'supervisord.identifier', 'i:', 'identifier=', str, default='supervisor')  # noqa
        self.add('child_logdir', 'supervisord.child_logdir', 'q:', 'child_logdir=', existing_directory, default=tempfile.gettempdir())  # noqa
        self.add('minfds', 'supervisord.minfds', 'a:', 'minfds=', int, default=1024)
        self.add('minprocs', 'supervisord.minprocs', '', 'minprocs=', int, default=200)
        self.add('nocleanup', 'supervisord.nocleanup', 'k', 'nocleanup', flag=1, default=0)  # noqa
        self.add('strip_ansi', 'supervisord.strip_ansi', 't', 'strip_ansi', flag=1, default=0)  # noqa
        self.add('silent', 'supervisord.silent', 's', 'silent', flag=1, default=0)

        self.pid_history = {}
        self.process_group_configs = []
        self.signal_receiver = SignalReceiver()
        self.poller = poller.Poller()

    ##

    def _default_config_file(self):
        """Return the name of the found config file or print usage/exit."""
        config = None
        for path in self.search_paths:
            if os.path.exists(path):
                config = path
                break
        if config is None and self.require_config_file:
            self.usage('No config file found at default paths (%s); use the -c option to specify a config file at a '
                       'different path' % ', '.join(self.search_paths))
        return config

    def help(self, dummy):
        """
        Print a long help message to stdout and exit(0).

        Occurrences of "%s" in are replaced by self.progname.
        """
        help = self.doc + '\n'
        if help.find('%s') > 0:
            help = help.replace('%s', self.progname)
        sys.stdout.write(help)
        sys.exit(0)

    def add(
            self,
            name=None,  # attribute name on self
            confname=None,  # dotted config path name
            short=None,  # short option name
            long=None,  # long option name
            handler=None,  # handler (defaults to string)
            default=None,  # default value
            required=None,  # message if not provided
            flag=None,  # if not None, flag value
            env=None,  # if not None, environment variable
    ):
        """Add information about a configuration option.

        This can take several forms:

        add(name, confname)
            Configuration option 'confname' maps to attribute 'name'
        add(name, None, short, long)
            Command line option '-short' or '--long' maps to 'name'
        add(None, None, short, long, handler)
            Command line option calls handler
        add(name, None, short, long, handler)
            Assign handler return value to attribute 'name'

        In addition, one of the following keyword arguments may be given:

        default=...  -- if not None, the default value
        required=... -- if nonempty, an error message if no value provided
        flag=...     -- if not None, flag value for command line option
        env=...      -- if not None, name of environment variable that
                        overrides the configuration file or default
        """
        if flag is not None:
            if handler is not None:
                raise ValueError('use at most one of flag= and handler=')
            if not long and not short:
                raise ValueError('flag= requires a command line flag')
            if short and short.endswith(':'):
                raise ValueError('flag= requires a command line flag')
            if long and long.endswith('='):
                raise ValueError('flag= requires a command line flag')
            handler = lambda arg, fl=flag: fl

        if short and long:
            if short.endswith(':') != long.endswith('='):
                raise ValueError('inconsistent short/long options: %r %r' % (
                    short, long))

        if short:
            if short[0] == '-':
                raise ValueError("short option should not start with '-'")
            key, rest = short[:1], short[1:]
            if rest not in ('', ':'):
                raise ValueError("short option should be 'x' or 'x:'")
            key = '-' + key
            if key in self.options_map:
                raise ValueError("duplicate short option key '%s'" % key)
            self.options_map[key] = (name, handler)
            self.short_options.append(short)

        if long:
            if long[0] == '-':
                raise ValueError("long option should not start with '-'")
            key = long
            if key[-1] == '=':
                key = key[:-1]
            key = '--' + key
            if key in self.options_map:
                raise ValueError("duplicate long option key '%s'" % key)
            self.options_map[key] = (name, handler)
            self.long_options.append(long)

        if env:
            self.environ_map[env] = (name, handler)

        if name:
            if not hasattr(self, name):
                setattr(self, name, None)
            self.names_list.append((name, confname))
            if default is not None:
                self.default_map[name] = default
            if required:
                self.required_map[name] = required

    def _set(self, attr, value, prio):
        current = self.attr_priorities.get(attr, -1)
        if prio >= current:
            setattr(self, attr, value)
            self.attr_priorities[attr] = prio

    def _realize(self, args=None, doc=None, progname=None):
        """Realize a configuration.

        Optional arguments:

        args     -- the command line arguments, less the program name
                    (default is sys.argv[1:])

        doc      -- usage message (default is __main__.__doc__)
        """
        # Provide dynamic default method arguments
        if args is None:
            args = sys.argv[1:]
        if progname is None:
            progname = sys.argv[0]
        if doc is None:
            try:
                import __main__
                doc = __main__.__doc__
            except Exception:
                pass
        self.progname = progname
        self.doc = doc

        self.options = []
        self.args = []

        # Call getopt
        try:
            self.options, self.args = getopt.getopt( args, ''.join(self.short_options), self.long_options)
        except getopt.error as exc:
            self.usage(str(exc))

        # Check for positional args
        if self.args and not self.positional_args_allowed:
            self.usage('positional arguments are not supported: %s' % (str(self.args)))

        # Process options returned by getopt
        for opt, arg in self.options:
            name, handler = self.options_map[opt]
            if handler is not None:
                try:
                    arg = handler(arg)
                except ValueError as msg:
                    self.usage('invalid value for %s %r: %s' % (opt, arg, msg))
            if name and arg is not None:
                if getattr(self, name) is not None:
                    self.usage('conflicting command line option %r' % opt)
                self._set(name, arg, 2)

        # Process environment variables
        for envvar in self.environ_map.keys():
            name, handler = self.environ_map[envvar]
            if envvar in os.environ:
                value = os.environ[envvar]
                if handler is not None:
                    try:
                        value = handler(value)
                    except ValueError as msg:
                        self.usage('invalid environment value for %s %r: %s'
                                   % (envvar, value, msg))
                if name and value is not None:
                    self._set(name, value, 1)

        if self.config_file is None:
            self.config_file = self.default_config_file()

        self.process_config()

    def _process_config(self, do_usage=True):
        """Process configuration data structure.

        This includes reading config file if necessary, setting defaults etc.
        """
        if self.config_file:
            self.process_config_file(do_usage)

        # Copy config options to attributes of self.  This only fills in options that aren't already set from the
        # command line.
        for name, confname in self.names_list:
            if confname:
                parts = confname.split('.')
                obj = self.config_root
                for part in parts:
                    if obj is None:
                        break
                    # Here AttributeError is not a user error!
                    obj = getattr(obj, part)
                self._set(name, obj, 0)

        # Process defaults
        for name, value in self.default_map.items():
            if getattr(self, name) is None:
                setattr(self, name, value)

        # Process required options
        for name, message in self.required_map.items():
            if getattr(self, name) is None:
                self.usage(message)

    def process_config_file(self, do_usage):
        # Process config file
        if not hasattr(self.config_file, 'read'):
            self.here = os.path.abspath(os.path.dirname(self.config_file))
        try:
            self.read_config(self.config_file)
        except ValueError as msg:
            if do_usage:
                # if this is not called from an RPC method, run usage and exit.
                self.usage(str(msg))
            else:
                # if this is called from an RPC method, raise an error
                raise ValueError(msg)

    def get_plugins(self, parser, factory_key, section_prefix):
        factories = []

        for section in parser.sections():
            if not section.startswith(section_prefix):
                continue

            name = section.split(':', 1)[1]
            factory_spec = parser.saneget(section, factory_key, None)
            if factory_spec is None:
                raise ValueError('section [%s] does not specify a %s' % (section, factory_key))
            try:
                factory = import_spec(factory_spec)
            except (AttributeError, ImportError):
                raise ValueError('%s cannot be resolved within [%s]' % (factory_spec, section))

            extras = {}
            for k in parser.options(section):
                if k != factory_key:
                    extras[k] = parser.saneget(section, k)
            factories.append((name, factory, extras))

        return factories

    def read_include_config(self, fp, parser, expansions):
        if parser.has_section('include'):
            parser.expand_here(self.here)
            if not parser.has_option('include', 'files'):
                raise ValueError('.ini file has [include] section, but no files setting')
            files = parser.get('include', 'files')
            files = expand(files, expansions, 'include.files')
            files = files.split()
            if hasattr(fp, 'name'):
                base = os.path.dirname(os.path.abspath(fp.name))
            else:
                base = '.'
            for pattern in files:
                pattern = os.path.join(base, pattern)
                filenames = glob.glob(pattern)
                if not filenames:
                    self.parse_warnings.append('No file matches via include "%s"' % pattern)
                    continue
                for filename in sorted(filenames):
                    self.parse_infos.append('Included extra file "%s" during parsing' % filename)
                    try:
                        parser.read(filename)
                    except configparser.ParsingError as why:
                        raise ValueError(str(why))
                    else:
                        parser.expand_here(os.path.abspath(os.path.dirname(filename)))

    ##

    def version(self, dummy) -> None:
        """Print version to stdout and exit(0)."""
        sys.stdout.write('%s\n' % VERSION)
        sys.exit(0)

    def default_config_file(self):
        if os.getuid() == 0:
            warnings.warn(
                'Supervisord is running as root and it is searching for its configuration file in default locations '
                '(including its current working directory); you probably want to specify a "-c" argument specifying an '
                'absolute path to a configuration file for improved security.',
            )
        return self._default_config_file(self)

    def realize(self, *arg, **kw):
        self._realize(*arg, **kw)
        section = self.config_root.supervisord

        # Additional checking of user option; set uid and gid
        if self.user is not None:
            try:
                uid = name_to_uid(self.user)
            except ValueError as msg:
                self.usage(msg)  # invalid user
            self.uid = uid
            self.gid = gid_for_uid(uid)

        if not self.loglevel:
            self.loglevel = section.loglevel

        if self.logfile:
            logfile = self.logfile
        else:
            logfile = section.logfile

        if logfile != 'syslog':
            # if the value for logfile is "syslog", we don't want to normalize the path to something like
            # $CWD/syslog.log, but instead use the syslog service.
            self.logfile = normalize_path(logfile)

        if self.pidfile:
            pidfile = self.pidfile
        else:
            pidfile = section.pidfile

        self.pidfile = normalize_path(pidfile)

    def process_config(self, do_usage=True):
        self._process_config(do_usage=do_usage)

        new = self.config_root.supervisord.process_group_configs
        self.process_group_configs = new

    def read_config(self, fp):
        # Clear parse messages, since we may be re-reading the config a second time after a reload.
        self.parse_criticals = []
        self.parse_warnings = []
        self.parse_infos = []

        section = self.config_root.supervisord
        need_close = False
        if not hasattr(fp, 'read'):
            if not os.path.exists(fp):
                raise ValueError('could not find config file %s' % fp)
            try:
                fp = open(fp, 'r')
                need_close = True
            except OSError:
                raise ValueError('could not read config file %s' % fp)

        parser = UnhosedConfigParser()
        parser.expansions = self.environ_expansions
        try:
            try:
                parser.read_file(fp)
            except AttributeError:
                parser.readfp(fp)
        except configparser.ParsingError as why:
            raise ValueError(str(why))
        finally:
            if need_close:
                fp.close()

        host_node_name = platform.node()
        expansions = {
            'here': self.here,
            'host_node_name': host_node_name,
        }
        expansions.update(self.environ_expansions)

        self.read_include_config(fp, parser, expansions)

        sections = parser.sections()
        if 'supervisord' not in sections:
            raise ValueError('.ini file does not include supervisord section')

        common_expansions = {'here': self.here}

        def get(opt, default, **kwargs):
            expansions = kwargs.get('expansions', {})
            expansions.update(common_expansions)
            kwargs['expansions'] = expansions
            return parser.getdefault(opt, default, **kwargs)

        section.minfds = integer(get('minfds', 1024))
        section.minprocs = integer(get('minprocs', 200))

        directory = get('directory', None)
        if directory is None:
            section.directory = None
        else:
            section.directory = existing_directory(directory)

        section.user = get('user', None)
        section.umask = octal_type(get('umask', '022'))
        section.logfile = existing_dirpath(get('logfile', 'supervisord.log'))
        section.logfile_maxbytes = byte_size(get('logfile_maxbytes', '50MB'))
        section.logfile_backups = integer(get('logfile_backups', 10))
        section.loglevel = logging_level(get('loglevel', 'info'))
        section.pidfile = existing_dirpath(get('pidfile', 'supervisord.pid'))
        section.identifier = get('identifier', 'supervisor')
        section.nodaemon = boolean(get('nodaemon', 'false'))
        section.silent = boolean(get('silent', 'false'))

        tempdir = tempfile.gettempdir()
        section.child_logdir = existing_directory(get('child_logdir', tempdir))
        section.nocleanup = boolean(get('nocleanup', 'false'))
        section.strip_ansi = boolean(get('strip_ansi', 'false'))

        environ_str = get('environment', '')
        environ_str = expand(environ_str, expansions, 'environment')
        section.environment = dict_of_key_value_pairs(environ_str)

        # extend expansions for global from [supervisord] environment definition
        for k, v in section.environment.items():
            self.environ_expansions['ENV_%s' % k] = v

        section.process_group_configs = self.process_groups_from_parser(parser)
        for group in section.process_group_configs:
            for proc in group.process_configs:
                env = section.environment.copy()
                env.update(proc.environment)
                proc.environment = env
        return section

    def process_groups_from_parser(self, parser):
        groups = []
        all_sections = parser.sections()
        homogeneous_exclude = []

        common_expansions = {'here': self.here}

        def get(section, opt, default, **kwargs):
            expansions = kwargs.get('expansions', {})
            expansions.update(common_expansions)
            kwargs['expansions'] = expansions
            return parser.saneget(section, opt, default, **kwargs)

        # process heterogeneous groups
        for section in all_sections:
            if not section.startswith('group:'):
                continue
            group_name = process_or_group_name(section.split(':', 1)[1])
            programs = list_of_strings(get(section, 'programs', None))
            priority = integer(get(section, 'priority', 999))
            group_processes = []
            for program in programs:
                program_section = 'program:%s' % program
                if program_section not in all_sections:
                    raise ValueError('[%s] names unknown program %s' % (section, program))
                homogeneous_exclude.append(program_section)
                processes = self.processes_from_section(parser, program_section, group_name, ProcessConfig)

                group_processes.extend(processes)
            groups.append(ProcessGroupConfig(self, group_name, priority, group_processes))

        # process "normal" homogeneous groups
        for section in all_sections:
            if ((not section.startswith('program:')) or section in homogeneous_exclude):
                continue
            program_name = process_or_group_name(section.split(':', 1)[1])
            priority = integer(get(section, 'priority', 999))
            processes = self.processes_from_section(parser, section, program_name, ProcessConfig)
            groups.append(ProcessGroupConfig(self, program_name, priority, processes))

        # process "event listener" homogeneous groups
        for section in all_sections:
            if not section.startswith('eventlistener:'):
                continue
            pool_name = section.split(':', 1)[1]

            # give listeners a "high" default priority so they are started first
            # and stopped last at mainloop exit
            priority = integer(get(section, 'priority', -1))

            buffer_size = integer(get(section, 'buffer_size', 10))
            if buffer_size < 1:
                raise ValueError('[%s] section sets invalid buffer_size (%d)' % (section, buffer_size))

            result_handler = get(section, 'result_handler', 'supervisor.dispatchers:default_handler')
            try:
                result_handler = self.import_spec(result_handler)
            except (AttributeError, ImportError):
                raise ValueError('%s cannot be resolved within [%s]' % (
                    result_handler, section))

            pool_event_names = [x.upper() for x in list_of_strings(get(section, 'events', ''))]
            pool_event_names = set(pool_event_names)
            if not pool_event_names:
                raise ValueError('[%s] section requires an "events" line' % section)

            from .events import EventTypes
            pool_events = []
            for pool_event_name in pool_event_names:
                pool_event = getattr(EventTypes, pool_event_name, None)
                if pool_event is None:
                    raise ValueError('Unknown event type %s in [%s] events' % (pool_event_name, section))
                pool_events.append(pool_event)

            redirect_stderr = boolean(get(section, 'redirect_stderr', 'false'))
            if redirect_stderr:
                raise ValueError('[%s] section sets redirect_stderr=true '
                                 'but this is not allowed because it will interfere '
                                 'with the eventlistener protocol' % section)

            processes = self.processes_from_section(parser, section, pool_name, EventListenerConfig)

            groups.append(
                EventListenerPoolConfig(
                    self,
                    pool_name,
                    priority,
                    processes,
                    buffer_size,
                    pool_events,
                    result_handler,
                ),
            )

        groups.sort()
        return groups

    def processes_from_section(self, parser, section, group_name, klass=None):
        try:
            return self._processes_from_section(parser, section, group_name, klass)
        except ValueError as e:
            filename = parser.section_to_file.get(section, self.config_file)
            raise ValueError('%s in section %r (file: %r)' % (e, section, filename))

    def _processes_from_section(self, parser, section, group_name, klass=None):
        if klass is None:
            klass = ProcessConfig
        programs = []

        program_name = process_or_group_name(section.split(':', 1)[1])
        host_node_name = platform.node()
        common_expansions = {
            'here': self.here,
            'program_name': program_name,
            'host_node_name': host_node_name,
            'group_name': group_name,
        }

        def get(section, opt, *args, **kwargs):
            expansions = kwargs.get('expansions', {})
            expansions.update(common_expansions)
            kwargs['expansions'] = expansions
            return parser.saneget(section, opt, *args, **kwargs)

        priority = integer(get(section, 'priority', 999))
        autostart = boolean(get(section, 'autostart', 'true'))
        autorestart = auto_restart(get(section, 'autorestart', 'unexpected'))
        startsecs = integer(get(section, 'startsecs', 1))
        startretries = integer(get(section, 'startretries', 3))
        stopsignal = signal_number(get(section, 'stopsignal', 'TERM'))
        stopwaitsecs = integer(get(section, 'stopwaitsecs', 10))
        stopasgroup = boolean(get(section, 'stopasgroup', 'false'))
        killasgroup = boolean(get(section, 'killasgroup', stopasgroup))
        exitcodes = list_of_exitcodes(get(section, 'exitcodes', '0'))
        # see also redirect_stderr check in process_groups_from_parser()
        redirect_stderr = boolean(get(section, 'redirect_stderr', 'false'))
        numprocs = integer(get(section, 'numprocs', 1))
        numprocs_start = integer(get(section, 'numprocs_start', 0))
        environment_str = get(section, 'environment', '', do_expand=False)
        stdout_cmaxbytes = byte_size(get(section, 'stdout_capture_maxbytes', '0'))
        stdout_events = boolean(get(section, 'stdout_events_enabled', 'false'))
        stderr_cmaxbytes = byte_size(get(section, 'stderr_capture_maxbytes', '0'))
        stderr_events = boolean(get(section, 'stderr_events_enabled', 'false'))

        # find uid from "user" option
        user = get(section, 'user', None)
        if user is None:
            uid = None
        else:
            uid = name_to_uid(user)

        umask = get(section, 'umask', None)
        if umask is not None:
            umask = octal_type(umask)

        process_name = process_or_group_name(
            get(section, 'process_name', '%(program_name)s', do_expand=False),
        )

        if numprocs > 1:
            if '%(process_num)' not in process_name:
                # process_name needs to include process_num when we represent a group of processes
                raise ValueError('%(process_num) must be present within process_name when numprocs > 1')

        if stopasgroup and not killasgroup:
            raise ValueError('Cannot set stopasgroup=true and killasgroup=false')

        for process_num in range(numprocs_start, numprocs + numprocs_start):
            expansions = common_expansions
            expansions.update({'process_num': process_num, 'numprocs': numprocs})
            expansions.update(self.environ_expansions)

            environment = dict_of_key_value_pairs(expand(environment_str, expansions, 'environment'))

            # extend expansions for process from [program:x] environment definition
            for k, v in environment.items():
                expansions['ENV_%s' % k] = v

            directory = get(section, 'directory', None)

            logfiles = {}

            for k in ('stdout', 'stderr'):
                lf_key = '%s_logfile' % k
                lf_val = get(section, lf_key, Automatic)
                if isinstance(lf_val, str):
                    lf_val = expand(lf_val, expansions, lf_key)
                lf_val = logfile_name(lf_val)
                logfiles[lf_key] = lf_val

                bu_key = '%s_logfile_backups' % k
                backups = integer(get(section, bu_key, 10))
                logfiles[bu_key] = backups

                mb_key = '%s_logfile_maxbytes' % k
                maxbytes = byte_size(get(section, mb_key, '50MB'))
                logfiles[mb_key] = maxbytes

                sy_key = '%s_syslog' % k
                syslog = boolean(get(section, sy_key, False))
                logfiles[sy_key] = syslog

                # rewrite deprecated "syslog" magic logfile into the equivalent
                # TODO remove this in a future version
                if lf_val is Syslog:
                    self.parse_warnings.append(
                        'For [%s], %s=syslog but this is deprecated and will be removed. Use %s=true to enable '
                        ' syslog instead.' % (section, lf_key, sy_key))
                    logfiles[lf_key] = lf_val = None
                    logfiles[sy_key] = True

                if lf_val is Automatic and not maxbytes:
                    self.parse_warnings.append(
                        'For [%s], AUTO logging used for %s without rollover, set maxbytes > 0 to avoid filling up '
                        'filesystem unintentionally' % (section, lf_key))

            if redirect_stderr:
                if logfiles['stderr_logfile'] not in (Automatic, None):
                    self.parse_warnings.append(
                        'For [%s], redirect_stderr=true but stderr_logfile has also been set to a filename, the '
                        'filename has been ignored' % section)
                # never create an stderr logfile when redirected
                logfiles['stderr_logfile'] = None

            command = get(section, 'command', None, expansions=expansions)
            if command is None:
                raise ValueError(
                    'program section %s does not specify a command' % section)

            pconfig = klass(
                self,
                name=expand(process_name, expansions, 'process_name'),
                command=command,
                directory=directory,
                umask=umask,
                priority=priority,
                autostart=autostart,
                autorestart=autorestart,
                startsecs=startsecs,
                startretries=startretries,
                uid=uid,
                stdout_logfile=logfiles['stdout_logfile'],
                stdout_capture_maxbytes=stdout_cmaxbytes,
                stdout_events_enabled=stdout_events,
                stdout_logfile_backups=logfiles['stdout_logfile_backups'],
                stdout_logfile_maxbytes=logfiles['stdout_logfile_maxbytes'],
                stdout_syslog=logfiles['stdout_syslog'],
                stderr_logfile=logfiles['stderr_logfile'],
                stderr_capture_maxbytes=stderr_cmaxbytes,
                stderr_events_enabled=stderr_events,
                stderr_logfile_backups=logfiles['stderr_logfile_backups'],
                stderr_logfile_maxbytes=logfiles['stderr_logfile_maxbytes'],
                stderr_syslog=logfiles['stderr_syslog'],
                stopsignal=stopsignal,
                stopwaitsecs=stopwaitsecs,
                stopasgroup=stopasgroup,
                killasgroup=killasgroup,
                exitcodes=exitcodes,
                redirect_stderr=redirect_stderr,
                environment=environment)

            programs.append(pconfig)

        programs.sort()  # asc by priority
        return programs
