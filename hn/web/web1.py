import datetime
import jwt
import json
import typing as ta

import aiohttp.web


def json_response(body: ta.Any = '', **kwargs: ta.Any) -> aiohttp.web.Response:
    kwargs['body'] = json.dumps(body or kwargs['body']).encode('utf-8')
    kwargs['content_type'] = 'text/json'
    return aiohttp.web.Response(**kwargs)


JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20


USERS = [
    {
        'id': 0,
        'name': 'barf',
        'password': 'fff',
    }
]


async def login(request):
    post_data = await request.post()

    for user in USERS:
        if user['name'] == post_data['username']:
            break
    else:
        return json_response({'message': 'Wrong credentials'}, status=400)

    if user['password'] != post_data['password']:
        return json_response({'message': 'Wrong credentials'}, status=400)

    payload = {
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }

    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return json_response({'token': jwt_token})


app = aiohttp.web.Application()
app.router.add_route('POST', '/login', login)
aiohttp.web.run_app(app)
