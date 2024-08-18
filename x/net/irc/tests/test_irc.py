"""
TODO:
 - integration chat iface
  - https://github.com/Rapptz/discord.py
  - https://github.com/slackapi/python-slackclient

https://tools.ietf.org/html/rfc2812
https://ircv3.net/irc/
https://modern.ircdocs.horse/

https://github.com/slingamn/irctest/
https://github.com/thobbs/pure-sasl

Host:     irc.darwin.network
Port:     6697
SSL/TLS:  true
Password: smellyoulater
Channel:  #darwin
"""
import socket
import threading
import ssl

import pytest

from .. import utils


class IrcSimpleClient:

    def __init__(self, username, channel, server='irc.darwin.network', port=6697):
        super().__init__()

        self.username = username
        self.server = server
        self.port = port
        self.channel = channel

    def connect(self):
        ssl_context = ssl.create_default_context()
        rawconn = socket.create_connection((self.server, self.port)).__enter__()
        self.conn = ssl_context.wrap_socket(rawconn, server_hostname=self.server).__enter__()

    def get_response(self):
        return self.conn.recv(512).decode('utf-8')

    def send_cmd(self, cmd, message):
        command = '{} {}\r\n'.format(cmd, message).encode('utf-8')
        self.conn.send(command)

    def send_message_to_channel(self, message):
        command = 'PRIVMSG {}'.format(self.channel)
        message = ':' + message
        self.send_cmd(command, message)

    def join_channel(self):
        cmd = 'JOIN'
        channel = self.channel
        self.send_cmd(cmd, channel)


@pytest.mark.skip()
def test_irc():
    username = 'omnibus_irc_test'
    channel = '#test'

    def print_response():
        resp = client.get_response()
        if resp:
            print(f'resp: {resp}')
            msg = utils.parse_message(resp)
            print(f'msg: {msg}')
            # msg = resp.strip().split(':')
            # print('< {}> {}'.format(msg[1].split('!')[0], msg[2].strip()))

    cmd = ''
    joined = False
    client = IrcSimpleClient(username, channel)
    client.connect()

    client.send_cmd('PASS', 'smellyoulater')

    client.send_cmd('NICK', username)
    client.send_cmd('USER', '{} * * :{}'.format(username, username))

    while not joined:
        resp = client.get_response()
        print(resp.strip())

        if 'No Ident response' in resp:
            client.send_cmd('NICK', username)
            client.send_cmd('USER', '{} * * :{}'.format(username, username))

        # we're accepted, now let's join the channel!
        if '376' in resp:
            client.join_channel()

        # username already in use? try to use username with _
        if '433' in resp:
            username = '_' + username
            client.send_cmd('NICK', username)
            client.send_cmd('USER', '{} * * :{}'.format(username, username))

        # if PING send PONG with name of the server
        if 'PING' in resp:
            client.send_cmd('PONG', ':' + resp.split(':')[1])

        # we've joined
        if '366' in resp:
            joined = True

    while cmd != '/quit':
        cmd = input('< {}> '.format(username)).strip()
        if cmd == '/quit':
            client.send_cmd('QUIT', 'Good bye!')
        client.send_message_to_channel(cmd)

        # socket conn.receive blocks the program until a response is received
        # to prevent blocking program execution, receive should be threaded
        response_thread = threading.Thread(target=print_response)
        response_thread.daemon = True
        response_thread.start()


if __name__ == '__main__':
    test_irc()
