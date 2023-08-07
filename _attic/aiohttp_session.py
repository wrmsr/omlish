"""
Copyright 2015-2020 aio-libs collaboration.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at

   https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.
"""
import abc
import base64
import json
import logging
import time
import typing as ta

import aiohttp.typedefs
import aiohttp.web
import cryptography.fernet


log = logging.getLogger(__package__)

Middleware: ta.TypeAlias = ta.Callable[
    [aiohttp.web.Request, aiohttp.typedefs.Handler],
    ta.Awaitable[aiohttp.web.StreamResponse]
]


class _CookieParams(ta.TypedDict, total=False):
    domain: ta.Optional[str]
    max_age: ta.Optional[int]
    path: str
    secure: ta.Optional[bool]
    httponly: bool
    samesite: ta.Optional[str]
    expires: str


class SessionData(ta.TypedDict, total=False):
    created: int
    session: ta.Dict[str, ta.Any]


class Session(ta.MutableMapping[str, ta.Any]):
    """Session dict-like object."""

    def __init__(
        self,
        identity: ta.Optional[ta.Any],
        *,
        data: ta.Optional[SessionData],
        new: bool,
        max_age: ta.Optional[int] = None,
    ) -> None:
        self._changed: bool = False
        self._mapping: ta.Dict[str, ta.Any] = {}
        self._identity = identity if data != {} else None
        self._new = new if data != {} else True
        self._max_age = max_age
        created = data.get("created", None) if data else None
        session_data = data.get("session", None) if data else None
        now = int(time.time())
        age = now - created if created else now
        if max_age is not None and age > max_age:
            session_data = None
        if self._new or created is None:
            self._created = now
        else:
            self._created = created

        if session_data is not None:
            self._mapping.update(session_data)

    def __repr__(self) -> str:
        return "<{} [new:{}, changed:{}, created:{}] {!r}>".format(
            self.__class__.__name__,
            self.new,
            self._changed,
            self.created,
            self._mapping,
        )

    @property
    def new(self) -> bool:
        return self._new

    @property
    def identity(self) -> ta.Optional[ta.Any]:  # type: ignore[misc]
        return self._identity

    @property
    def created(self) -> int:
        return self._created

    @property
    def empty(self) -> bool:
        return not bool(self._mapping)

    @property
    def max_age(self) -> ta.Optional[int]:
        return self._max_age

    @max_age.setter
    def max_age(self, value: ta.Optional[int]) -> None:
        self._max_age = value

    def changed(self) -> None:
        self._changed = True

    def invalidate(self) -> None:
        self._changed = True
        self._mapping = {}

    def set_new_identity(self, identity: ta.Optional[ta.Any]) -> None:
        if not self._new:
            raise RuntimeError("Can't change identity for a session which is not new")

        self._identity = identity

    def __len__(self) -> int:
        return len(self._mapping)

    def __iter__(self) -> ta.Iterator[str]:
        return iter(self._mapping)

    def __contains__(self, key: object) -> bool:
        return key in self._mapping

    def __getitem__(self, key: str) -> ta.Any:
        return self._mapping[key]

    def __setitem__(self, key: str, value: ta.Any) -> None:
        self._mapping[key] = value
        self._changed = True
        self._created = int(time.time())

    def __delitem__(self, key: str) -> None:
        del self._mapping[key]
        self._changed = True
        self._created = int(time.time())


SESSION_KEY = "aiohttp_session"
STORAGE_KEY = "aiohttp_session_storage"


async def get_session(request: aiohttp.web.Request) -> Session:
    session = request.get(SESSION_KEY)
    if session is None:
        storage = request.get(STORAGE_KEY)
        if storage is None:
            raise RuntimeError(
                "Install aiohttp_session middleware " "in your aiohttp.web.Application"
            )

        session = await storage.load_session(request)
        if not isinstance(session, Session):
            raise RuntimeError(
                "Installed {!r} storage should return session instance "
                "on .load_session() call, got {!r}.".format(storage, session)
            )
        request[SESSION_KEY] = session
    return session


