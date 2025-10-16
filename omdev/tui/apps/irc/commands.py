import abc
import typing as ta

from omlish import check
from omlish import lang
from omlish.argparse import all as argparse


if ta.TYPE_CHECKING:
    from .app import IrcApp


##


class IrcCommand(abc.ABC):
    """Abstract base class for IRC commands."""

    def __init__(self) -> None:
        super().__init__()

        self.__parser: argparse.ArgumentParser = argparse.NoExitArgumentParser(
            prog=self.name,
            description=self.description,
            formatter_class=self._HelpFormatter,
        )
        self._configure_parser(self.__parser)

    #

    @property
    def name(self) -> str:
        return lang.camel_to_snake(type(self).__name__.removesuffix('IrcCommand'))

    @property
    def description(self) -> str | None:
        return None

    class _HelpFormatter(argparse.HelpFormatter):
        def start_section(self, heading):
            return super().start_section(heading.title())

        def add_usage(self, usage, actions, groups, prefix=None):
            if prefix is None:
                prefix = 'Usage: '
            return super().add_usage(usage, actions, groups, prefix)

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    #

    @ta.final
    async def run(self, app: 'IrcApp', argv: list[str]) -> None:
        try:
            args = self.__parser.parse_args(argv)
        except argparse.ArgumentError:
            await app.add_message('system', self.__parser.format_help())
            return

        await self._run_args(app, args)

    @abc.abstractmethod
    async def _run_args(self, app: 'IrcApp', args: argparse.Namespace) -> None:
        raise NotImplementedError


class ConnectIrcCommand(IrcCommand):
    """Connect to an IRC server."""

    description: ta.ClassVar[str] = 'Connect to an IRC server'

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('server', help='IRC server hostname')
        parser.add_argument('port', type=int, help='Port number')
        parser.add_argument('nickname', help='Your nickname')
        parser.add_argument(
            '--ssl',
            action='store_true',
            help='Use SSL/TLS (auto-detected for common ports)',
        )

    async def _run_args(self, app: 'IrcApp', args: argparse.Namespace) -> None:
        use_ssl = args.ssl or None  # None triggers auto-detection
        ssl_msg = ' (SSL)' if args.ssl or args.port in (6697, 6698, 7000, 7070, 9999) else ''
        await app.add_message('system', f'Connecting to {args.server}:{args.port}{ssl_msg} as {args.nickname}...')
        success = await check.not_none(app.client).connect(
            args.server,
            args.port,
            args.nickname,
            use_ssl=use_ssl if args.ssl else None,
        )
        if success:
            await app.add_message('system', 'Connected!')


class JoinIrcCommand(IrcCommand):
    """Join a channel."""

    description: ta.ClassVar[str] = 'Join an IRC channel'

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('channel', help='Channel name (# prefix optional)')

    async def _run_args(self, app: 'IrcApp', args: argparse.Namespace) -> None:
        channel = args.channel
        if not channel.startswith('#'):
            channel = '#' + channel

        if app.client and app.client.connected:
            await app.client.join(channel)
            app.get_or_create_window(channel)
            app.switch_to_window(channel)
        else:
            await app.add_message('system', 'Not connected to server')


class PartIrcCommand(IrcCommand):
    """Leave a channel."""

    description: ta.ClassVar[str] = 'Leave an IRC channel'

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('reason', nargs='*', help='Part message (optional)')

    async def _run_args(self, app: 'IrcApp', args: argparse.Namespace) -> None:
        if app.current_channel:
            reason = ' '.join(args.reason) if args.reason else 'Leaving'
            if app.client and app.client.connected:
                await app.client.part(app.current_channel, reason)
        else:
            await app.add_message('system', 'Not in a channel')


class NamesIrcCommand(IrcCommand):
    """Request names list for current channel."""

    description: ta.ClassVar[str] = 'Request names list for current channel'

    async def _run_args(self, app: 'IrcApp', args: argparse.Namespace) -> None:
        if app.current_channel:
            if app.client and app.client.connected:
                await app.client.names(app.current_channel)
            else:
                await app.add_message('system', 'Not connected to server')
        else:
            await app.add_message('system', 'Not in a channel')


class QuitIrcCommand(IrcCommand):
    """Quit IRC."""

    description: ta.ClassVar[str] = 'Quit IRC and exit the application'

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('message', nargs='*', help='Quit message (optional)')

    async def _run_args(self, app: 'IrcApp', args: argparse.Namespace) -> None:
        reason = ' '.join(args.message) if args.message else 'Quit'
        if app.client and app.client.connected:
            await app.client.quit(reason)
        await app.add_message('system', 'Goodbye!')
        app.exit()


##


ALL_COMMANDS: ta.Mapping[str, IrcCommand] = {
    'connect': ConnectIrcCommand(),
    'join': JoinIrcCommand(),
    'part': PartIrcCommand(),
    'names': NamesIrcCommand(),
    'quit': QuitIrcCommand(),
}
