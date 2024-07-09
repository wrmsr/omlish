import trio

from .. import triotp2 as t2


class api:
    @staticmethod
    async def get(key):
        return await t2.gen_server_call(__name__, ('api_get', key))

    @staticmethod
    async def set(key, val):
        return await t2.gen_server_call(__name__, ('api_set', key, val))

    @staticmethod
    async def clear():
        return await t2.gen_server_call(__name__, 'api_clear')


class special_call:
    @staticmethod
    async def delayed(nursery):
        return await t2.gen_server_call(__name__, ('special_call_delayed', nursery))

    @staticmethod
    async def timedout(timeout):
        return await t2.gen_server_call(__name__, 'special_call_timedout', timeout=timeout)

    @staticmethod
    async def stopped():
        return await t2.gen_server_call(__name__, 'special_call_stopped')

    @staticmethod
    async def failure():
        return await t2.gen_server_call(__name__, 'special_call_failure')


class special_cast:
    @staticmethod
    async def normal():
        await t2.gen_server_cast(__name__, 'special_cast_normal')

    @staticmethod
    async def stop():
        await t2.gen_server_cast(__name__, 'special_cast_stop')

    @staticmethod
    async def fail():
        await t2.gen_server_cast(__name__, 'special_cast_fail')


class special_info:
    async def matched(val):
        await t2.mailbox_send(__name__, ('special_info_matched', val))

    async def no_match(val):
        await t2.mailbox_send(__name__, ('special_info_no_match', val))

    @staticmethod
    async def stop():
        await t2.mailbox_send(__name__, 'special_info_stop')

    @staticmethod
    async def fail():
        await t2.mailbox_send(__name__, 'special_info_fail')


class KvStore(t2.Module):

    async def start(self, test_state):
        try:
            await t2.gen_server_start(self, test_state, name=__name__)

        except Exception as err:
            test_state.did_raise = err

        finally:
            test_state.stopped.set()

    async def init(self, test_state):
        test_state.ready.set()
        return test_state

    async def terminate(self, reason, test_state):
        test_state.terminated_with = reason

    async def handle_call(self, message, caller, test_state):
        match message:
            case ('api_get', key):
                val = test_state.data.get(key)
                return (t2.Reply(val), test_state)

            case ('api_set', key, val):
                prev = test_state.data.get(key)
                test_state.data[key] = val
                return (t2.Reply(prev), test_state)

            case ('special_call_delayed', nursery):
                async def slow_task():
                    await trio.sleep(0)
                    await t2.gen_server_reply(caller, 'done')

                nursery.start_soon(slow_task)
                return (t2.NoReply(), test_state)

            case 'special_call_timedout':
                return (t2.NoReply(), test_state)

            case 'special_call_stopped':
                return (t2.Stop(), test_state)

            case 'special_call_failure':
                exc = RuntimeError('pytest')
                return (t2.Stop(exc), test_state)

            case _:
                exc = NotImplementedError('wrong call')
                return (t2.Reply(exc), test_state)

    async def handle_cast(self, message, test_state):
        match message:
            case 'special_cast_normal':
                test_state.casted.set()
                return (t2.NoReply(), test_state)

            case 'special_cast_stop':
                return (t2.Stop(), test_state)

            case _:
                exc = NotImplementedError('wrong cast')
                return (t2.Stop(exc), test_state)

    async def handle_info(self, message, test_state):
        match message:
            case ('special_info_matched', val):
                test_state.info_val = val
                test_state.info.set()
                return (t2.NoReply(), test_state)

            case 'special_info_stop':
                return (t2.Stop(), test_state)

            case 'special_info_fail':
                exc = RuntimeError('pytest')
                return (t2.Stop(exc), test_state)

            case _:
                test_state.unknown_info.append(message)
                test_state.info.set()
                return (t2.NoReply(), test_state)
