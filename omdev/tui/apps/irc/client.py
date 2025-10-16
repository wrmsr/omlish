import asyncio
import ssl
import typing as ta

from omlish import check


##


class IrcClient:
    """Simple asyncio-based IRC client."""

    def __init__(
            self,
            callback: ta.Callable[[str, str], ta.Awaitable[None]],
    ) -> None:
        super().__init__()

        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.callback: ta.Callable[[str, str], ta.Awaitable[None]] = callback
        self.nickname: str = ''
        self.connected: bool = False
        self.read_task: asyncio.Task | None = None

    async def shutdown(self) -> None:
        if self.read_task is not None:
            self.read_task.cancel()
            await self.read_task

    async def connect(
            self,
            server: str,
            port: int,
            nickname: str,
            realname: str = 'Textual IRC',
            use_ssl: bool | None = None,
    ) -> bool:
        """Connect to IRC server."""

        check.none(self.read_task)

        try:
            # Auto-detect SSL for common SSL ports if not explicitly specified
            if use_ssl is None:
                use_ssl = port in (6697, 6698, 7000, 7070, 9999)

            ssl_context = None
            if use_ssl:
                ssl_context = ssl.create_default_context()

            self.reader, self.writer = await asyncio.open_connection(
                server, port, ssl=ssl_context,
            )
            self.nickname = nickname
            self.connected = True

            # Send initial IRC handshake
            await self.send_raw(f'NICK {nickname}')
            await self.send_raw(f'USER {nickname} 0 * :{realname}')

            # Start reading messages
            self.read_task = asyncio.create_task(self._read_loop())

            return True

        except Exception as e:  # noqa  # FIXME
            await self.callback('system', f'Connection error: {e}')
            return False

    async def send_raw(self, message: str) -> None:
        """Send raw IRC message."""

        if self.writer:
            self.writer.write(f'{message}\r\n'.encode())
            await self.writer.drain()

    async def join(self, channel: str) -> None:
        """Join a channel."""

        await self.send_raw(f'JOIN {channel}')

    async def part(self, channel: str, message: str = 'Leaving') -> None:
        """Leave a channel."""

        await self.send_raw(f'PART {channel} :{message}')

    async def privmsg(self, target: str, message: str) -> None:
        """Send a message to a channel or user."""

        await self.send_raw(f'PRIVMSG {target} :{message}')

    async def names(self, channel: str) -> None:
        """Request names list for a channel."""

        await self.send_raw(f'NAMES {channel}')

    async def quit(self, message: str = 'Quit') -> None:
        """Quit IRC."""

        await self.send_raw(f'QUIT :{message}')
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False

    async def _read_loop(self) -> None:
        """Read messages from server."""

        try:
            while self.connected and self.reader:
                line = await self.reader.readline()
                if not line:
                    break

                message = line.decode('utf-8', errors='ignore').strip()
                if message:
                    await self._handle_message(message)

        except Exception as e:  # noqa  # FIXME
            await self.callback('system', f'Read error: {e}')

        finally:
            self.connected = False
            await self.callback('system', 'Disconnected from server')

    async def _handle_message(self, message: str) -> None:
        """Parse and handle IRC messages."""

        # Handle PING
        if message.startswith('PING'):
            pong = message.replace('PING', 'PONG', 1)
            await self.send_raw(pong)
            return

        # Parse IRC message
        prefix = ''
        if message.startswith(':'):
            prefix, _, message = message[1:].partition(' ')

        parts = message.split(' ', 2)
        command = parts[0] if parts else ''
        params = parts[1:] if len(parts) > 1 else []

        # Extract nickname from prefix
        nick = prefix.split('!')[0] if '!' in prefix else prefix

        # Handle different message types
        if command == 'PRIVMSG' and len(params) >= 2:
            target = params[0]
            text = params[1]
            text = text.removeprefix(':')

            window = target if target.startswith('#') else nick
            await self.callback(window, f'<{nick}> {text}')

        elif command == 'JOIN' and params:
            channel = params[0].lstrip(':')
            await self.callback(channel, f'* {nick} has joined {channel}')

        elif command == 'PART' and params:
            channel = params[0]
            reason = params[1].lstrip(':') if len(params) > 1 else ''
            msg = f'* {nick} has left {channel}'
            if reason:
                msg += f' ({reason})'
            await self.callback(channel, msg)

        elif command == 'QUIT':
            reason = params[0].lstrip(':') if params else ''
            msg = f'* {nick} has quit'
            if reason:
                msg += f' ({reason})'
            await self.callback('system', msg)

        elif command == 'NICK' and params:
            new_nick = params[0].lstrip(':')
            await self.callback('system', f'* {nick} is now known as {new_nick}')

        elif command.isdigit():
            # Numeric replies
            reply_text = ' '.join(params).lstrip(':')
            await self.callback('system', f'[{command}] {reply_text}')
        else:
            # Unhandled messages go to system
            await self.callback('system', message)
