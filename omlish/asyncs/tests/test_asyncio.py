import asyncio


def test_asyncio():
    def hello_world(loop):
        print('Hello World')
        loop.stop()

    loop = asyncio.new_event_loop()

    # Schedule a call to hello_world()
    loop.call_soon(hello_world, loop)

    # Blocking call interrupted by loop.stop()
    try:
        loop.run_forever()
    finally:
        loop.close()
