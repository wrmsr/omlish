# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

# You can run this .tac file directly with:
#    twistd -ny demo_manhole.tac

"""
socat - UNIX-CONNECT:manhole.sock

An interactive Python interpreter with syntax coloring.

Nothing interesting is actually defined here.  Two listening ports are
set up and attached to protocols which know how to properly set up a
ColoredManhole instance.
"""

from twisted.application import internet, service
from twisted.conch.insults import insults
from twisted.conch.manhole import ColoredManhole
from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm
from twisted.conch.telnet import TelnetTransport, TelnetBootstrapProtocol
from twisted.cred import checkers, portal
from twisted.internet import protocol, reactor


def makeService(args):
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(username="password")

    f = protocol.ServerFactory()
    f.protocol = lambda: TelnetTransport(
        TelnetBootstrapProtocol,
        insults.ServerProtocol,
        args['protocolFactory'],
        *args.get('protocolArgs', ()),
        **args.get('protocolKwArgs', {}),
    )
    tsvc = internet.TCPServer(args['telnet'], f)

    def chainProtocolFactory():
        return insults.ServerProtocol(
            args['protocolFactory'],
            *args.get('protocolArgs', ()),
            **args.get('protocolKwArgs', {}),
        )

    rlm = TerminalRealm()
    rlm.chainedProtocolFactory = chainProtocolFactory
    ptl = portal.Portal(rlm, [checker])
    f = ConchFactory(ptl)
    csvc = internet.TCPServer(args['ssh'], f)

    m = service.MultiService()
    tsvc.setServiceParent(m)
    csvc.setServiceParent(m)
    return m


def _main():
    # application = service.Application("Interactive Python Interpreter")
    #
    # makeService({
    #     'protocolFactory': ColoredManhole,
    #     'protocolArgs': (None,),
    #     'telnet': 6023,
    #     'ssh': 6022,
    # }).setServiceParent(application)

    def make_manhole(namespace):
        f = protocol.ServerFactory()
        f.protocol = lambda: TelnetTransport(
            TelnetBootstrapProtocol,
            insults.ServerProtocol,
            ColoredManhole,
            namespace,
        )
        return f

    manhole = make_manhole({})
    # reactor.listenTCP(6024, manhole)
    reactor.listenUNIX('manhole.sock', manhole)
    reactor.run()


if __name__ == '__main__':
    _main()
