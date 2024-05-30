import aiohttp.web as aw

from ..server import HelloHandler


async def test_hello(aiohttp_client, loop):
    app = aw.Application()
    app.router.add_get('/', HelloHandler())
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello, World!' in text