async def new_session(request: aiohttp.web.Request) -> Session:
    storage = request.get(STORAGE_KEY)
    if storage is None:
        raise RuntimeError(
            "Install aiohttp_session middleware " "in your aiohttp.web.Application"
        )

    session = await storage.new_session()
    if not isinstance(session, Session):
        raise RuntimeError(
            "Installed {!r} storage should return session instance "
            "on .load_session() call, got {!r}.".format(storage, session)
        )
    request[SESSION_KEY] = session
    return session


def session_middleware(storage: "AbstractStorage") -> Middleware:
    if not isinstance(storage, AbstractStorage):
        raise RuntimeError(f"Expected AbstractStorage got {storage}")

    @aiohttp.web.middleware
    async def factory(request: aiohttp.web.Request, handler: aiohttp.typedefs.Handler) -> aiohttp.web.StreamResponse:
        request[STORAGE_KEY] = storage
        raise_response = False
        # TODO aiohttp 4:
        # Remove Union from response, and drop the raise_response variable
        response: ta.Union[aiohttp.web.StreamResponse, aiohttp.web.HTTPException]
        try:
            response = await handler(request)
        except aiohttp.web.HTTPException as exc:
            response = exc
            raise_response = True
        if not isinstance(response, (aiohttp.web.StreamResponse, aiohttp.web.HTTPException)):
            raise RuntimeError(f"Expect response, not {type(response)!r}")
        if not isinstance(response, (aiohttp.web.Response, aiohttp.web.HTTPException)):
            # likely got websocket or streaming
            return response
        if response.prepared:
            raise RuntimeError("Cannot save session data into prepared response")
        session = request.get(SESSION_KEY)
        if session is not None:
            if session._changed:
                await storage.save_session(request, response, session)
        if raise_response:
            raise ta.cast(aiohttp.web.HTTPException, response)
        return response

    return factory


def setup(app: aiohttp.web.Application, storage: "AbstractStorage") -> None:
    """Setup the library in aiohttp fashion."""

    app.middlewares.append(session_middleware(storage))


class AbstractStorage(metaclass=abc.ABCMeta):
    def __init__(
        self,
        *,
        cookie_name: str = "AIOHTTP_SESSION",
        domain: ta.Optional[str] = None,
        max_age: ta.Optional[int] = None,
        path: str = "/",
        secure: ta.Optional[bool] = None,
        httponly: bool = True,
        samesite: ta.Optional[str] = None,
        encoder: ta.Callable[[object], str] = json.dumps,
        decoder: ta.Callable[[str], ta.Any] = json.loads,
    ) -> None:
        self._cookie_name = cookie_name
        self._cookie_params = _CookieParams(
            domain=domain,
            max_age=max_age,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )
        self._max_age = max_age
        self._encoder = encoder
        self._decoder = decoder

    @property
    def cookie_name(self) -> str:
        return self._cookie_name

    @property
    def max_age(self) -> ta.Optional[int]:
        return self._max_age

    @property
    def cookie_params(self) -> _CookieParams:
        return self._cookie_params

    def _get_session_data(self, session: Session) -> SessionData:
        if session.empty:
            return {}

        return {"created": session.created, "session": session._mapping}

    async def new_session(self) -> Session:
        return Session(None, data=None, new=True, max_age=self.max_age)

    @abc.abstractmethod
    async def load_session(self, request: aiohttp.web.Request) -> Session:
        pass

    @abc.abstractmethod
    async def save_session(
        self, request: aiohttp.web.Request, response: aiohttp.web.StreamResponse, session: Session
    ) -> None:
        pass

    def load_cookie(self, request: aiohttp.web.Request) -> ta.Optional[str]:
        return request.cookies.get(self._cookie_name)

    def save_cookie(
        self,
        response: aiohttp.web.StreamResponse,
        cookie_data: str,
        *,
        max_age: ta.Optional[int] = None,
    ) -> None:
        params = self._cookie_params.copy()
        if max_age is not None:
            params["max_age"] = max_age
            t = time.gmtime(time.time() + max_age)
            params["expires"] = time.strftime("%a, %d-%b-%Y %T GMT", t)
        if not cookie_data:
            response.del_cookie(
                self._cookie_name, domain=params["domain"], path=params["path"]
            )
        else:
            response.set_cookie(self._cookie_name, cookie_data, **params)


