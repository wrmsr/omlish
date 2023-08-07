"""
Copyright (c) 2018-2020 Kuchuk Oleh <kuchuklehjs@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import asyncio
import collections
import functools
import logging
import re

from aiohttp import hdrs
from aiohttp import web
import jwt


logger = logging.getLogger(__name__)

_request_property = ...


def JWTMiddleware(
    secret_or_pub_key,
    request_property='payload',
    credentials_required=True,
    whitelist=tuple(),
    token_getter=None,
    is_revoked=None,
    store_token=False,
    algorithms=None,
    auth_scheme='Bearer',
    audience=None,
    issuer=None
):
    if not (secret_or_pub_key and isinstance(secret_or_pub_key, str)):
        raise RuntimeError('secret or public key should be provided for correct work')

    if not isinstance(request_property, str):
        raise TypeError('request_property should be a str')

    global _request_property

    _request_property = request_property

    @web.middleware
    async def jwt_middleware(request, handler):
        if request.method == hdrs.METH_OPTIONS:
            return await handler(request)

        if check_request(request, whitelist):
            return await handler(request)

        token = None

        if callable(token_getter):
            token = await invoke(functools.partial(token_getter, request))
        elif 'Authorization' in request.headers:
            try:
                scheme, token = request.headers.get('Authorization').strip().split(' ')
            except ValueError:
                raise web.HTTPForbidden(reason='Invalid authorization header')

            if not re.match(auth_scheme, scheme):
                if credentials_required:
                    raise web.HTTPForbidden(reason='Invalid token scheme')
                return await handler(request)

        if not token and credentials_required:
            raise web.HTTPUnauthorized(reason='Missing authorization token')

        if token is not None:
            if not isinstance(token, bytes):
                token = token.encode()

            try:
                decoded = jwt.decode(
                    token,
                    secret_or_pub_key,
                    algorithms=algorithms,
                    audience=audience,
                    issuer=issuer
                )
            except jwt.InvalidTokenError as exc:
                logger.exception(exc, exc_info=exc)
                msg = 'Invalid authorization token, ' + str(exc)
                raise web.HTTPUnauthorized(reason=msg)

            if callable(is_revoked):
                if await invoke(functools.partial(
                    is_revoked,
                    request,
                    decoded,
                )):
                    raise web.HTTPForbidden(reason='Token is revoked')

            request[request_property] = decoded

            if store_token and isinstance(store_token, str):
                request[store_token] = token

        return await handler(request)

    return jwt_middleware


###


def match_any(required, provided):
    return any([scope in provided for scope in required])


def match_all(required, provided):
    return set(required).issubset(set(provided))


def login_required(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        if _request_property is ...:
            raise RuntimeError('Incorrect usage of decorator. Please initialize middleware first')
        request = args[-1]

        if isinstance(request, web.View):
            request = request.request

        if not isinstance(request, web.BaseRequest):  # pragma: no cover
            raise RuntimeError('Incorrect usage of decorator. Expect web.BaseRequest as an argument')

        if not request.get(_request_property):
            raise web.HTTPUnauthorized(reason='Authorization required')

        return await func(*args, **kwargs)
    return wrapped


def check_permissions(
    scopes,
    permissions_property='scopes',
    comparison=match_all,
):
    if not callable(comparison):
        raise TypeError('comparison should be a func')

    if isinstance(scopes, str):
        scopes = scopes.split(' ')

    def scopes_checker(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if _request_property is ...:
                raise RuntimeError('Incorrect usage of decorator. Please initialize middleware first')

            request = args[-1]

            if isinstance(request, web.View):
                request = request.request

            if not isinstance(request, web.BaseRequest):  # pragma: no cover
                raise RuntimeError('Incorrect usage of decorator. Expect web.BaseRequest as an argument')

            payload = request.get(_request_property)

            if not payload:
                raise web.HTTPUnauthorized(reason='Authorization required')

            user_scopes = payload.get(permissions_property, [])

            if not isinstance(user_scopes, collections.Iterable):
                raise web.HTTPForbidden(reason='Invalid permissions format')

            if not comparison(scopes, user_scopes):
                raise web.HTTPForbidden(reason='Insufficient scopes')

            return await func(*args, **kwargs)

        return wrapped

    return scopes_checker


###


def check_request(request, entries):
    for pattern in entries:
        if re.match(pattern, request.path):
            return True

    return False


async def invoke(func):
    result = func()
    if asyncio.iscoroutine(result):
        result = await result
    return result