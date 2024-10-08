
from asyncio import Protocol
from asyncio import get_event_loop

from omserv.secrets import load_secrets

from ..connection import IrcClientConnection
from ..constants import RPL_MYINFO
from ..events import Error
from ..events import Join
from ..events import Reply


class MessageSendProtocol(Protocol):
    def __init__(self, nickname: str, channel: str, message: str) -> None:
        self.nickname = nickname
        self.channel = channel
        self.message = message
        self.conn = IrcClientConnection()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.conn.send_command('NICK', self.nickname)
        self.conn.send_command('USER', 'ircproto', '0', 'ircproto example client')
        self.send_outgoing_data()

    def connection_lost(self, exc):
        get_event_loop().stop()

    def data_received(self, data: bytes):
        close_connection = False
        for event in self.conn.feed_data(data):
            print('<<< ' + event.encode().rstrip())
            if isinstance(event, Reply):
                if event.is_error:
                    self.transport.abort()
                    return
                elif event.code == RPL_MYINFO:
                    self.conn.send_command('JOIN', self.channel)
            elif isinstance(event, Join):
                self.conn.send_command('PRIVMSG', self.channel, self.message)
                self.conn.send_command('QUIT')
                close_connection = True
            elif isinstance(event, Error):
                self.transport.abort()
                return

        self.send_outgoing_data()
        if close_connection:
            self.transport.close()

    def send_outgoing_data(self):
        # This is more complicated than it should because we want to print all outgoing data here. Normally,
        # self.transport.write(self.conn.data_to_send()) would suffice.
        output = self.conn.data_to_send()
        if output:
            print('>>> ' + output.decode('utf-8').replace('\r\n', '\r\n>>> ').rstrip('> \r\n'))
            self.transport.write(output)


def _main():
    # parser = ArgumentParser(description='A sample IRC client')
    # parser.add_argument('host', help='address of irc server (foo.bar.baz or foo.bar.baz:port)')
    # parser.add_argument('nickname', help='nickname to register as')
    # parser.add_argument('channel', help='channel to join once registered')
    # parser.add_argument('message', help='message to send once joined')
    # args = parser.parse_args()
    # host, _, port = args.host.partition(':')

    cfg = load_secrets()
    host = cfg['irc_host']
    port = cfg['irc_port']
    channel = cfg['irc_channel']
    nickname = cfg['irc_nick']
    message = 'barf'

    loop = get_event_loop()
    protocol = MessageSendProtocol(nickname, channel, message)
    import ssl
    sc = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    loop.run_until_complete(loop.create_connection(lambda: protocol, host, int(port or 6667), ssl=sc))
    loop.run_forever()


if __name__ == '__main__':
    _main()
