import pytest

from .. import triotp2 as t2


class echo_server(t2.ServerApp):

    @staticmethod
    async def echo(message):
        return await t2.gen_server.call(__name__, ('echo', message))

    @staticmethod
    async def stop():
        await t2.gen_server.cast(__name__, 'stop')

    ##

    async def start(self, start_arg):
        await t2.gen_server.start(self, init_arg=None, name=__name__)

    async def init(self, _init_arg):
        return 'nostate'

    async def terminate(self, reason, state):
        print('exited with reason', reason, 'and state', state)

    async def handle_call(self, message, _caller, state):
        match message:
            case ('echo', message):
                return (t2.Reply(message), state)

            case _:
                exc = NotImplementedError('unknown command')
                return (t2.Reply(exc), state)

    async def handle_cast(self, message, state):
        match message:
            case 'stop':
                return (t2.Stop(), state)

            case _:
                exc = NotImplementedError('unknown command')
                return (t2.Stop(exc), state)


async def echo_client():
    response = await echo_server.echo('hello')
    assert response == 'hello'

    response = await echo_server.echo('world')
    assert response == 'world'

    await echo_server.stop()


@pytest.mark.trio
async def test_echo_server():
    t2.init_mailboxes()

    children = [
        t2.ChildSpec(
            id='server',
            task=echo_server().start,
            args=[None],
            restart=t2.RestartStrategy.TRANSIENT,
        ),
        t2.ChildSpec(
            id='client',
            task=echo_client,
            args=[],
            restart=t2.RestartStrategy.TRANSIENT,
        ),
    ]
    opts = t2.SupervisorOptions(
        max_restarts=3,
        max_seconds=5,
    )
    await t2.supervisor.start(children, opts)