class SimpleCookieStorage(AbstractStorage):
    """Simple JSON storage.

    Doesn't any encryption/validation, use it for tests only"""

    def __init__(
        self,
        *,
        cookie_name: str = "AIOHTTP_SESSION",
        domain: ta.Optional[str] = None,
        max_age: ta.Optional[int] = None,
        path: str = "/",
        secure: ta.Optional[bool] = None,
        httponly: bool = True,
        samesite: ta.Optional[str] = None,
        encoder: ta.Callable[[object], str] = json.dumps,
        decoder: ta.Callable[[str], ta.Any] = json.loads,
    ) -> None:
        super().__init__(
            cookie_name=cookie_name,
            domain=domain,
            max_age=max_age,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
            encoder=encoder,
            decoder=decoder,
        )

    async def load_session(self, request: aiohttp.web.Request) -> Session:
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data=None, new=True, max_age=self.max_age)

        data = self._decoder(cookie)
        return Session(None, data=data, new=False, max_age=self.max_age)

    async def save_session(
        self, request: aiohttp.web.Request, response: aiohttp.web.StreamResponse, session: Session
    ) -> None:
        cookie_data = self._encoder(self._get_session_data(session))
        self.save_cookie(response, cookie_data, max_age=session.max_age)


class EncryptedCookieStorage(AbstractStorage):
    """Encrypted JSON storage."""

    def __init__(
        self,
        secret_key: ta.Union[str, bytes, bytearray, cryptography.fernet.Fernet],
        *,
        cookie_name: str = "AIOHTTP_SESSION",
        domain: ta.Optional[str] = None,
        max_age: ta.Optional[int] = None,
        path: str = "/",
        secure: ta.Optional[bool] = None,
        httponly: bool = True,
        samesite: ta.Optional[str] = None,
        encoder: ta.Callable[[object], str] = json.dumps,
        decoder: ta.Callable[[str], ta.Any] = json.loads
    ) -> None:
        super().__init__(
            cookie_name=cookie_name,
            domain=domain,
            max_age=max_age,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
            encoder=encoder,
            decoder=decoder,
        )

        if isinstance(secret_key, cryptography.fernet.Fernet):
            self._fernet = secret_key
        else:
            if isinstance(secret_key, (bytes, bytearray)):
                secret_key = base64.urlsafe_b64encode(secret_key)
            self._fernet = cryptography.fernet.Fernet(secret_key)

    async def load_session(self, request: aiohttp.web.Request) -> Session:
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data=None, new=True, max_age=self.max_age)
        else:
            try:
                data = self._decoder(
                    self._fernet.decrypt(
                        cookie.encode("utf-8"), ttl=self.max_age
                    ).decode("utf-8")
                )
                return Session(None, data=data, new=False, max_age=self.max_age)
            except cryptography.fernet.InvalidToken:
                log.warning(
                    "Cannot decrypt cookie value, " "create a new fresh session"
                )
                return Session(None, data=None, new=True, max_age=self.max_age)

    async def save_session(
        self, request: aiohttp.web.Request, response: aiohttp.web.StreamResponse, session: Session
    ) -> None:
        if session.empty:
            return self.save_cookie(response, "", max_age=session.max_age)

        cookie_data = self._encoder(self._get_session_data(session)).encode("utf-8")
        self.save_cookie(
            response,
            self._fernet.encrypt(cookie_data).decode("utf-8"),
            max_age=session.max_age,
        )
