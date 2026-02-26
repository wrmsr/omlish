#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output ../ci/cli.py
# @omlish-git-diff-omit
# ruff: noqa: N802 PYI034 TC003 UP006 UP007 UP036 UP043 UP045 UP046
"""
Inputs:
 - requirements.txt
 - ci.Dockerfile
 - compose.yml

==

./python -m omdev.ci run --cache-dir omdev/ci/tests/cache omdev/ci/tests/project omlish-ci
"""
import abc
import argparse
import asyncio
import asyncio.base_subprocess
import asyncio.subprocess
import base64
import collections
import collections.abc
import concurrent.futures as cf
import contextlib
import contextvars
import copy
import dataclasses as dc
import datetime
import decimal
import email.utils
import enum
import errno
import fcntl
import fractions
import functools
import glob
import gzip
import hashlib
import heapq
import html
import http
import http.client
import http.server
import inspect
import io
import itertools
import json
import logging
import operator
import os
import os.path
import re
import selectors
import shlex
import shutil
import socket
import socket as socket_
import ssl
import stat
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import threading
import time
import traceback
import types
import typing as ta
import unicodedata
import urllib.parse
import urllib.request
import uuid
import weakref
import xml.etree.ElementTree as ET


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


def __omlish_amalg__():  # noqa
    return dict(
        src_files=[
            dict(path='consts.py', sha1='ef00d55ab4cdd799b22f2e8b736eacd52ee8a80e'),
            dict(path='github/env.py', sha1='c7a2389048f008f46f59f6bcc11e0d15655f2b1c'),
            dict(path='shell.py', sha1='a59e59b812394d0502837f4c198e1cf604f90227'),
            dict(path='../oci/compression.py', sha1='7d165bc51a77db13ff45927daecc42839cfd75ea'),
            dict(path='../../omlish/asyncs/asyncio/utils.py', sha1='34691d4d0e5bab68f14e193a6200df040cfd0136'),
            dict(path='../../omlish/docker/ports.py', sha1='a3202c69b85bc4f1034479df3400fddc86130e5c'),
            dict(path='../../omlish/http/urllib.py', sha1='25431c5bdc7dd5cbecfcb8c0bdffaabf8c1691b9'),
            dict(path='../../omlish/http/versions.py', sha1='5b1659b81eb197c6880fbe78684a1348595ec804'),
            dict(path='../../omlish/io/pushback.py', sha1='783fe8a40fa9f2febf035f4553c53c73b9bd58e1'),
            dict(path='../../omlish/lite/abstract.py', sha1='a2fc3f3697fa8de5247761e9d554e70176f37aac'),
            dict(path='../../omlish/lite/asyncs.py', sha1='b3f2251c56617ce548abf9c333ac996b63edb23e'),
            dict(path='../../omlish/lite/cached.py', sha1='0c33cf961ac8f0727284303c7a30c5ea98f714f2'),
            dict(path='../../omlish/lite/check.py', sha1='d30cfee7f46d37c55e98fdb7c60327c521f8295e'),
            dict(path='../../omlish/lite/contextmanagers.py', sha1='993f5ed96d3410f739a20363f55670d5e5267fa3'),
            dict(path='../../omlish/lite/dataclasses.py', sha1='8b144d1d9474d96cf2a35f4db5cb224c30f538d6'),
            dict(path='../../omlish/lite/json.py', sha1='57eeddc4d23a17931e00284ffa5cb6e3ce089486'),
            dict(path='../../omlish/lite/objects.py', sha1='9566bbf3530fd71fcc56321485216b592fae21e9'),
            dict(path='../../omlish/lite/reflect.py', sha1='c4fec44bf144e9d93293c996af06f6c65fc5e63d'),
            dict(path='../../omlish/lite/strings.py', sha1='89831ecbc34ad80e118a865eceb390ed399dc4d6'),
            dict(path='../../omlish/lite/typing.py', sha1='9d6caabc7b31534109e3f2e249d21f8610c9c079'),
            dict(path='../../omlish/logs/levels.py', sha1='91405563d082a5eba874da82aac89d83ce7b6152'),
            dict(path='../../omlish/logs/std/filters.py', sha1='f36aab646d84d31e295b33aaaaa6f8b67ff38b3d'),
            dict(path='../../omlish/logs/std/proxy.py', sha1='3e7301a2aa351127f9c85f61b2f85dcc3f15aafb'),
            dict(path='../../omlish/logs/warnings.py', sha1='c4eb694b24773351107fcc058f3620f1dbfb6799'),
            dict(path='../../omlish/os/files.py', sha1='32f4fe2e7d32a6b368619081bd300e6f150e312b'),
            dict(path='../../omlish/os/paths.py', sha1='56c40b7c2aa84d1778d60ee4cda498f8c380cc8d'),
            dict(path='../../omlish/secrets/ssl.py', sha1='68af8abad22d64afa1736a8363036aa2121ada78'),
            dict(path='../../omlish/sockets/addresses.py', sha1='26533e88a8073f89646c0f77f1fbe0869282ab0e'),
            dict(path='../../omlish/sockets/io.py', sha1='b6b8a73ac0f29893c7128f9d4f62240efbd917bb'),
            dict(path='github/api/v1/api.py', sha1='1985c16447f5d245b659936571d361285374c5d9'),
            dict(path='github/api/v2/api.py', sha1='08322895cd895db1cbffceb1e5bfc7b10cac50cc'),
            dict(path='github/bootstrap.py', sha1='9bf24b05603cd1a82db8be8b645bbad3e0d3f22f'),
            dict(path='../oci/datarefs.py', sha1='793ce5f2774e052b28d04b226a5f1eff6eec0a72'),
            dict(path='../oci/pack/unpacking.py', sha1='f43dee9a2eee79cbbb90f0721ed234a2bc35daa7'),
            dict(path='../../omlish/argparse/cli.py', sha1='f4dc3cd353d14386b5da0306768700e396afd2b3'),
            dict(path='../../omlish/formats/yaml/goyaml/errors.py', sha1='8fa73c90292f56f8faaedebb2f478ff6a3b95460'),
            dict(path='../../omlish/http/coro/io.py', sha1='6ccbbf6a1a6a702ce0f1dc24b4057e8264ef4641'),
            dict(path='../../omlish/http/parsing.py', sha1='2ee187993274e697332c7df7b46a98382f4cee2a'),
            dict(path='../../omlish/lite/marshal.py', sha1='96348f5f2a26dc27d842d33cc3927e9da163436b'),
            dict(path='../../omlish/lite/maybes.py', sha1='04d2fcbea17028a5e6b8e7a7fb742375495ed233'),
            dict(path='../../omlish/lite/runtime.py', sha1='2e752a27ae2bf89b1bb79b4a2da522a3ec360c70'),
            dict(path='../../omlish/lite/timeouts.py', sha1='2f19c808e582877f999d7ea7dde0acd6382266a2'),
            dict(path='../../omlish/logs/infos.py', sha1='4dd104bd468a8c438601dd0bbda619b47d2f1620'),
            dict(path='../../omlish/logs/metrics/base.py', sha1='95120732c745ceec5333f81553761ab6ff4bb3fb'),
            dict(path='../../omlish/logs/protocols.py', sha1='05ca4d1d7feb50c4e3b9f22ee371aa7bf4b3dbd1'),
            dict(path='../../omlish/logs/std/json.py', sha1='2a75553131e4d5331bb0cedde42aa183f403fc3b'),
            dict(path='../../omlish/os/temp.py', sha1='fba3470ac095a6c3f893156cc4437bda1b8796cb'),
            dict(path='../../omlish/sockets/bind.py', sha1='d0040d74960fb00c30ae9ece5252c270b59ae3f4'),
            dict(path='../../omlish/sockets/handlers.py', sha1='733a4855d563001ad09df511531d710aa2632770'),
            dict(path='../../omlish/text/mangle.py', sha1='5631de37ca659e064eb1afcf2213d317b626f8bd'),
            dict(path='../dataserver/targets.py', sha1='661fc3e60ad436646c8acff3c547d5b86ceb0bd6'),
            dict(path='../oci/data.py', sha1='9cfc3bb8e23fb4cd746c6e8f0e02624e8f63f234'),
            dict(path='../oci/repositories.py', sha1='bd0ac0fb906f679a660c87124da268370733fcc6'),
            dict(path='../oci/tars.py', sha1='3ed00e97a494bd92c6a6149d22d51469bc0af384'),
            dict(path='../../omlish/asyncs/asyncio/sockets.py', sha1='8d24dae988a30bb73f167a9ab62d4fc9eef4ad06'),
            dict(path='../../omlish/asyncs/asyncio/timeouts.py', sha1='4d31b02b3c39b8f2fa7e94db36552fde6942e36a'),
            dict(path='../../omlish/formats/yaml/goyaml/tokens.py', sha1='d52876a2a525bc99eb554fe28c3d27e7e01f43a9'),
            dict(path='../../omlish/http/handlers.py', sha1='2b97d76b8e2e507b5c5b6a241d077c00960ee638'),
            dict(path='../../omlish/lite/inject.py', sha1='6f097e3170019a34ff6834d36fcc9cbeed3a7ab4'),
            dict(path='../../omlish/logs/contexts.py', sha1='1000a6d5ddfb642865ca532e34b1d50759781cf0'),
            dict(path='../../omlish/logs/std/standard.py', sha1='5c97c1b9f7ead58d6127d047b873398f708f288d'),
            dict(path='../../omlish/logs/utils.py', sha1='9b879044cbdc3172fd7282c7f2a4880b81261cdd'),
            dict(path='../../omlish/sockets/server/handlers.py', sha1='6f9adca9fa04774a28a488a4e2a11bb4492c71d0'),
            dict(path='../../omlish/subprocesses/run.py', sha1='8200e48f0c49d164df3503cd0143038d0c4d30aa'),
            dict(path='../../omlish/subprocesses/wrap.py', sha1='8a9b7d2255481fae15c05f5624b0cdc0766f4b3f'),
            dict(path='../dataserver/handlers.py', sha1='f624715f2500087226ec3374315cc8a1ea47a29b'),
            dict(path='../dataserver/routes.py', sha1='0186bb2e84ff4d5c05af2a57c61f6fd605eba790'),
            dict(path='../oci/media.py', sha1='a20324c5b0661c9a9a7679406d019ab3ba4acd98'),
            dict(path='../oci/pack/packing.py', sha1='7585c3dea6b8a62b6ca63fe78968497db915ea57'),
            dict(path='../../omlish/formats/yaml/goyaml/ast.py', sha1='811593bad2d89bfecc4a688a8d5e92e66c026073'),
            dict(path='../../omlish/formats/yaml/goyaml/scanning.py', sha1='fe21556a59a30e12a110e85ef2b201a5d81f14d0'),
            dict(path='../../omlish/http/coro/server/server.py', sha1='7c98ff3073835079b4170c1235332f1c620cbf52'),
            dict(path='../../omlish/logs/base.py', sha1='eaa2ce213235815e2f86c50df6c41cfe26a43ba2'),
            dict(path='../../omlish/logs/std/records.py', sha1='67e552537d9268d4df6939b8a92be885fda35238'),
            dict(path='../../omlish/secrets/tempssl.py', sha1='360d4cd98483357bcf013e156dafd92fd37ed220'),
            dict(path='../../omlish/sockets/server/server.py', sha1='89204da9ea77577418ff7d2910aea0d593c765f3'),
            dict(path='../../omlish/sockets/server/ssl.py', sha1='790dfd208f4d267c826d491d4eb5deeda5ebdddc'),
            dict(path='../../omlish/sockets/server/threading.py', sha1='ad4ef21b7e3fe3a774d14040191d1e16fa0d1de7'),
            dict(path='../../omlish/subprocesses/base.py', sha1='cb9f668be5422fecb27222caabb67daac6c1bab9'),
            dict(path='docker/cacheserved/manifests.py', sha1='80a65d08319d152f0bc6f893351e23368b3de93b'),
            dict(path='../dataserver/server.py', sha1='e1ba8ca6f85458a64ede4ca07836aa103246132a'),
            dict(path='../oci/building.py', sha1='b4fea06c03ba02d3ecfc6d10d955dc76f263846a'),
            dict(path='../oci/loading.py', sha1='64d806ffad8d24087ccc29f759f672e6d795bee2'),
            dict(path='../../omlish/formats/yaml/goyaml/parsing.py', sha1='a7faf2bf497eec7087b2ee803b088af08d4b6cd0'),
            dict(path='../../omlish/http/coro/server/sockets.py', sha1='512e6fdd4ad9a533b81a584e45c7d7e9b0188c15'),
            dict(path='../../omlish/logs/asyncs.py', sha1='8376df395029a9d0957e2338adede895a9364215'),
            dict(path='../../omlish/logs/std/loggers.py', sha1='dbdfc66188e6accb75d03454e43221d3fba0f011'),
            dict(path='../../omlish/subprocesses/asyncs.py', sha1='bba44d524c24c6ac73168aee6343488414e5bf48'),
            dict(path='../../omlish/subprocesses/sync.py', sha1='8434919eba4da67825773d56918fdc0cb2f1883b'),
            dict(path='../dataserver/http.py', sha1='f85ca91015bac434281326ef7885babd9d6d834c'),
            dict(path='../oci/dataserver.py', sha1='dd147b56282b054cef264556a0ff3b3d1719bcee'),
            dict(path='../../omlish/asyncs/asyncio/subprocesses.py', sha1='b6b5f9ae3fd0b9c83593bad2e04a08f726e5904d'),
            dict(path='../../omlish/formats/yaml/goyaml/decoding.py', sha1='03e29317ab0a76549db8e6938dfe83596dfe48df'),
            dict(path='../../omlish/http/coro/server/simple.py', sha1='27bb1e958ef2e53adf98d4e01cc5868e8b4af72c'),
            dict(path='../../omlish/logs/modules.py', sha1='dd7d5f8e63fe8829dfb49460f3929ab64b68ee14'),
            dict(path='cache.py', sha1='9353e5c3b73bed47258680fd15ac49417113f0ca'),
            dict(path='docker/cmds.py', sha1='5528c384f68f9003732bfaf6be302e84747909dd'),
            dict(path='docker/dataserver.py', sha1='949e561ab756846425a39c05964c0fb256ae61db'),
            dict(path='utils.py', sha1='b7b7b439b1077771f2bd7c7c74ed422ea2663014'),
            dict(path='../../omlish/lite/timing.py', sha1='af5022f5a508939f1b433ed0514ede340fd0d672'),
            dict(path='compose.py', sha1='d2bec1385701979c7ff9913456b72d8c7b31f70b'),
            dict(path='docker/cache.py', sha1='07a9e3d00bdd60f1a0a9b55aca12430fa1b4e3d9'),
            dict(path='docker/repositories.py', sha1='e4bfc0e91c3bf20259895ce7c95a1eb3f6507518'),
            dict(path='docker/utils.py', sha1='082e2b962ca1bc8e6b3f9bbe6ecfcadff310d54f'),
            dict(path='github/api/clients.py', sha1='8ddc0f5ccf718f1b530f4a965f0cc56b68a6a2a8'),
            dict(path='github/api/v2/azure.py', sha1='19052e8e2babb8b2953ec10e6b9dcee97c21419a'),
            dict(path='requirements.py', sha1='c370a65958a00412e00608a0e1f12795e276aee1'),
            dict(path='../oci/pack/repositories.py', sha1='e9bf6fa8bdaae2031dd0967d07a56c93a2e099b6'),
            dict(path='docker/buildcaching.py', sha1='7b2633d5b8dac6aab01dd459e273cb370c5b11c8'),
            dict(path='docker/cacheserved/cache.py', sha1='69732c658dba7ccf260e784132ff0c60192e3c69'),
            dict(path='docker/imagepulling.py', sha1='d6b1ca1ecb9aa5c593a25e6deb78e942c75ebcb4'),
            dict(path='github/api/v1/client.py', sha1='6ddd600cd8a7ff72a6a3408ded14240bafab6944'),
            dict(path='github/api/v2/client.py', sha1='e28f27c07011487d5a3f4ae32fdfa1a857d02459'),
            dict(path='ci.py', sha1='87b82e2bd86aa886764f1e0067251b056e359650'),
            dict(path='docker/inject.py', sha1='69acac65fae413cb58c1f9aa739d2cc1c3ffa09d'),
            dict(path='github/cache.py', sha1='d91f9c87d167574e94c99817e6c3a0f75925dfb9'),
            dict(path='github/cli.py', sha1='6d14b0eb4ca5f606ad2821b63b9707ce57f50406'),
            dict(path='github/inject.py', sha1='99c0dd7c55767e7c49f70b7edac25da67f718b2e'),
            dict(path='inject.py', sha1='e86b16d79a113a4f387e68ed0db1d067bcada93a'),
            dict(path='cli.py', sha1='92948cf3ec76fd9ceb25762aadbf497354adce6d'),
        ],
    )


########################################


# shell.py
T = ta.TypeVar('T')

# ../../omlish/asyncs/asyncio/utils.py
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

# ../../omlish/lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)
CheckMessage = ta.Union[str, ta.Callable[..., ta.Optional[str]], None]  # ta.TypeAlias
CheckLateConfigureFn = ta.Callable[['Checks'], None]  # ta.TypeAlias
CheckOnRaiseFn = ta.Callable[[Exception], None]  # ta.TypeAlias
CheckExceptionFactory = ta.Callable[..., Exception]  # ta.TypeAlias
CheckArgsRenderer = ta.Callable[..., ta.Optional[str]]  # ta.TypeAlias

# ../../omlish/lite/contextmanagers.py
ExitStackedT = ta.TypeVar('ExitStackedT', bound='ExitStacked')
AsyncExitStackedT = ta.TypeVar('AsyncExitStackedT', bound='AsyncExitStacked')

# ../../omlish/lite/typing.py
A0 = ta.TypeVar('A0')
A1 = ta.TypeVar('A1')
A2 = ta.TypeVar('A2')

# ../../omlish/logs/levels.py
LogLevel = int  # ta.TypeAlias

# ../../omlish/sockets/addresses.py
SocketAddress = ta.Any  # ta.TypeAlias

# github/api/v2/api.py
GithubCacheServiceV2RequestT = ta.TypeVar('GithubCacheServiceV2RequestT')
GithubCacheServiceV2ResponseT = ta.TypeVar('GithubCacheServiceV2ResponseT')

# ../../omlish/argparse/cli.py
ArgparseCmdFn = ta.Callable[[], ta.Optional[int]]  # ta.TypeAlias

# ../../omlish/formats/yaml/goyaml/errors.py
YamlErrorOr = ta.Union['YamlError', T]  # ta.TypeAlias

# ../../omlish/lite/maybes.py
U = ta.TypeVar('U')

# ../../omlish/lite/timeouts.py
TimeoutLike = ta.Union['Timeout', ta.Type['Timeout.DEFAULT'], ta.Iterable['TimeoutLike'], 'CanFloat', float, int, bool, None]  # ta.TypeAlias  # noqa

# ../../omlish/logs/infos.py
LoggingMsgFn = ta.Callable[[], ta.Union[str, tuple]]  # ta.TypeAlias
LoggingExcInfoTuple = ta.Tuple[ta.Type[BaseException], BaseException, ta.Optional[types.TracebackType]]  # ta.TypeAlias
LoggingExcInfo = ta.Union[BaseException, LoggingExcInfoTuple]  # ta.TypeAlias
LoggingExcInfoArg = ta.Union[LoggingExcInfo, bool, None]  # ta.TypeAlias
LoggingContextInfo = ta.Any  # ta.TypeAlias

# ../../omlish/sockets/bind.py
SocketBinderT = ta.TypeVar('SocketBinderT', bound='SocketBinder')
SocketBinderConfigT = ta.TypeVar('SocketBinderConfigT', bound='SocketBinder.Config')
CanSocketBinderConfig = ta.Union['SocketBinder.Config', int, ta.Tuple[str, int], str]  # ta.TypeAlias
CanSocketBinder = ta.Union['SocketBinder', CanSocketBinderConfig]  # ta.TypeAlias

# ../../omlish/sockets/handlers.py
SocketHandler = ta.Callable[[SocketAddress, 'SocketIoPair'], None]  # ta.TypeAlias

# ../../omlish/asyncs/asyncio/timeouts.py
AwaitableT = ta.TypeVar('AwaitableT', bound=ta.Awaitable)

# ../../omlish/http/handlers.py
HttpHandler = ta.Callable[['HttpHandlerRequest'], 'HttpHandlerResponse']  # ta.TypeAlias
HttpHandlerResponseData = ta.Union[bytes, 'HttpHandlerResponseStreamedData']  # ta.TypeAlias  # noqa

# ../../omlish/lite/inject.py
InjectorKeyCls = ta.Union[type, ta.NewType]  # ta.TypeAlias
InjectorProviderFn = ta.Callable[['Injector'], ta.Any]  # ta.TypeAlias
InjectorProviderFnMap = ta.Mapping['InjectorKey', 'InjectorProviderFn']  # ta.TypeAlias
InjectorBindingOrBindings = ta.Union['InjectorBinding', 'InjectorBindings']  # ta.TypeAlias

# ../../omlish/logs/contexts.py
LoggingContextInfoT = ta.TypeVar('LoggingContextInfoT', bound=LoggingContextInfo)

# ../../omlish/sockets/server/handlers.py
SocketServerHandler = ta.Callable[['SocketAndAddress'], None]  # ta.TypeAlias

# ../dataserver/handlers.py
DataServerTargetT = ta.TypeVar('DataServerTargetT', bound='DataServerTarget')

# ../../omlish/http/coro/server/server.py
CoroHttpServerFactory = ta.Callable[[SocketAddress], 'CoroHttpServer']  # ta.TypeAlias

# ../../omlish/subprocesses/base.py
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']  # ta.TypeAlias

# ../oci/building.py
OciMediaDataclassT = ta.TypeVar('OciMediaDataclassT', bound='OciMediaDataclass')


########################################
# ../consts.py


CI_CACHE_VERSION = 2


########################################
# ../github/env.py


##


@dc.dataclass(frozen=True)
class GithubEnvVar:
    k: str

    def __call__(self) -> ta.Optional[str]:
        return os.environ.get(self.k)


GITHUB_ENV_VARS: ta.Set[GithubEnvVar] = set()


def register_github_env_var(k: str) -> GithubEnvVar:
    ev = GithubEnvVar(k)
    GITHUB_ENV_VARS.add(ev)
    return ev


########################################
# ../shell.py


##


@dc.dataclass(frozen=True)
class ShellCmd:
    s: str

    env: ta.Optional[ta.Mapping[str, str]] = None

    def build_run_kwargs(
            self,
            *,
            env: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> ta.Dict[str, ta.Any]:
        if env is None:
            env = os.environ
        if self.env:
            if (ek := set(env) & set(self.env)):
                raise KeyError(*ek)
            env = {**env, **self.env}

        return dict(
            env=env,
            **kwargs,
        )

    def run(self, fn: ta.Callable[..., T], **kwargs) -> T:
        return fn(
            'sh', '-c', self.s,
            **self.build_run_kwargs(**kwargs),
        )


########################################
# ../../oci/compression.py


##


class OciCompression(enum.Enum):
    GZIP = enum.auto()
    ZSTD = enum.auto()


########################################
# ../../../omlish/asyncs/asyncio/utils.py
"""
TODO:
 - split module
"""


##


def asyncio_ensure_task(obj: ta.Awaitable) -> asyncio.Task:
    if isinstance(obj, asyncio.Task):
        return obj
    elif isinstance(obj, ta.Coroutine):
        return asyncio.create_task(obj)
    else:
        raise TypeError(obj)


##


def asyncio_once(fn: CallableT) -> CallableT:
    task = None

    @functools.wraps(fn)
    async def inner(*args, **kwargs):
        nonlocal task
        if not task:
            task = asyncio.create_task(fn(*args, **kwargs))
        return await task

    return ta.cast(CallableT, inner)


##


def drain_asyncio_tasks(loop=None):
    if loop is None:
        loop = asyncio.get_running_loop()

    while loop._ready or loop._scheduled:  # noqa
        loop._run_once()  # noqa


@contextlib.contextmanager
def draining_asyncio_tasks() -> ta.Iterator[None]:
    loop = asyncio.get_running_loop()
    try:
        yield
    finally:
        if loop is not None:
            drain_asyncio_tasks(loop)  # noqa


##


async def asyncio_wait_concurrent(
        awaitables: ta.Iterable[ta.Awaitable[T]],
        concurrency: ta.Union[int, asyncio.Semaphore],
        *,
        return_when: ta.Any = asyncio.FIRST_EXCEPTION,
) -> ta.List[T]:
    if isinstance(concurrency, asyncio.Semaphore):
        semaphore = concurrency
    elif isinstance(concurrency, int):
        if concurrency < 1:
            raise ValueError(f'Concurrency must be >= 1, got {concurrency}')
        semaphore = asyncio.Semaphore(concurrency)
    else:
        raise TypeError(concurrency)

    async def limited_task(a):
        async with semaphore:
            return await a

    futs = [asyncio.create_task(limited_task(a)) for a in awaitables]
    done, pending = await asyncio.wait(futs, return_when=return_when)

    for fut in pending:
        fut.cancel()

    for fut in done:
        if fut.exception():
            raise fut.exception()  # type: ignore

    return [fut.result() for fut in done]


async def asyncio_wait_maybe_concurrent(
        awaitables: ta.Iterable[ta.Awaitable[T]],
        concurrency: ta.Union[int, asyncio.Semaphore, None],
) -> ta.List[T]:
    # Note: Only supports return_when=asyncio.FIRST_EXCEPTION
    if concurrency is None:
        return [await a for a in awaitables]

    else:
        return await asyncio_wait_concurrent(awaitables, concurrency)


########################################
# ../../../omlish/docker/ports.py
"""
TODO:
 - docstring
 - timebomb
 - auto-discover available ports
"""


##


@dc.dataclass(frozen=True)
class DockerPortRelay:
    """
    Uses roughly the following command to forward connections from inside docker-for-mac's vm to the mac host:

      docker run --rm -i -p 5001:5000 alpine/socat -d -d TCP-LISTEN:5000,fork,reuseaddr TCP:host.docker.internal:5021

    This allows requests made by the docker daemon running inside the vm to `host.docker.internal:5001` to be forwarded
    to the mac host on port 5021. The reason for this is to be able to use a docker registry running locally directly on
    the host mac - specifically to be able to do so with ssl certificate checking disabled (which docker will only do on
    localhost, which on a mac in the vm isn't actually the mac host - hence the necessity of the relay).
    """

    docker_port: int  # port
    host_port: int

    name: ta.Optional[str] = None

    DEFAULT_HOST_NAME: ta.ClassVar[str] = 'host.docker.internal'
    host_name: str = DEFAULT_HOST_NAME

    DEFAULT_INTERMEDIATE_PORT: ta.ClassVar[int] = 5000
    intermediate_port: int = DEFAULT_INTERMEDIATE_PORT

    DEFAULT_IMAGE: ta.ClassVar[str] = 'alpine/socat'
    image: str = DEFAULT_IMAGE

    def socat_args(self) -> ta.List[str]:
        return [
            '-d',
            f'TCP-LISTEN:{self.intermediate_port},fork,reuseaddr',
            f'TCP:{self.host_name}:{self.host_port}',
        ]

    def run_args(self) -> ta.List[str]:
        if (name := self.name) is None:
            name = f'docker_port_relay-{os.getpid()}-{self.docker_port}-{self.intermediate_port}-{self.host_port}'

        return [
            '--name', name,
            '--rm',
            '-p', f'{self.docker_port}:{self.intermediate_port}',
            self.image,
            *self.socat_args(),
        ]

    def run_cmd(self) -> ta.List[str]:
        return [
            'docker',
            'run',
            '-i',
            *self.run_args(),
        ]


########################################
# ../../../omlish/http/urllib.py


##


class NonRaisingUrllibErrorProcessor(urllib.request.HTTPErrorProcessor):
    """
    https://stackoverflow.com/a/74844056

    Usage:

        opener = urllib.request.build_opener(NonRaisingUrllibErrorProcessor)
        with opener.open(req) as resp:
            ...
    """

    def http_response(self, request, response):
        return response

    def https_response(self, request, response):
        return response


########################################
# ../../../omlish/http/versions.py


##


class UnknownHttpVersionError(Exception):
    pass


@ta.final
@functools.total_ordering
class HttpVersion:
    def __init__(self, major: int, minor: int) -> None:
        self._major = major
        self._minor = minor

        self._parts = parts = (major, minor)

        self._hash = hash(parts)

        self._str = f'HTTP/{major}.{minor}'
        self._short_str = f'{major}.{minor}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.major}, {self.minor})'

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> ta.Any:
        if not isinstance(other, HttpVersion):
            return NotImplemented
        return self._parts == other._parts

    def __lt__(self, other: object) -> ta.Any:
        if not isinstance(other, HttpVersion):
            return NotImplemented
        return self._parts < other._parts

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    def __str__(self) -> str:
        return self._str

    @property
    def short_str(self) -> str:
        return self._short_str

    def __iter__(self) -> ta.Iterator[int]:
        return iter(self._parts)


@ta.final
class HttpVersions:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    HTTP_0_9 = HttpVersion(0, 9)
    HTTP_1_0 = HttpVersion(1, 0)
    HTTP_1_1 = HttpVersion(1, 1)
    HTTP_2_0 = HttpVersion(2, 0)

    _FROM_STR: ta.ClassVar[ta.Mapping[str, HttpVersion]] = {
        str(v): v for v in [
            HTTP_0_9,
            HTTP_1_0,
            HTTP_1_1,
            HTTP_2_0,
        ]
    }

    @classmethod
    def from_str(cls, s: str) -> HttpVersion:
        try:
            return cls._FROM_STR[s]
        except KeyError:
            raise UnknownHttpVersionError(s) from None

    @classmethod
    def of(cls, o: ta.Union[HttpVersion, str]) -> HttpVersion:
        if isinstance(o, HttpVersion):
            return o
        elif isinstance(o, str):
            return cls.from_str(o)
        else:
            raise TypeError(o)


########################################
# ../../../omlish/io/pushback.py


##


class PushbackReader:
    """
    Wrap a non-seekable stream (e.g. socket.makefile('rb') or BufferedReader)
    and provide:
      - read(n=-1)
      - readline(limit=-1)
      - readuntil(delim, max_bytes, include_delim=True, chunk_size=8192)

    Extra bytes read past a delimiter are kept in an internal pushback buffer and returned on subsequent reads/readline
    calls.
    """

    def __init__(self, raw):
        self._raw = raw
        self._pushback = bytearray()

    class MaxLengthExceededError(Exception):
        pass

    def read(self, n: int = -1) -> bytes:
        if n == 0:
            return b''

        # read all
        if n < 0:
            out = bytes(self._pushback)
            self._pushback.clear()
            rest = self._raw.read(-1)
            return out + (rest or b'')

        # satisfy from pushback first
        if len(self._pushback) >= n:
            out = bytes(self._pushback[:n])
            del self._pushback[:n]
            return out

        out = bytes(self._pushback)
        self._pushback.clear()
        need = n - len(out)
        chunk = self._raw.read(need) or b''
        return out + chunk

    def readline(self, limit: int = -1) -> bytes:
        # If limit is set, we must not exceed it.
        if limit == 0:
            return b''

        # First, see if pushback already contains a full line.
        nl = self._pushback.find(b'\n')
        if nl != -1:
            end = nl + 1
            if limit > -1:
                end = min(end, limit)
            out = bytes(self._pushback[:end])
            del self._pushback[:end]
            return out

        # Otherwise, accumulate until newline or limit or EOF.
        buf = bytearray()
        if self._pushback:
            buf += self._pushback
            self._pushback.clear()

        while True:
            # Stop if limit reached
            if limit > -1 and len(buf) >= limit:
                return bytes(buf[:limit])

            # Read more
            # Choose a chunk size that respects limit
            to_read = 8192
            if limit > -1:
                to_read = min(to_read, limit - len(buf))
            chunk = self._raw.read1(to_read)
            if not chunk:
                return bytes(buf)

            buf += chunk
            nl = buf.find(b'\n')
            if nl != -1:
                end = nl + 1
                if limit > -1:
                    end = min(end, limit)
                out = bytes(buf[:end])
                # push back anything after the returned part
                if end < len(buf):
                    self._pushback += buf[end:]
                return out

    def readuntil(
            self,
            delim: bytes,
            *,
            max_bytes: ta.Optional[int] = None,
            include_delim: bool = True,
            chunk_size: int = 8192,
    ) -> bytes:
        if not delim:
            raise ValueError('delim must be non-empty')
        if max_bytes is not None and max_bytes < 0:
            raise ValueError('max_bytes must be >= 0')

        buf = bytearray()

        # start with any pushback data
        if self._pushback:
            buf += self._pushback
            self._pushback.clear()

        while True:
            idx = buf.find(delim)
            if idx != -1:
                end = idx + (len(delim) if include_delim else 0)
                out = bytes(buf[:end])
                # push back everything after the delimiter (or after idx+len(delim))
                tail_start = idx + len(delim)
                if tail_start < len(buf):
                    self._pushback += buf[tail_start:]
                return out

            if max_bytes is not None:
                if len(buf) >= max_bytes:
                    raise PushbackReader.MaxLengthExceededError(f'Delimiter not found within {max_bytes} bytes')
                # read another chunk, but don't exceed max_bytes by too much
                to_read = min(chunk_size, max_bytes - len(buf))
            else:
                to_read = chunk_size

            chunk = self._raw.read1(to_read)
            if not chunk:
                raise EOFError('EOF reached before delimiter was found')
            buf += chunk


########################################
# ../../../omlish/lite/abstract.py


##


_ABSTRACT_METHODS_ATTR = '__abstractmethods__'
_IS_ABSTRACT_METHOD_ATTR = '__isabstractmethod__'


def is_abstract_method(obj: ta.Any) -> bool:
    return bool(getattr(obj, _IS_ABSTRACT_METHOD_ATTR, False))


def compute_abstract_methods(cls: type) -> ta.FrozenSet[str]:
    # ~> https://github.com/python/cpython/blob/f3476c6507381ca860eec0989f53647b13517423/Modules/_abc.c#L358

    # Stage 1: direct abstract methods

    abstracts = {
        a
        # Get items as a list to avoid mutation issues during iteration
        for a, v in list(cls.__dict__.items())
        if is_abstract_method(v)
    }

    # Stage 2: inherited abstract methods

    for base in cls.__bases__:
        # Get __abstractmethods__ from base if it exists
        if (base_abstracts := getattr(base, _ABSTRACT_METHODS_ATTR, None)) is None:
            continue

        # Iterate over abstract methods in base
        for key in base_abstracts:
            # Check if this class has an attribute with this name
            try:
                value = getattr(cls, key)
            except AttributeError:
                # Attribute not found in this class, skip
                continue

            # Check if it's still abstract
            if is_abstract_method(value):
                abstracts.add(key)

    return frozenset(abstracts)


def update_abstracts(cls: ta.Type[T], *, force: bool = False) -> ta.Type[T]:
    if not force and not hasattr(cls, _ABSTRACT_METHODS_ATTR):
        # Per stdlib: We check for __abstractmethods__ here because cls might by a C implementation or a python
        # implementation (especially during testing), and we want to handle both cases.
        return cls

    abstracts = compute_abstract_methods(cls)
    setattr(cls, _ABSTRACT_METHODS_ATTR, abstracts)
    return cls


#


class AbstractTypeError(TypeError):
    pass


_FORCE_ABSTRACT_ATTR = '__forceabstract__'


class Abstract:
    """
    Different from, but interoperable with, abc.ABC / abc.ABCMeta:

     - This raises AbstractTypeError during class creation, not instance instantiation - unless Abstract or abc.ABC are
       explicitly present in the class's direct bases.
     - This will forbid instantiation of classes with Abstract in their direct bases even if there are no
       abstractmethods left on the class.
     - This is a mixin, not a metaclass.
     - As it is not an ABCMeta, this does not support virtual base classes. As a result, operations like `isinstance`
       and `issubclass` are ~7x faster.
     - It additionally enforces a base class order of (Abstract, abc.ABC) to preemptively prevent common mro conflicts.

    If not mixed-in with an ABCMeta, it will update __abstractmethods__ itself.
    """

    __slots__ = ()

    __abstractmethods__: ta.ClassVar[ta.FrozenSet[str]] = frozenset()

    #

    def __forceabstract__(self):
        raise TypeError

    # This is done manually, rather than through @abc.abstractmethod, to mask it from static analysis.
    setattr(__forceabstract__, _IS_ABSTRACT_METHOD_ATTR, True)

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        setattr(
            cls,
            _FORCE_ABSTRACT_ATTR,
            getattr(Abstract, _FORCE_ABSTRACT_ATTR) if Abstract in cls.__bases__ else False,
        )

        super().__init_subclass__(**kwargs)

        if not (Abstract in cls.__bases__ or abc.ABC in cls.__bases__):
            if ams := compute_abstract_methods(cls):
                amd = {
                    a: mcls
                    for mcls in cls.__mro__[::-1]
                    for a in ams
                    if a in mcls.__dict__
                }

                raise AbstractTypeError(
                    f'Cannot subclass abstract class {cls.__name__} with abstract methods: ' +
                    ', '.join(sorted([
                        '.'.join([
                            *([
                                *([m] if (m := getattr(c, '__module__')) else []),
                                getattr(c, '__qualname__', getattr(c, '__name__')),
                            ] if c is not None else '?'),
                            a,
                        ])
                        for a in ams
                        for c in [amd.get(a)]
                    ])),
                )

        xbi = (Abstract, abc.ABC)  # , ta.Generic ?
        bis = [(cls.__bases__.index(b), b) for b in xbi if b in cls.__bases__]
        if bis != sorted(bis):
            raise TypeError(
                f'Abstract subclass {cls.__name__} must have proper base class order of '
                f'({", ".join(getattr(b, "__name__") for b in xbi)}), got: '
                f'({", ".join(getattr(b, "__name__") for _, b in sorted(bis))})',
            )

        if not isinstance(cls, abc.ABCMeta):
            update_abstracts(cls, force=True)


########################################
# ../../../omlish/lite/asyncs.py


##


async def opt_await(aw: ta.Optional[ta.Awaitable[T]]) -> ta.Optional[T]:
    return (await aw if aw is not None else None)


async def async_list(ai: ta.AsyncIterable[T]) -> ta.List[T]:
    return [v async for v in ai]


async def async_enumerate(ai: ta.AsyncIterable[T]) -> ta.AsyncIterable[ta.Tuple[int, T]]:
    i = 0
    async for e in ai:
        yield (i, e)
        i += 1


##


def as_async(fn: ta.Callable[..., T], *, wrap: bool = False) -> ta.Callable[..., ta.Awaitable[T]]:
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)

    return functools.wraps(fn)(inner) if wrap else inner


##


class SyncAwaitCoroutineNotTerminatedError(Exception):
    pass


def sync_await(aw: ta.Awaitable[T]) -> T:
    """
    Allows for the synchronous execution of async functions which will never actually *externally* await anything. These
    functions are allowed to await any number of other functions - including contextmanagers and generators - so long as
    nothing ever actually 'leaks' out of the function, presumably to an event loop.
    """

    ret = missing = object()

    async def thunk():
        nonlocal ret

        ret = await aw

    cr = thunk()
    try:
        try:
            cr.send(None)
        except StopIteration:
            pass

        if ret is missing or cr.cr_await is not None or cr.cr_running:
            raise SyncAwaitCoroutineNotTerminatedError('Not terminated')

    finally:
        cr.close()

    return ta.cast(T, ret)


#


def sync_aiter(ai: ta.AsyncIterator[T]) -> ta.Iterator[T]:
    while True:
        try:
            o = sync_await(ai.__anext__())
        except StopAsyncIteration:
            break
        yield o


def sync_async_list(ai: ta.AsyncIterable[T]) -> ta.List[T]:
    """
    Uses `sync_await` to synchronously read the full contents of a function call returning an async iterator, given that
    the function never externally awaits anything.
    """

    lst: ta.Optional[ta.List[T]] = None

    async def inner():
        nonlocal lst

        lst = [v async for v in ai]

    sync_await(inner())

    if not isinstance(lst, list):
        raise TypeError(lst)

    return lst


#


@ta.final
class SyncAwaitContextManager(ta.Generic[T]):
    def __init__(self, acm: ta.AsyncContextManager[T]) -> None:
        self._acm = acm

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._acm!r})'

    def __enter__(self) -> T:
        return sync_await(self._acm.__aenter__())

    def __exit__(self, exc_type, exc_val, exc_tb):
        return sync_await(self._acm.__aexit__(exc_type, exc_val, exc_tb))


sync_async_with = SyncAwaitContextManager


##


@ta.final
class SyncToAsyncContextManager(ta.Generic[T]):
    def __init__(self, cm: ta.ContextManager[T]) -> None:
        self._cm = cm

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._cm!r})'

    async def __aenter__(self) -> T:
        return self._cm.__enter__()

    async def __aexit__(self, exc_type, exc_value, traceback, /):
        return self._cm.__exit__(exc_type, exc_value, traceback)


as_async_context_manager = SyncToAsyncContextManager


########################################
# ../../../omlish/lite/cached.py


##


class _AbstractCachedNullary:
    def __init__(self, fn):
        super().__init__()

        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):  # noqa
        raise TypeError

    def __get__(self, instance, owner=None):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


##


class _CachedNullary(_AbstractCachedNullary):
    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value


def cached_nullary(fn: CallableT) -> CallableT:
    return _CachedNullary(fn)  # type: ignore


def static_init(fn: CallableT) -> CallableT:
    fn = cached_nullary(fn)
    fn()
    return fn


##


class _AsyncCachedNullary(_AbstractCachedNullary):
    async def __call__(self, *args, **kwargs):
        if self._value is self._missing:
            self._value = await self._fn()
        return self._value


def async_cached_nullary(fn):  # ta.Callable[..., T]) -> ta.Callable[..., T]:
    return _AsyncCachedNullary(fn)


##


cached_property = functools.cached_property


class _cached_property:  # noqa
    """Backported to pick up https://github.com/python/cpython/commit/056dfc71dce15f81887f0bd6da09d6099d71f979 ."""

    def __init__(self, func):
        self.func = func
        self.attrname = None  # noqa
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__

    _NOT_FOUND = object()

    def __set_name__(self, owner, name):
        if self.attrname is None:
            self.attrname = name  # noqa
        elif name != self.attrname:
            raise TypeError(
                f'Cannot assign the same cached_property to two different names ({self.attrname!r} and {name!r}).',
            )

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError('Cannot use cached_property instance without calling __set_name__ on it.')

        try:
            cache = instance.__dict__
        except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
            raise TypeError(
                f"No '__dict__' attribute on {type(instance).__name__!r} instance to cache {self.attrname!r} property.",
            ) from None

        val = cache.get(self.attrname, self._NOT_FOUND)

        if val is self._NOT_FOUND:
            val = self.func(instance)
            try:
                cache[self.attrname] = val
            except TypeError:
                raise TypeError(
                    f"The '__dict__' attribute on {type(instance).__name__!r} instance does not support item "
                    f"assignment for caching {self.attrname!r} property.",
                ) from None

        return val


globals()['cached_property'] = _cached_property


########################################
# ../../../omlish/lite/check.py
"""
TODO:
 - def maybe(v: lang.Maybe[T])
 - def not_ ?
 - ** class @dataclass Raise - user message should be able to be an exception type or instance or factory
"""


##


class Checks:
    def __init__(self) -> None:
        super().__init__()

        self._config_lock = threading.RLock()
        self._on_raise_fns: ta.Sequence[CheckOnRaiseFn] = []
        self._exception_factory: CheckExceptionFactory = Checks.default_exception_factory
        self._args_renderer: ta.Optional[CheckArgsRenderer] = None
        self._late_configure_fns: ta.Sequence[CheckLateConfigureFn] = []

    @staticmethod
    def default_exception_factory(exc_cls: ta.Type[Exception], *args, **kwargs) -> Exception:
        return exc_cls(*args, **kwargs)  # noqa

    #

    def register_on_raise(self, fn: CheckOnRaiseFn) -> None:
        with self._config_lock:
            self._on_raise_fns = [*self._on_raise_fns, fn]

    def unregister_on_raise(self, fn: CheckOnRaiseFn) -> None:
        with self._config_lock:
            self._on_raise_fns = [e for e in self._on_raise_fns if e != fn]

    #

    def register_on_raise_breakpoint_if_env_var_set(self, key: str) -> None:
        import os

        def on_raise(exc: Exception) -> None:  # noqa
            if key in os.environ:
                breakpoint()  # noqa

        self.register_on_raise(on_raise)

    #

    def set_exception_factory(self, factory: CheckExceptionFactory) -> None:
        self._exception_factory = factory

    def set_args_renderer(self, renderer: ta.Optional[CheckArgsRenderer]) -> None:
        self._args_renderer = renderer

    #

    def register_late_configure(self, fn: CheckLateConfigureFn) -> None:
        with self._config_lock:
            self._late_configure_fns = [*self._late_configure_fns, fn]

    def _late_configure(self) -> None:
        if not self._late_configure_fns:
            return

        with self._config_lock:
            if not (lc := self._late_configure_fns):
                return

            for fn in lc:
                fn(self)

            self._late_configure_fns = []

    #

    class _ArgsKwargs:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    def _raise(
            self,
            exception_type: ta.Type[Exception],
            default_message: str,
            message: CheckMessage,
            ak: _ArgsKwargs = _ArgsKwargs(),
            *,
            render_fmt: ta.Optional[str] = None,
    ) -> ta.NoReturn:
        exc_args = ()
        if callable(message):
            message = ta.cast(ta.Callable, message)(*ak.args, **ak.kwargs)
            if isinstance(message, tuple):
                message, *exc_args = message  # type: ignore

        if message is None:
            message = default_message

        self._late_configure()

        if render_fmt is not None and (af := self._args_renderer) is not None:
            rendered_args = af(render_fmt, *ak.args)
            if rendered_args is not None:
                message = f'{message} : {rendered_args}'

        exc = self._exception_factory(
            exception_type,
            message,
            *exc_args,
            *ak.args,
            **ak.kwargs,
        )

        for fn in self._on_raise_fns:
            fn(exc)

        raise exc

    #

    def _unpack_isinstance_spec(self, spec: ta.Any) -> ta.Any:
        if isinstance(spec, type):
            return spec
        if spec == ta.Any:
            return object
        if spec is None:
            return None.__class__
        if not isinstance(spec, tuple):
            return spec
        if ta.Any in spec:
            return object
        if None in spec:
            spec = tuple(filter(None, spec)) + (None.__class__,)  # noqa
        return spec

    @ta.overload
    def isinstance(self, v: ta.Any, spec: ta.Type[T], msg: CheckMessage = None, /) -> T:
        ...

    @ta.overload
    def isinstance(self, v: ta.Any, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Any:
        ...

    def isinstance(self, v, spec, msg=None):
        if not isinstance(v, self._unpack_isinstance_spec(spec)):
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='not isinstance(%s, %s)',
            )

        return v

    @ta.overload
    def of_isinstance(self, spec: ta.Type[T], msg: CheckMessage = None, /) -> ta.Callable[[ta.Any], T]:
        ...

    @ta.overload
    def of_isinstance(self, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Callable[[ta.Any], ta.Any]:
        ...

    def of_isinstance(self, spec, msg=None, /):
        spec = self._unpack_isinstance_spec(spec)

        def inner(v):
            return self.isinstance(v, spec, msg)

        return inner

    def cast(self, v: ta.Any, cls: ta.Type[T], msg: CheckMessage = None, /) -> T:
        if not isinstance(v, cls):
            self._raise(
                TypeError,
                'Must be instance',
                msg,
                Checks._ArgsKwargs(v, cls),
            )

        return v

    def of_cast(self, cls: ta.Type[T], msg: CheckMessage = None, /) -> ta.Callable[[T], T]:
        def inner(v):
            return self.cast(v, cls, msg)

        return inner

    def not_isinstance(self, v: T, spec: ta.Any, msg: CheckMessage = None, /) -> T:  # noqa
        if isinstance(v, self._unpack_isinstance_spec(spec)):
            self._raise(
                TypeError,
                'Must not be instance',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='isinstance(%s, %s)',
            )

        return v

    def of_not_isinstance(self, spec: ta.Any, msg: CheckMessage = None, /) -> ta.Callable[[T], T]:
        spec = self._unpack_isinstance_spec(spec)

        def inner(v):
            return self.not_isinstance(v, spec, msg)

        return inner

    ##

    def issubclass(self, v: ta.Type[T], spec: ta.Any, msg: CheckMessage = None, /) -> ta.Type[T]:  # noqa
        if not issubclass(v, spec):
            self._raise(
                TypeError,
                'Must be subclass',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='not issubclass(%s, %s)',
            )

        return v

    def not_issubclass(self, v: ta.Type[T], spec: ta.Any, msg: CheckMessage = None, /) -> ta.Type[T]:
        if issubclass(v, spec):
            self._raise(
                TypeError,
                'Must not be subclass',
                msg,
                Checks._ArgsKwargs(v, spec),
                render_fmt='issubclass(%s, %s)',
            )

        return v

    def not_issubclass_except_nameerror(self, v: ta.Type[T], spec: ta.Callable[[], type], msg: CheckMessage = None, /) -> ta.Type[T]:  # noqa
        try:
            c = spec()
        except NameError:
            return v

        if issubclass(v, c):
            self._raise(
                TypeError,
                'Must not be subclass',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='issubclass(%s, %s)',
            )

        return v

    #

    def in_(self, v: T, c: ta.Container[T], msg: CheckMessage = None, /) -> T:
        if v not in c:
            self._raise(
                ValueError,
                'Must be in',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='%s not in %s',
            )

        return v

    def not_in(self, v: T, c: ta.Container[T], msg: CheckMessage = None, /) -> T:
        if v in c:
            self._raise(
                ValueError,
                'Must not be in',
                msg,
                Checks._ArgsKwargs(v, c),
                render_fmt='%s in %s',
            )

        return v

    def empty(self, v: SizedT, msg: CheckMessage = None, /) -> SizedT:
        if len(v) != 0:
            self._raise(
                ValueError,
                'Must be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def iterempty(self, v: ta.Iterable[T], msg: CheckMessage = None, /) -> ta.Iterable[T]:
        it = iter(v)
        try:
            next(it)
        except StopIteration:
            pass
        else:
            self._raise(
                ValueError,
                'Must be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def not_empty(self, v: SizedT, msg: CheckMessage = None, /) -> SizedT:
        if len(v) == 0:
            self._raise(
                ValueError,
                'Must not be empty',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def unique(self, it: ta.Iterable[T], msg: CheckMessage = None, /) -> ta.Iterable[T]:
        dupes = [e for e, c in collections.Counter(it).items() if c > 1]
        if dupes:
            self._raise(
                ValueError,
                'Must be unique',
                msg,
                Checks._ArgsKwargs(it, dupes),
            )

        return it

    def single(self, obj: ta.Iterable[T], msg: CheckMessage = None, /) -> T:
        try:
            [value] = obj
        except ValueError:
            self._raise(
                ValueError,
                'Must be single',
                msg,
                Checks._ArgsKwargs(obj),
                render_fmt='%s',
            )

        return value

    def opt_single(self, obj: ta.Iterable[T], msg: CheckMessage = None, /) -> ta.Optional[T]:
        it = iter(obj)
        try:
            value = next(it)
        except StopIteration:
            return None

        try:
            next(it)
        except StopIteration:
            return value  # noqa

        self._raise(
            ValueError,
            'Must be empty or single',
            msg,
            Checks._ArgsKwargs(obj),
            render_fmt='%s',
        )

        raise RuntimeError  # noqa

    async def async_single(self, obj: ta.AsyncIterable[T], msg: CheckMessage = None, /) -> T:
        ait = obj.__aiter__()

        try:
            try:
                value = await ait.__anext__()
            except StopAsyncIteration:
                pass

            else:
                try:
                    await ait.__anext__()
                except StopAsyncIteration:
                    return value

        finally:
            if inspect.isasyncgen(ait):
                await ait.aclose()

        self._raise(
            ValueError,
            'Must be single',
            msg,
            Checks._ArgsKwargs(obj),
            render_fmt='%s',
        )

        raise RuntimeError  # noqa

    async def async_opt_single(self, obj: ta.AsyncIterable[T], msg: CheckMessage = None, /) -> ta.Optional[T]:
        ait = obj.__aiter__()

        try:
            try:
                value = await ait.__anext__()
            except StopAsyncIteration:
                return None

            try:
                await ait.__anext__()
            except StopAsyncIteration:
                return value  # noqa

        finally:
            if inspect.isasyncgen(ait):
                await ait.aclose()

        self._raise(
            ValueError,
            'Must be empty or single',
            msg,
            Checks._ArgsKwargs(obj),
            render_fmt='%s',
        )

        raise RuntimeError  # noqa

    #

    def none(self, v: ta.Any, msg: CheckMessage = None, /) -> None:
        if v is not None:
            self._raise(
                ValueError,
                'Must be None',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

    def not_none(self, v: ta.Optional[T], msg: CheckMessage = None, /) -> T:
        if v is None:
            self._raise(
                ValueError,
                'Must not be None',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    #

    def equal(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o != v:
            self._raise(
                ValueError,
                'Must be equal',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s != %s',
            )

        return v

    def not_equal(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o == v:
            self._raise(
                ValueError,
                'Must not be equal',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s == %s',
            )

        return v

    def is_(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o is not v:
            self._raise(
                ValueError,
                'Must be the same',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s is not %s',
            )

        return v

    def is_not(self, v: T, o: ta.Any, msg: CheckMessage = None, /) -> T:
        if o is v:
            self._raise(
                ValueError,
                'Must not be the same',
                msg,
                Checks._ArgsKwargs(v, o),
                render_fmt='%s is %s',
            )

        return v

    def callable(self, v: T, msg: CheckMessage = None, /) -> T:  # noqa
        if not callable(v):
            self._raise(
                TypeError,
                'Must be callable',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def non_empty_str(self, v: ta.Optional[str], msg: CheckMessage = None, /) -> str:
        if not isinstance(v, str) or not v:
            self._raise(
                ValueError,
                'Must be non-empty str',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

        return v

    def replacing(self, expected: ta.Any, old: ta.Any, new: T, msg: CheckMessage = None, /) -> T:
        if old != expected:
            self._raise(
                ValueError,
                'Must be replacing',
                msg,
                Checks._ArgsKwargs(expected, old, new),
                render_fmt='%s -> %s -> %s',
            )

        return new

    def replacing_none(self, old: ta.Any, new: T, msg: CheckMessage = None, /) -> T:
        if old is not None:
            self._raise(
                ValueError,
                'Must be replacing None',
                msg,
                Checks._ArgsKwargs(old, new),
                render_fmt='%s -> %s',
            )

        return new

    #

    def arg(self, v: bool, msg: CheckMessage = None, /) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'Argument condition not met',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )

    def state(self, v: bool, msg: CheckMessage = None, /) -> None:
        if not v:
            self._raise(
                RuntimeError,
                'State condition not met',
                msg,
                Checks._ArgsKwargs(v),
                render_fmt='%s',
            )


check = Checks()


########################################
# ../../../omlish/lite/contextmanagers.py


##


class ExitStacked:
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for a in ('__enter__', '__exit__'):
            for b in cls.__bases__:
                if b is ExitStacked:
                    continue
                try:
                    fn = getattr(b, a)
                except AttributeError:
                    pass
                else:
                    if fn is not getattr(ExitStacked, a):
                        raise TypeError(f'ExitStacked subclass {cls} must not not override {a} via {b}')

    _exit_stack: ta.Optional[contextlib.ExitStack] = None

    @contextlib.contextmanager
    def _exit_stacked_init_wrapper(self) -> ta.Iterator[None]:
        """
        Overridable wrapper around __enter__ which deliberately does not have access to an _exit_stack yet. Intended for
        things like wrapping __enter__ in a lock.
        """

        yield

    @ta.final
    def __enter__(self: ExitStackedT) -> ExitStackedT:
        """
        Final because any contexts entered during this init must be exited if any exception is thrown, and user
        overriding would likely interfere with that. Override `_enter_contexts` for such init.
        """

        with self._exit_stacked_init_wrapper():
            if self._exit_stack is not None:
                raise RuntimeError
            es = self._exit_stack = contextlib.ExitStack()
            es.__enter__()
            try:
                self._enter_contexts()
            except BaseException:  # noqa
                es.__exit__(*sys.exc_info())
                raise
            return self

    @ta.final
    def __exit__(self, exc_type, exc_val, exc_tb):
        if (es := self._exit_stack) is None:
            return None
        try:
            self._exit_contexts()
        except BaseException:  # noqa
            es.__exit__(*sys.exc_info())
            raise
        return es.__exit__(exc_type, exc_val, exc_tb)

    def _enter_contexts(self) -> None:
        pass

    def _exit_contexts(self) -> None:
        pass

    def _enter_context(self, cm: ta.ContextManager[T]) -> T:
        if (es := self._exit_stack) is None:
            raise RuntimeError
        return es.enter_context(cm)


class AsyncExitStacked:
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for a in ('__aenter__', '__aexit__'):
            for b in cls.__bases__:
                if b is AsyncExitStacked:
                    continue
                try:
                    fn = getattr(b, a)
                except AttributeError:
                    pass
                else:
                    if fn is not getattr(AsyncExitStacked, a):
                        raise TypeError(f'AsyncExitStacked subclass {cls} must not not override {a} via {b}')

    _exit_stack: ta.Optional[contextlib.AsyncExitStack] = None

    @contextlib.asynccontextmanager
    async def _async_exit_stacked_init_wrapper(self) -> ta.AsyncGenerator[None, None]:
        yield

    @ta.final
    async def __aenter__(self: AsyncExitStackedT) -> AsyncExitStackedT:
        async with self._async_exit_stacked_init_wrapper():
            if self._exit_stack is not None:
                raise RuntimeError
            es = self._exit_stack = contextlib.AsyncExitStack()
            await es.__aenter__()
            try:
                await self._async_enter_contexts()
            except BaseException:  # noqa
                await es.__aexit__(*sys.exc_info())
                raise
            return self

    @ta.final
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if (es := self._exit_stack) is None:
            return None
        try:
            await self._async_exit_contexts()
        except BaseException:  # noqa
            await es.__aexit__(*sys.exc_info())
            raise
        return await es.__aexit__(exc_type, exc_val, exc_tb)

    async def _async_enter_contexts(self) -> None:
        pass

    async def _async_exit_contexts(self) -> None:
        pass

    def _enter_context(self, cm: ta.ContextManager[T]) -> T:
        if (es := self._exit_stack) is None:
            raise RuntimeError
        return es.enter_context(cm)

    async def _enter_async_context(self, cm: ta.AsyncContextManager[T]) -> T:
        if (es := self._exit_stack) is None:
            raise RuntimeError
        return await es.enter_async_context(cm)


##


@contextlib.contextmanager
def defer(fn: ta.Callable, *args: ta.Any, **kwargs: ta.Any) -> ta.Generator[ta.Callable, None, None]:
    if args or kwargs:
        fn = functools.partial(fn, *args, **kwargs)
    try:
        yield fn
    finally:
        fn()


@contextlib.asynccontextmanager
async def adefer(fn: ta.Awaitable) -> ta.AsyncGenerator[ta.Awaitable, None]:
    try:
        yield fn
    finally:
        await fn


##


@contextlib.contextmanager
def attr_setting(obj, attr, val, *, default=None):  # noqa
    not_set = object()
    orig = getattr(obj, attr, not_set)
    try:
        setattr(obj, attr, val)
        if orig is not not_set:
            yield orig
        else:
            yield default
    finally:
        if orig is not_set:
            delattr(obj, attr)
        else:
            setattr(obj, attr, orig)


##


class AsyncClosingManager(contextlib.AbstractAsyncContextManager):
    def __init__(self, thing):
        self.thing = thing

    async def __aenter__(self):
        return self.thing

    async def __aexit__(self, *exc_info):
        await self.thing.aclose()


aclosing = AsyncClosingManager


########################################
# ../../../omlish/lite/dataclasses.py


##


def dataclass_shallow_astuple(o: ta.Any) -> ta.Tuple[ta.Any, ...]:
    return tuple(getattr(o, f.name) for f in dc.fields(o))


def dataclass_shallow_asdict(o: ta.Any) -> ta.Dict[str, ta.Any]:
    return {f.name: getattr(o, f.name) for f in dc.fields(o)}


##


def is_immediate_dataclass(cls: type) -> bool:
    if not isinstance(cls, type):
        raise TypeError(cls)
    return dc._FIELDS in cls.__dict__  # type: ignore[attr-defined]  # noqa


##


def _install_dataclass_fn(cls: type, fn: ta.Any, fn_name: ta.Optional[str] = None) -> None:
    if fn_name is None:
        fn_name = fn.__name__
    setattr(cls, fn_name, fn)
    fn.__qualname__ = f'{cls.__qualname__}.{fn_name}'


##


def install_dataclass_cache_hash(
        *,
        cached_hash_attr: str = '__dataclass_hash__',
):
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        if (
                cls.__hash__ is object.__hash__ or
                '__hash__' not in cls.__dict__
        ):
            raise TypeError(cls)

        real_hash = cls.__hash__

        def cached_hash(self) -> int:
            try:
                return object.__getattribute__(self, cached_hash_attr)
            except AttributeError:
                object.__setattr__(self, cached_hash_attr, h := real_hash(self))  # type: ignore[call-arg]
            return h

        _install_dataclass_fn(cls, cached_hash, '__hash__')

        return cls

    return inner


##


def dataclass_maybe_post_init(sup: ta.Any) -> bool:
    if not isinstance(sup, super):
        raise TypeError(sup)
    try:
        fn = sup.__post_init__  # type: ignore
    except AttributeError:
        return False
    fn()
    return True


##


def dataclass_filtered_repr(
        obj: ta.Any,
        fn: ta.Union[ta.Callable[[ta.Any, dc.Field, ta.Any], bool], ta.Literal['omit_none', 'omit_falsey']],
) -> str:
    if fn == 'omit_none':
        fn = lambda o, f, v: v is not None  # noqa
    elif fn == 'omit_falsey':
        fn = lambda o, f, v: bool(v)

    return (
        f'{obj.__class__.__qualname__}(' +
        ', '.join([
            f'{f.name}={v!r}'
            for f in dc.fields(obj)
            if fn(obj, f, v := getattr(obj, f.name))
        ]) +
        ')'
    )


def dataclass_repr_omit_none(obj: ta.Any) -> str:
    return dataclass_filtered_repr(obj, 'omit_none')


def dataclass_repr_omit_falsey(obj: ta.Any) -> str:
    return dataclass_filtered_repr(obj, 'omit_falsey')


def install_dataclass_filtered_repr(
        fn: ta.Union[ta.Callable[[ta.Any, dc.Field, ta.Any], bool], ta.Literal['omit_none', 'omit_falsey']],
):
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        def filtered_repr(self) -> str:
            return dataclass_filtered_repr(self, fn)

        _install_dataclass_fn(cls, filtered_repr, '__repr__')

        return cls

    return inner


#


def dataclass_terse_repr(obj: ta.Any) -> str:
    return f'{obj.__class__.__qualname__}({", ".join(repr(getattr(obj, f.name)) for f in dc.fields(obj))})'


def install_dataclass_terse_repr():
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        def terse_repr(self) -> str:
            return dataclass_terse_repr(self)

        _install_dataclass_fn(cls, terse_repr, '__repr__')

        return cls

    return inner


##


def dataclass_descriptor_method(*bind_attrs: str, bind_owner: bool = False) -> ta.Callable:
    if not bind_attrs:
        def __get__(self, instance, owner=None):  # noqa
            return self

    elif bind_owner:
        def __get__(self, instance, owner=None):  # noqa
            # Guaranteed to return a new instance even with no attrs
            return dc.replace(self, **{
                a: v.__get__(instance, owner) if (v := getattr(self, a)) is not None else None
                for a in bind_attrs
            })

    else:
        def __get__(self, instance, owner=None):  # noqa
            if instance is None:
                return self

            # Guaranteed to return a new instance even with no attrs
            return dc.replace(self, **{
                a: v.__get__(instance, owner) if (v := getattr(self, a)) is not None else None
                for a in bind_attrs
            })

    return __get__


##


def install_dataclass_kw_only_init():
    def inner(cls):
        if not isinstance(cls, type) and dc.is_dataclass(cls):
            raise TypeError(cls)

        real_init = cls.__init__  # type: ignore[misc]

        flds = dc.fields(cls)  # noqa

        if any(f.name == 'self' for f in flds):
            self_name = '__dataclass_self__'
        else:
            self_name = 'self'

        src = '\n'.join([
            'def __init__(',
            f'    {self_name},',
            '    *,',
            *[
                ''.join([
                    f'    {f.name}: __dataclass_type_{f.name}__',
                    f' = __dataclass_default_{f.name}__' if f.default is not dc.MISSING else '',
                    ',',
                ])
                for f in flds
            ],
            ') -> __dataclass_None__:',
            '    __dataclass_real_init__(',
            f'        {self_name},',
            *[
                f'        {f.name}={f.name},'
                for f in flds
            ],
            '    )',
        ])

        ns: dict = {
            '__dataclass_None__': None,
            '__dataclass_real_init__': real_init,
            **{
                f'__dataclass_type_{f.name}__': f.type
                for f in flds
            },
            **{
                f'__dataclass_default_{f.name}__': f.default
                for f in flds
                if f.default is not dc.MISSING
            },
        }

        exec(src, ns)

        kw_only_init = ns['__init__']

        functools.update_wrapper(kw_only_init, real_init)

        _install_dataclass_fn(cls, kw_only_init, '__init__')

        return cls

    return inner


##


@dc.dataclass()
class DataclassFieldRequiredError(Exception):
    name: str


def dataclass_field_required(name: str) -> ta.Callable[[], ta.Any]:
    def inner() -> ta.NoReturn:
        raise DataclassFieldRequiredError(name)
    return inner


########################################
# ../../../omlish/lite/json.py


##


JSON_PRETTY_INDENT = 2

JSON_PRETTY_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=JSON_PRETTY_INDENT,
)

json_dump_pretty: ta.Callable[..., None] = functools.partial(json.dump, **JSON_PRETTY_KWARGS)
json_dumps_pretty: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_PRETTY_KWARGS)


##


JSON_COMPACT_SEPARATORS = (',', ':')

JSON_COMPACT_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=None,
    separators=JSON_COMPACT_SEPARATORS,
)

json_dump_compact: ta.Callable[..., None] = functools.partial(json.dump, **JSON_COMPACT_KWARGS)
json_dumps_compact: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_COMPACT_KWARGS)


########################################
# ../../../omlish/lite/objects.py


##


def deep_subclasses(cls: ta.Type[T]) -> ta.Iterator[ta.Type[T]]:
    seen = set()
    todo = list(reversed(cls.__subclasses__()))
    while todo:
        cur = todo.pop()
        if cur in seen:
            continue
        seen.add(cur)
        yield cur
        todo.extend(reversed(cur.__subclasses__()))


##


def mro_owner_dict(
        instance_cls: type,
        owner_cls: ta.Optional[type] = None,
        *,
        bottom_up_key_order: bool = False,
        sort_keys: bool = False,
) -> ta.Mapping[str, ta.Tuple[type, ta.Any]]:
    if owner_cls is None:
        owner_cls = instance_cls

    mro = instance_cls.__mro__[-2::-1]
    try:
        pos = mro.index(owner_cls)
    except ValueError:
        raise TypeError(f'Owner class {owner_cls} not in mro of instance class {instance_cls}') from None

    dct: ta.Dict[str, ta.Tuple[type, ta.Any]] = {}
    if not bottom_up_key_order:
        for cur_cls in mro[:pos + 1][::-1]:
            for k, v in cur_cls.__dict__.items():
                if k not in dct:
                    dct[k] = (cur_cls, v)

    else:
        for cur_cls in mro[:pos + 1]:
            dct.update({k: (cur_cls, v) for k, v in cur_cls.__dict__.items()})

    if sort_keys:
        dct = dict(sorted(dct.items(), key=lambda t: t[0]))

    return dct


def mro_dict(
        instance_cls: type,
        owner_cls: ta.Optional[type] = None,
        *,
        bottom_up_key_order: bool = False,
        sort_keys: bool = False,
) -> ta.Mapping[str, ta.Any]:
    return {
        k: v
        for k, (o, v) in mro_owner_dict(
            instance_cls,
            owner_cls,
            bottom_up_key_order=bottom_up_key_order,
            sort_keys=sort_keys,
        ).items()
    }


def dir_dict(o: ta.Any) -> ta.Dict[str, ta.Any]:
    return {
        a: getattr(o, a)
        for a in dir(o)
    }


########################################
# ../../../omlish/lite/reflect.py


##


_GENERIC_ALIAS_TYPES = (
    ta._GenericAlias,  # type: ignore  # noqa
    *([ta._SpecialGenericAlias] if hasattr(ta, '_SpecialGenericAlias') else []),  # noqa
)


def is_generic_alias(obj: ta.Any, *, origin: ta.Any = None) -> bool:
    return (
        isinstance(obj, _GENERIC_ALIAS_TYPES) and
        (origin is None or ta.get_origin(obj) is origin)
    )


is_callable_alias = functools.partial(is_generic_alias, origin=ta.Callable)


##


_UNION_ALIAS_ORIGINS = frozenset([
    ta.get_origin(ta.Optional[int]),
    *(
        [
            ta.get_origin(int | None),
            ta.get_origin(getattr(ta, 'TypeVar')('_T') | None),
        ] if sys.version_info >= (3, 10) else ()
    ),
])


def is_union_alias(obj: ta.Any) -> bool:
    return ta.get_origin(obj) in _UNION_ALIAS_ORIGINS


#


def is_optional_alias(spec: ta.Any) -> bool:
    return (
        is_union_alias(spec) and
        len(ta.get_args(spec)) == 2 and
        any(a in (None, type(None)) for a in ta.get_args(spec))
    )


def get_optional_alias_arg(spec: ta.Any) -> ta.Any:
    [it] = [it for it in ta.get_args(spec) if it not in (None, type(None))]
    return it


##


def is_new_type(spec: ta.Any) -> bool:
    if isinstance(ta.NewType, type):
        return isinstance(spec, ta.NewType)
    else:
        # Before https://github.com/python/cpython/commit/c2f33dfc83ab270412bf243fb21f724037effa1a
        return isinstance(spec, types.FunctionType) and spec.__code__ is ta.NewType.__code__.co_consts[1]  # type: ignore  # noqa


def get_new_type_supertype(spec: ta.Any) -> ta.Any:
    return spec.__supertype__


##


def is_literal_type(spec: ta.Any) -> bool:
    if hasattr(ta, '_LiteralGenericAlias'):
        return isinstance(spec, ta._LiteralGenericAlias)  # noqa
    else:
        return (
            isinstance(spec, ta._GenericAlias) and  # type: ignore  # noqa
            spec.__origin__ is ta.Literal
        )


def get_literal_type_args(spec: ta.Any) -> ta.Iterable[ta.Any]:
    return spec.__args__


########################################
# ../../../omlish/lite/strings.py


##


def camel_case(name: str, *, lower: bool = False) -> str:
    if not name:
        return ''
    s = ''.join(map(str.capitalize, name.split('_')))  # noqa
    if lower:
        s = s[0].lower() + s[1:]
    return s


def snake_case(name: str) -> str:
    uppers: list[int | None] = [i for i, c in enumerate(name) if c.isupper()]
    return '_'.join([name[l:r].lower() for l, r in zip([None, *uppers], [*uppers, None])]).strip('_')


##


def is_dunder(name: str) -> bool:
    return (
        name[:2] == name[-2:] == '__' and
        name[2:3] != '_' and
        name[-3:-2] != '_' and
        len(name) > 4
    )


def is_sunder(name: str) -> bool:
    return (
        name[0] == name[-1] == '_' and
        name[1:2] != '_' and
        name[-2:-1] != '_' and
        len(name) > 2
    )


##


def strip_with_newline(s: str) -> str:
    if not s:
        return ''
    return s.strip() + '\n'


@ta.overload
def split_keep_delimiter(s: str, d: str) -> str:
    ...


@ta.overload
def split_keep_delimiter(s: bytes, d: bytes) -> bytes:
    ...


def split_keep_delimiter(s, d):
    ps = []
    i = 0
    while i < len(s):
        if (n := s.find(d, i)) < i:
            ps.append(s[i:])
            break
        ps.append(s[i:n + 1])
        i = n + 1
    return ps


##


FORMAT_NUM_BYTES_SUFFIXES: ta.Sequence[str] = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB']


def format_num_bytes(num_bytes: int) -> str:
    for i, suffix in enumerate(FORMAT_NUM_BYTES_SUFFIXES):
        value = num_bytes / 1024 ** i
        if num_bytes < 1024 ** (i + 1):
            if value.is_integer():
                return f'{int(value)}{suffix}'
            else:
                return f'{value:.2f}{suffix}'

    return f'{num_bytes / 1024 ** (len(FORMAT_NUM_BYTES_SUFFIXES) - 1):.2f}{FORMAT_NUM_BYTES_SUFFIXES[-1]}'


########################################
# ../../../omlish/lite/typing.py


##
# A workaround for typing deficiencies (like `Argument 2 to NewType(...) must be subclassable`).
#
# Note that this problem doesn't happen at runtime - it happens in mypy:
#
#   mypy <(echo "import typing as ta; MyCallback = ta.NewType('MyCallback', ta.Callable[[], None])")
#   /dev/fd/11:1:22: error: Argument 2 to NewType(...) must be subclassable (got "Callable[[], None]")  [valid-newtype]
#


@dc.dataclass(frozen=True)
class AnyFunc(ta.Generic[T]):
    fn: ta.Callable[..., T]

    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        return self.fn(*args, **kwargs)


@dc.dataclass(frozen=True)
class Func0(ta.Generic[T]):
    fn: ta.Callable[[], T]

    def __call__(self) -> T:
        return self.fn()


@dc.dataclass(frozen=True)
class Func1(ta.Generic[A0, T]):
    fn: ta.Callable[[A0], T]

    def __call__(self, a0: A0) -> T:
        return self.fn(a0)


@dc.dataclass(frozen=True)
class Func2(ta.Generic[A0, A1, T]):
    fn: ta.Callable[[A0, A1], T]

    def __call__(self, a0: A0, a1: A1) -> T:
        return self.fn(a0, a1)


@dc.dataclass(frozen=True)
class Func3(ta.Generic[A0, A1, A2, T]):
    fn: ta.Callable[[A0, A1, A2], T]

    def __call__(self, a0: A0, a1: A1, a2: A2) -> T:
        return self.fn(a0, a1, a2)


##


@dc.dataclass(frozen=True)
class CachedFunc0(ta.Generic[T]):
    fn: ta.Callable[[], T]

    def __call__(self) -> T:
        try:
            return object.__getattribute__(self, '_value')
        except AttributeError:
            pass

        value = self.fn()
        object.__setattr__(self, '_value', value)
        return value


@dc.dataclass(frozen=True)
class AsyncCachedFunc0(ta.Generic[T]):
    fn: ta.Callable[[], ta.Awaitable[T]]

    async def __call__(self) -> T:
        try:
            return object.__getattribute__(self, '_value')
        except AttributeError:
            pass

        value = await self.fn()
        object.__setattr__(self, '_value', value)
        return value


##


_TYPING_ANNOTATIONS_ATTR = '__annotate__' if sys.version_info >= (3, 14) else '__annotations__'


def typing_annotations_attr() -> str:
    return _TYPING_ANNOTATIONS_ATTR


##


@ta.runtime_checkable
class CanInt(ta.Protocol):
    def __int__(self) -> int:
        ...


@ta.runtime_checkable
class CanFloat(ta.Protocol):
    def __float__(self) -> float:
        ...


########################################
# ../../../omlish/logs/levels.py


##


@ta.final
class NamedLogLevel(int):
    # logging.getLevelNamesMapping (or, as that is unavailable <3.11, logging._nameToLevel) includes the deprecated
    # aliases.
    _NAMES_BY_INT: ta.ClassVar[ta.Mapping[LogLevel, str]] = dict(sorted(logging._levelToName.items(), key=lambda t: -t[0]))  # noqa

    _INTS_BY_NAME: ta.ClassVar[ta.Mapping[str, LogLevel]] = {v: k for k, v in _NAMES_BY_INT.items()}

    _NAME_INT_PAIRS: ta.ClassVar[ta.Sequence[ta.Tuple[str, LogLevel]]] = list(_INTS_BY_NAME.items())

    #

    _CACHE: ta.ClassVar[ta.MutableMapping[int, 'NamedLogLevel']] = {}

    @ta.overload
    def __new__(cls, name: str, offset: int = 0, /) -> 'NamedLogLevel':
        ...

    @ta.overload
    def __new__(cls, i: int, /) -> 'NamedLogLevel':
        ...

    def __new__(cls, x, offset=0, /):
        if isinstance(x, str):
            return cls(cls._INTS_BY_NAME[x.upper()] + offset)
        elif not offset and (c := cls._CACHE.get(x)) is not None:
            return c
        else:
            return super().__new__(cls, x + offset)

    #

    _name_and_offset: ta.Tuple[str, int]

    @property
    def name_and_offset(self) -> ta.Tuple[str, int]:
        try:
            return self._name_and_offset
        except AttributeError:
            pass

        if (n := self._NAMES_BY_INT.get(self)) is not None:
            t = (n, 0)
        else:
            for n, i in self._NAME_INT_PAIRS:  # noqa
                if self >= i:
                    t = (n, (self - i))
                    break
            else:
                t = ('NOTSET', int(self))

        self._name_and_offset = t
        return t

    @property
    def exact_name(self) -> ta.Optional[str]:
        n, o = self.name_and_offset
        return n if not o else None

    @property
    def effective_name(self) -> str:
        n, _ = self.name_and_offset
        return n

    #

    def __str__(self) -> str:
        return self.exact_name or f'{self.effective_name}{int(self):+}'

    def __repr__(self) -> str:
        n, o = self.name_and_offset
        return f'{self.__class__.__name__}({n!r}{f", {int(o)}" if o else ""})'

    #

    CRITICAL: ta.ClassVar['NamedLogLevel']
    ERROR: ta.ClassVar['NamedLogLevel']
    WARNING: ta.ClassVar['NamedLogLevel']
    INFO: ta.ClassVar['NamedLogLevel']
    DEBUG: ta.ClassVar['NamedLogLevel']
    NOTSET: ta.ClassVar['NamedLogLevel']


NamedLogLevel.CRITICAL = NamedLogLevel(logging.CRITICAL)
NamedLogLevel.ERROR = NamedLogLevel(logging.ERROR)
NamedLogLevel.WARNING = NamedLogLevel(logging.WARNING)
NamedLogLevel.INFO = NamedLogLevel(logging.INFO)
NamedLogLevel.DEBUG = NamedLogLevel(logging.DEBUG)
NamedLogLevel.NOTSET = NamedLogLevel(logging.NOTSET)


NamedLogLevel._CACHE.update({i: NamedLogLevel(i) for i in NamedLogLevel._NAMES_BY_INT})  # noqa


########################################
# ../../../omlish/logs/std/filters.py


##


class TidLoggingFilter(logging.Filter):
    def filter(self, record):
        # FIXME: handle better - missing from wasm and cosmos
        if hasattr(threading, 'get_native_id'):
            record.tid = threading.get_native_id()
        else:
            record.tid = '?'
        return True


########################################
# ../../../omlish/logs/std/proxy.py


##


class ProxyLoggingFilterer(logging.Filterer):
    def __init__(self, underlying: logging.Filterer) -> None:  # noqa
        self._underlying = underlying

    @property
    def underlying(self) -> logging.Filterer:
        return self._underlying

    @property
    def filters(self):
        return self._underlying.filters

    @filters.setter
    def filters(self, filters):
        self._underlying.filters = filters

    def addFilter(self, filter):  # noqa
        self._underlying.addFilter(filter)

    def removeFilter(self, filter):  # noqa
        self._underlying.removeFilter(filter)

    def filter(self, record):
        return self._underlying.filter(record)


class ProxyLoggingHandler(ProxyLoggingFilterer, logging.Handler):
    def __init__(self, underlying: logging.Handler) -> None:  # noqa
        ProxyLoggingFilterer.__init__(self, underlying)

    _underlying: logging.Handler

    @property
    def underlying(self) -> logging.Handler:
        return self._underlying

    def get_name(self):
        return self._underlying.get_name()

    def set_name(self, name):
        self._underlying.set_name(name)

    @property
    def name(self):  # type: ignore[override]
        return self._underlying.name

    @property
    def level(self):
        return self._underlying.level

    @level.setter
    def level(self, level):
        self._underlying.level = level

    @property
    def formatter(self):
        return self._underlying.formatter

    @formatter.setter
    def formatter(self, formatter):
        self._underlying.formatter = formatter

    def createLock(self):
        self._underlying.createLock()

    def acquire(self):
        self._underlying.acquire()

    def release(self):
        self._underlying.release()

    def setLevel(self, level):
        self._underlying.setLevel(level)

    def format(self, record):
        return self._underlying.format(record)

    def emit(self, record):
        self._underlying.emit(record)

    def handle(self, record):
        return self._underlying.handle(record)

    def setFormatter(self, fmt):
        self._underlying.setFormatter(fmt)

    def flush(self):
        self._underlying.flush()

    def close(self):
        self._underlying.close()

    def handleError(self, record):
        self._underlying.handleError(record)


########################################
# ../../../omlish/logs/warnings.py


##


class LoggingSetupWarning(Warning):
    pass


########################################
# ../../../omlish/os/files.py


##


def is_fd_open(fd: int) -> bool:
    try:
        fcntl.fcntl(fd, fcntl.F_GETFD)
    except OSError as e:
        if e.errno == errno.EBADF:
            return False
        raise
    else:
        return True


def touch(path: str, mode: int = 0o666, exist_ok: bool = True) -> None:
    if exist_ok:
        # First try to bump modification time
        # Implementation note: GNU touch uses the UTIME_NOW option of the utimensat() / futimens() functions.
        try:
            os.utime(path, None)
        except OSError:
            pass
        else:
            return

    flags = os.O_CREAT | os.O_WRONLY
    if not exist_ok:
        flags |= os.O_EXCL

    fd = os.open(path, flags, mode)
    os.close(fd)


def unlink_if_exists(path: str) -> None:
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


@contextlib.contextmanager
def unlinking_if_exists(path: str) -> ta.Iterator[None]:
    try:
        yield
    finally:
        unlink_if_exists(path)


########################################
# ../../../omlish/os/paths.py


##


@ta.overload
def path_dirname(p: str, n: int = 1) -> str:
    ...


@ta.overload
def path_dirname(p: bytes, n: int = 1) -> bytes:
    ...


def path_dirname(p, n=1):
    if isinstance(p, bytes):
        sep: ta.Any = b'/'
    else:
        sep = '/'
    p = os.fspath(p)
    i = -1
    for _ in range(n):
        i = p.rindex(sep, 0, i)
    head = p[:i + 1]
    if head and head != sep * len(head):
        head = head.rstrip(sep)
    return head


def abs_real_path(p: str) -> str:
    return os.path.abspath(os.path.realpath(p))


def is_path_in_dir(base_dir: str, target_path: str) -> bool:
    base_dir = abs_real_path(base_dir)
    target_path = abs_real_path(target_path)

    return target_path.startswith(base_dir + os.path.sep)


def relative_symlink(
        src: str,
        dst: str,
        *,
        target_is_directory: bool = False,
        dir_fd: ta.Optional[int] = None,
        make_dirs: bool = False,
        **kwargs: ta.Any,
) -> None:
    if make_dirs:
        os.makedirs(os.path.dirname(dst), exist_ok=True)

    os.symlink(
        os.path.relpath(src, os.path.dirname(dst)),
        dst,
        target_is_directory=target_is_directory,
        dir_fd=dir_fd,
        **kwargs,
    )


########################################
# ../../../omlish/secrets/ssl.py


##


@dc.dataclass(frozen=True)
class SslCert:
    key_file: str
    cert_file: str


########################################
# ../../../omlish/sockets/addresses.py
"""
TODO:
 - codification of https://docs.python.org/3/library/socket.html#socket-families
"""


##


@dc.dataclass(frozen=True)
class SocketAddressInfoArgs:
    host: ta.Optional[str]
    port: ta.Union[str, int, None]
    family: socket_.AddressFamily = socket_.AddressFamily.AF_UNSPEC
    type: int = 0
    proto: int = 0
    flags: socket_.AddressInfo = socket_.AddressInfo(0)


@dc.dataclass(frozen=True)
class SocketAddressInfo:
    family: socket_.AddressFamily
    type: int
    proto: int
    canonname: ta.Optional[str]
    sockaddr: SocketAddress


class SocketFamilyAndAddress(ta.NamedTuple):
    family: socket_.AddressFamily
    address: SocketAddress


def get_best_socket_family(
        host: ta.Optional[str],
        port: ta.Union[str, int, None],
        family: ta.Union[int, socket_.AddressFamily] = socket_.AddressFamily.AF_UNSPEC,
) -> SocketFamilyAndAddress:
    """https://github.com/python/cpython/commit/f289084c83190cc72db4a70c58f007ec62e75247"""

    infos = socket_.getaddrinfo(
        host,
        port,
        family,
        type=socket_.SOCK_STREAM,
        flags=socket_.AI_PASSIVE,
    )
    ai = SocketAddressInfo(*next(iter(infos)))
    return SocketFamilyAndAddress(ai.family, ai.sockaddr)


class SocketAndAddress(ta.NamedTuple):
    socket: socket_.socket
    address: SocketAddress

    def wrap_socket(self, fn: ta.Callable[[socket_.socket], socket_.socket]):
        return self._replace(socket=fn(self.socket))

    @classmethod
    def socket_wrapper(
            cls,
            fn: ta.Callable[[socket_.socket], socket_.socket],
    ) -> ta.Callable[['SocketAndAddress'], 'SocketAndAddress']:
        def inner(conn):
            return conn.wrap_socket(fn)
        return inner


########################################
# ../../../omlish/sockets/io.py


##


class SocketWriter(io.BufferedIOBase):
    """
    Simple writable BufferedIOBase implementation for a socket

    Does not hold data in a buffer, avoiding any need to call flush().
    """

    def __init__(self, sock):
        super().__init__()

        self._sock = sock

    def writable(self):
        return True

    def write(self, b):
        self._sock.sendall(b)
        with memoryview(b) as view:
            return view.nbytes

    def fileno(self):
        return self._sock.fileno()


class SocketIoPair(ta.NamedTuple):
    r: ta.BinaryIO
    w: ta.BinaryIO

    @classmethod
    def from_socket(
            cls,
            sock: socket.socket,
            *,
            r_buf_size: int = -1,
            w_buf_size: int = 0,
    ) -> 'SocketIoPair':
        rf: ta.Any = sock.makefile('rb', r_buf_size)

        if w_buf_size:
            wf: ta.Any = SocketWriter(sock)
        else:
            wf = sock.makefile('wb', w_buf_size)

        return cls(rf, wf)


##


def close_socket_immediately(sock: socket.socket) -> None:
    try:
        # Explicitly shutdown. socket.close() merely releases the socket and waits for GC to perform the actual close.
        sock.shutdown(socket.SHUT_WR)

    except OSError:
        # Some platforms may raise ENOTCONN here
        pass

    sock.close()


########################################
# ../github/api/v1/api.py
"""
export FILE_SIZE=$(stat --format="%s" $FILE)

export CACHE_ID=$(curl -s \
  -X POST \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/caches" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json;api-version=6.0-preview.1' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"key": "'"$CACHE_KEY"'", "cacheSize": '"$FILE_SIZE"'}' \
  | jq .cacheId)

curl -s \
  -X PATCH \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/caches/$CACHE_ID" \
  -H 'Content-Type: application/octet-stream' \
  -H 'Accept: application/json;api-version=6.0-preview.1' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -H "Content-Range: bytes 0-$((FILE_SIZE - 1))/*" \
  --data-binary @"$FILE"

curl -s \
  -X POST \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/caches/$CACHE_ID" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json;api-version=6.0-preview.1' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"size": '"$(stat --format="%s" $FILE)"'}'

curl -s \
  -X GET \
  "${ACTIONS_CACHE_URL}_apis/artifactcache/cache?keys=$CACHE_KEY" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  | jq .
"""


##


class GithubCacheServiceV1:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    API_VERSION = '6.0-preview.1'

    @classmethod
    def get_service_url(cls, base_url: str) -> str:
        return f'{base_url.rstrip("/")}/_apis/artifactcache'

    #

    @classmethod
    def dataclass_to_json(cls, obj: ta.Any) -> ta.Any:
        return {
            camel_case(k, lower=True): v
            for k, v in dc.asdict(obj).items()
            if v is not None
        }

    @classmethod
    def dataclass_from_json(cls, dcls: ta.Type[T], obj: ta.Any) -> T:
        return dcls(**{
            snake_case(k): v
            for k, v in obj.items()
        })

    #

    @dc.dataclass(frozen=True)
    class ArtifactCacheEntry:
        cache_key: ta.Optional[str]
        scope: ta.Optional[str]
        cache_version: ta.Optional[str]
        creation_time: ta.Optional[str]
        archive_location: ta.Optional[str]

    @dc.dataclass(frozen=True)
    class ArtifactCacheList:
        total_count: int
        artifact_caches: ta.Optional[ta.Sequence['GithubCacheServiceV1.ArtifactCacheEntry']]

    #

    @dc.dataclass(frozen=True)
    class ReserveCacheRequest:
        key: str
        cache_size: ta.Optional[int] = None
        version: ta.Optional[str] = None

    @dc.dataclass(frozen=True)
    class ReserveCacheResponse:
        cache_id: int

    #

    @dc.dataclass(frozen=True)
    class CommitCacheRequest:
        size: int

    #

    class CompressionMethod:
        GZIP = 'gzip'
        ZSTD_WITHOUT_LONG = 'zstd-without-long'
        ZSTD = 'zstd'

    @dc.dataclass(frozen=True)
    class InternalCacheOptions:
        compression_method: ta.Optional[str]  # CompressionMethod
        enable_cross_os_archive: ta.Optional[bool]
        cache_size: ta.Optional[int]


########################################
# ../github/api/v2/api.py
"""
https://github.com/tonistiigi/go-actions-cache/blob/3e9a6642607fd6e4d5d4fdab7c91fe8bf4c36a25/cache_v2.go

==

curl -s \
  -X POST \
  "${ACTIONS_RESULTS_URL}twirp/github.actions.results.api.v1.CacheService/CreateCacheEntry" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"key": "foo", "version": "0000000000000000000000000000000000000000000000000000000000000001" }' \
  | jq .

curl -s \
  -X POST \
  "${ACTIONS_RESULTS_URL}twirp/github.actions.results.api.v1.CacheService/GetCacheEntryDownloadURL" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACTIONS_RUNTIME_TOKEN" \
  -d '{"key": "foo", "restoreKeys": [], "version": "0000000000000000000000000000000000000000000000000000000000000001" }' \
  | jq .

"""  # noqa


##


class GithubCacheServiceV2:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    SERVICE_NAME = 'github.actions.results.api.v1.CacheService'

    @classmethod
    def get_service_url(cls, base_url: str) -> str:
        return f'{base_url.rstrip("/")}/twirp/{cls.SERVICE_NAME}'

    #

    @dc.dataclass(frozen=True)
    class Method(ta.Generic[GithubCacheServiceV2RequestT, GithubCacheServiceV2ResponseT]):
        name: str
        request: ta.Type[GithubCacheServiceV2RequestT]
        response: ta.Type[GithubCacheServiceV2ResponseT]

    #

    class CacheScopePermission:
        READ = 1
        WRITE = 2
        ALL = READ | WRITE

    @dc.dataclass(frozen=True)
    class CacheScope:
        scope: str
        permission: int  # CacheScopePermission

    @dc.dataclass(frozen=True)
    class CacheMetadata:
        repository_id: int
        scope: ta.Sequence['GithubCacheServiceV2.CacheScope']

    VERSION_LENGTH: int = 64

    #

    @dc.dataclass(frozen=True)
    class CreateCacheEntryRequest:
        key: str
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

        def __post_init__(self) -> None:
            check.equal(len(self.version), GithubCacheServiceV2.VERSION_LENGTH)

    @dc.dataclass(frozen=True)
    class CreateCacheEntryResponse:
        ok: bool
        signed_upload_url: str
        message: ta.Optional[str] = None

    CREATE_CACHE_ENTRY_METHOD: Method[
        CreateCacheEntryRequest,
        CreateCacheEntryResponse,
    ] = Method(
        'CreateCacheEntry',
        CreateCacheEntryRequest,
        CreateCacheEntryResponse,
    )

    #

    @dc.dataclass(frozen=True)
    class FinalizeCacheEntryUploadRequest:
        key: str
        size_bytes: int
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

    @dc.dataclass(frozen=True)
    class FinalizeCacheEntryUploadResponse:
        ok: bool
        entry_id: str
        message: ta.Optional[str] = None

    FINALIZE_CACHE_ENTRY_METHOD: Method[
        FinalizeCacheEntryUploadRequest,
        FinalizeCacheEntryUploadResponse,
    ] = Method(
        'FinalizeCacheEntryUpload',
        FinalizeCacheEntryUploadRequest,
        FinalizeCacheEntryUploadResponse,
    )

    #

    @dc.dataclass(frozen=True)
    class GetCacheEntryDownloadUrlRequest:
        key: str
        restore_keys: ta.Sequence[str]
        version: str
        metadata: ta.Optional['GithubCacheServiceV2.CacheMetadata'] = None

    @dc.dataclass(frozen=True)
    class GetCacheEntryDownloadUrlResponse:
        ok: bool
        signed_download_url: str
        matched_key: str

    GET_CACHE_ENTRY_DOWNLOAD_URL_METHOD: Method[
        GetCacheEntryDownloadUrlRequest,
        GetCacheEntryDownloadUrlResponse,
    ] = Method(
        'GetCacheEntryDownloadURL',
        GetCacheEntryDownloadUrlRequest,
        GetCacheEntryDownloadUrlResponse,
    )


########################################
# ../github/bootstrap.py
"""
sudo rm -rf \
    /usr/local/.ghcup \
    /opt/hostedtoolcache \

/usr/local/.ghcup       6.4G, 3391250 files
/opt/hostedtoolcache    8.0G, 14843980 files
/usr/local/lib/android  6.4G, 17251667 files
"""


##


GITHUB_ACTIONS_ENV_VAR = register_github_env_var('GITHUB_ACTIONS')


def is_in_github_actions() -> bool:
    return GITHUB_ACTIONS_ENV_VAR() is not None


########################################
# ../../oci/datarefs.py


##


@dc.dataclass(frozen=True)
class OciDataRef(Abstract):
    pass


@dc.dataclass(frozen=True)
class BytesOciDataRef(OciDataRef):
    data: bytes


@dc.dataclass(frozen=True)
class FileOciDataRef(OciDataRef):
    path: str


@dc.dataclass(frozen=True)
class TarFileOciDataRef(OciDataRef):
    tar_file: tarfile.TarFile
    tar_info: tarfile.TarInfo


##


@functools.singledispatch
def write_oci_data_ref_to_file(
        src_data: OciDataRef,
        dst_file: str,
        *,
        symlink: bool = False,  # noqa
        chunk_size: int = 1024 * 1024,
) -> None:
    with open_oci_data_ref(src_data) as f_src:
        with open(dst_file, 'wb') as f_dst:
            shutil.copyfileobj(f_src, f_dst, length=chunk_size)  # noqa


@write_oci_data_ref_to_file.register
def _(
        src_data: FileOciDataRef,
        dst_file: str,
        *,
        symlink: bool = False,
        **kwargs: ta.Any,
) -> None:
    if symlink:
        os.symlink(
            os.path.relpath(src_data.path, os.path.dirname(dst_file)),
            dst_file,
        )
    else:
        shutil.copyfile(src_data.path, dst_file)


#


@functools.singledispatch
def open_oci_data_ref(data: OciDataRef) -> ta.BinaryIO:
    raise TypeError(data)


@open_oci_data_ref.register
def _(data: FileOciDataRef) -> ta.BinaryIO:
    return open(data.path, 'rb')


@open_oci_data_ref.register
def _(data: BytesOciDataRef) -> ta.BinaryIO:
    return io.BytesIO(data.data)


@open_oci_data_ref.register
def _(data: TarFileOciDataRef) -> ta.BinaryIO:
    return check.not_none(data.tar_file.extractfile(data.tar_info))  # type: ignore[return-value]


#


@functools.singledispatch
def get_oci_data_ref_size(data: OciDataRef) -> int:
    raise TypeError(data)


@get_oci_data_ref_size.register
def _(data: FileOciDataRef) -> int:
    return os.path.getsize(data.path)


@get_oci_data_ref_size.register
def _(data: BytesOciDataRef) -> int:
    return len(data.data)


@get_oci_data_ref_size.register
def _(data: TarFileOciDataRef) -> int:
    return data.tar_info.size


##


@dc.dataclass(frozen=True)
class OciDataRefInfo:
    data: OciDataRef

    @cached_nullary
    def sha256(self) -> str:
        with open_oci_data_ref(self.data) as f:
            return hashlib.file_digest(f, 'sha256').hexdigest()  # type: ignore[arg-type]

    @cached_nullary
    def digest(self) -> str:
        return f'sha256:{self.sha256()}'

    @cached_nullary
    def size(self) -> int:
        return get_oci_data_ref_size(self.data)


########################################
# ../../oci/pack/unpacking.py


##


class OciLayerUnpacker(ExitStacked):
    def __init__(
            self,
            input_files: ta.Sequence[ta.Union[str, tarfile.TarFile]],
            output_file_path: str,
    ) -> None:
        super().__init__()

        self._input_files = list(input_files)
        self._output_file_path = output_file_path

    #

    @contextlib.contextmanager
    def _open_input_file(self, input_file: ta.Union[str, tarfile.TarFile]) -> ta.Iterator[tarfile.TarFile]:
        if isinstance(input_file, tarfile.TarFile):
            yield input_file

        elif isinstance(input_file, str):
            with tarfile.open(input_file) as tar_file:
                yield tar_file

        else:
            raise TypeError(input_file)

    #

    class _Entry(ta.NamedTuple):
        file: ta.Union[str, tarfile.TarFile]
        info: tarfile.TarInfo

    def _build_input_file_sorted_entries(self, input_file: ta.Union[str, tarfile.TarFile]) -> ta.Sequence[_Entry]:
        dct: ta.Dict[str, OciLayerUnpacker._Entry] = {}

        with self._open_input_file(input_file) as input_tar_file:
            for info in input_tar_file.getmembers():
                check.not_in(info.name, dct)
                dct[info.name] = self._Entry(
                    file=input_file,
                    info=info,
                )

        return sorted(dct.values(), key=lambda entry: entry.info.name)

    @cached_nullary
    def _entries_by_name(self) -> ta.Mapping[str, _Entry]:
        root: dict = {}

        def find_dir(dir_name: str) -> dict:  # noqa
            if dir_name:
                dir_parts = dir_name.split('/')
            else:
                dir_parts = []

            cur = root  # noqa
            for dir_part in dir_parts:
                cur = cur[dir_part]  # noqa

            return check.isinstance(cur, dict)

        #

        for input_file in self._input_files:
            sorted_entries = self._build_input_file_sorted_entries(input_file)

            wh_names = set()
            wh_opaques = set()

            #

            for entry in sorted_entries:
                info = entry.info
                name = check.non_empty_str(info.name)
                base_name = os.path.basename(name)
                dir_name = os.path.dirname(name)

                if base_name == '.wh..wh..opq':
                    wh_opaques.add(dir_name)
                    continue

                if base_name.startswith('.wh.'):
                    wh_base_name = os.path.basename(base_name[4:])
                    wh_name = os.path.join(dir_name, wh_base_name)
                    wh_names.add(wh_name)
                    continue

                cur = find_dir(dir_name)

                if info.type == tarfile.DIRTYPE:
                    try:
                        ex = cur[base_name]
                    except KeyError:
                        cur[base_name] = {'': entry}
                    else:
                        ex[''] = entry

                else:
                    cur[base_name] = entry

            #

            for wh_name in reversed(sorted(wh_names)):  # noqa
                wh_dir_name = os.path.dirname(wh_name)
                wh_base_name = os.path.basename(wh_name)

                cur = find_dir(wh_dir_name)
                rm = cur[wh_base_name]

                if isinstance(rm, dict):
                    # Whiteouts wipe out whole directory:
                    # https://github.com/containerd/containerd/blob/59c8cf6ea5f4175ad512914dd5ce554942bf144f/pkg/archive/tar_test.go#L648
                    # check.equal(set(rm), '')
                    del cur[wh_base_name]

                elif isinstance(rm, self._Entry):
                    del cur[wh_base_name]

                else:
                    raise TypeError(rm)

            if wh_opaques:
                raise NotImplementedError

        #

        out: ta.Dict[str, OciLayerUnpacker._Entry] = {}

        def rec(cur):  # noqa
            for _, child in sorted(cur.items(), key=lambda t: t[0]):
                if isinstance(child, dict):
                    rec(child)

                elif isinstance(child, self._Entry):
                    check.not_in(child.info.name, out)
                    out[child.info.name] = child

                else:
                    raise TypeError(child)

        rec(root)

        return out

    #

    @cached_nullary
    def _output_tar_file(self) -> tarfile.TarFile:
        return self._enter_context(tarfile.open(self._output_file_path, 'w'))

    #

    def _add_unpacked_entry(
            self,
            input_tar_file: tarfile.TarFile,
            info: tarfile.TarInfo,
    ) -> None:
        base_name = os.path.basename(info.name)
        check.state(not base_name.startswith('.wh.'))

        if info.type in tarfile.REGULAR_TYPES:
            with check.not_none(input_tar_file.extractfile(info)) as f:
                self._output_tar_file().addfile(info, f)

        else:
            self._output_tar_file().addfile(info)

    def _unpack_file(
            self,
            input_file: ta.Union[str, tarfile.TarFile],
    ) -> None:
        entries_by_name = self._entries_by_name()

        with self._open_input_file(input_file) as input_tar_file:
            info: tarfile.TarInfo
            for info in input_tar_file.getmembers():
                try:
                    entry = entries_by_name[info.name]
                except KeyError:
                    continue

                if entry.file != input_file:
                    continue

                self._add_unpacked_entry(input_tar_file, info)

    @cached_nullary
    def write(self) -> None:
        for input_file in self._input_files:
            self._unpack_file(input_file)


########################################
# ../../../omlish/argparse/cli.py
"""
FIXME:
 - exit_on_error lol

TODO:
 - default command
 - auto match all underscores to hyphens
 - pre-run, post-run hooks
 - exitstack?
 - suggestion - difflib.get_close_matches
 - add_argument_group - group kw on ArgparseKwarg?
"""


##


@dc.dataclass(eq=False)
class ArgparseArg:
    args: ta.Sequence[ta.Any]
    kwargs: ta.Mapping[str, ta.Any]
    group: ta.Optional[str] = None
    dest: ta.Optional[str] = None

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance.args, self.dest)  # type: ignore


def argparse_arg(*args, **kwargs) -> ArgparseArg:
    return ArgparseArg(
        args=args,
        group=kwargs.pop('group', None),
        kwargs=kwargs,
    )


def argparse_arg_(*args, **kwargs) -> ta.Any:
    return argparse_arg(*args, **kwargs)


#


@dc.dataclass(eq=False)
class ArgparseCmd:
    name: str
    fn: ArgparseCmdFn
    args: ta.Sequence[ArgparseArg] = ()  # noqa

    # _: dc.KW_ONLY

    aliases: ta.Optional[ta.Sequence[str]] = None
    parent: ta.Optional['ArgparseCmd'] = None
    accepts_unknown: bool = False

    def __post_init__(self) -> None:
        def check_name(s: str) -> None:
            check.isinstance(s, str)
            check.not_in('_', s)
            check.not_empty(s)
        check_name(self.name)
        check.not_isinstance(self.aliases, str)
        for a in self.aliases or []:
            check_name(a)

        check.arg(callable(self.fn))
        check.arg(all(isinstance(a, ArgparseArg) for a in self.args))
        check.isinstance(self.parent, (ArgparseCmd, type(None)))
        check.isinstance(self.accepts_unknown, bool)

        functools.update_wrapper(self, self.fn)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return dc.replace(self, fn=self.fn.__get__(instance, owner))  # noqa

    def __call__(self, *args, **kwargs) -> ta.Optional[int]:
        return self.fn(*args, **kwargs)


def argparse_cmd(
        *args: ArgparseArg,
        name: ta.Optional[str] = None,
        aliases: ta.Optional[ta.Iterable[str]] = None,
        parent: ta.Optional[ArgparseCmd] = None,
        accepts_unknown: bool = False,
) -> ta.Any:  # ta.Callable[[ArgparseCmdFn], ArgparseCmd]:  # FIXME
    for arg in args:
        check.isinstance(arg, ArgparseArg)
    check.isinstance(name, (str, type(None)))
    check.isinstance(parent, (ArgparseCmd, type(None)))
    check.not_isinstance(aliases, str)

    def inner(fn):
        return ArgparseCmd(
            (name if name is not None else fn.__name__).replace('_', '-'),
            fn,
            args,
            aliases=tuple(aliases) if aliases is not None else None,
            parent=parent,
            accepts_unknown=accepts_unknown,
        )

    return inner


##


def _get_argparse_arg_ann_kwargs(ann: ta.Any) -> ta.Mapping[str, ta.Any]:
    if ann is str:
        return {}
    elif ann is int:
        return {'type': int}
    elif ann is bool:
        return {'action': 'store_true'}
    elif ann is list:
        return {'action': 'append'}
    elif is_optional_alias(ann):
        return _get_argparse_arg_ann_kwargs(get_optional_alias_arg(ann))
    else:
        raise TypeError(ann)


class _ArgparseCliAnnotationBox:
    def __init__(self, annotations: ta.Mapping[str, ta.Any]) -> None:
        super().__init__()

        self.__annotations__ = annotations  # type: ignore


class ArgparseCli:
    def __init__(self, argv: ta.Optional[ta.Sequence[str]] = None) -> None:
        super().__init__()

        self._argv = argv if argv is not None else sys.argv[1:]

        self._args, self._unknown_args = self.get_parser().parse_known_args(self._argv)

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        ns = cls.__dict__
        objs = {}
        mro = cls.__mro__[::-1]
        for bns in [bcls.__dict__ for bcls in reversed(mro)] + [ns]:
            bseen = set()  # type: ignore
            for k, v in bns.items():
                if isinstance(v, (ArgparseCmd, ArgparseArg)):
                    check.not_in(v, bseen)
                    bseen.add(v)
                    objs[k] = v
                elif k in objs:
                    del [k]

        #

        anns = ta.get_type_hints(_ArgparseCliAnnotationBox({
            **{k: v for bcls in reversed(mro) for k, v in getattr(bcls, '__annotations__', {}).items()},
            **ns.get('__annotations__', {}),
        }), globalns=ns.get('__globals__', {}))

        #

        if '_parser' in ns:
            parser = check.isinstance(ns['_parser'], argparse.ArgumentParser)
        else:
            parser = argparse.ArgumentParser()
            setattr(cls, '_parser', parser)

        #

        subparsers = parser.add_subparsers()

        for att, obj in objs.items():
            if isinstance(obj, ArgparseCmd):
                if obj.parent is not None:
                    raise NotImplementedError

                for cn in [obj.name, *(obj.aliases or [])]:
                    subparser = subparsers.add_parser(cn)

                    for arg in (obj.args or []):
                        if (
                                len(arg.args) == 1 and
                                isinstance(arg.args[0], str) and
                                not (n := check.isinstance(arg.args[0], str)).startswith('-') and
                                'metavar' not in arg.kwargs
                        ):
                            subparser.add_argument(
                                n.replace('-', '_'),
                                **arg.kwargs,
                                metavar=n,
                            )
                        else:
                            subparser.add_argument(*arg.args, **arg.kwargs)

                    subparser.set_defaults(_cmd=obj)

            elif isinstance(obj, ArgparseArg):
                if obj.group is not None:
                    # FIXME: add_argument_group
                    raise NotImplementedError

                if att in anns:
                    ann_kwargs = _get_argparse_arg_ann_kwargs(anns[att])
                    obj.kwargs = {**ann_kwargs, **obj.kwargs}

                if not obj.dest:
                    if 'dest' in obj.kwargs:
                        obj.dest = obj.kwargs['dest']
                    else:
                        obj.dest = obj.kwargs['dest'] = att  # type: ignore

                parser.add_argument(*obj.args, **obj.kwargs)

            else:
                raise TypeError(obj)

    #

    _parser: ta.ClassVar[argparse.ArgumentParser]

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        return cls._parser

    @property
    def argv(self) -> ta.Sequence[str]:
        return self._argv

    @property
    def args(self) -> argparse.Namespace:
        return self._args

    @property
    def unknown_args(self) -> ta.Sequence[str]:
        return self._unknown_args

    #

    def _bind_cli_cmd(self, cmd: ArgparseCmd) -> ta.Callable:
        return cmd.__get__(self, type(self))

    def prepare_cli_run(self) -> ta.Optional[ta.Callable]:
        cmd = getattr(self.args, '_cmd', None)

        if self._unknown_args and not (cmd is not None and cmd.accepts_unknown):
            msg = f'unrecognized arguments: {" ".join(self._unknown_args)}'
            if (parser := self.get_parser()).exit_on_error:  # noqa
                parser.error(msg)
            else:
                raise argparse.ArgumentError(None, msg)

        if cmd is None:
            self.get_parser().print_help()
            return None

        return self._bind_cli_cmd(cmd)

    #

    def cli_run(self) -> ta.Optional[int]:
        if (fn := self.prepare_cli_run()) is None:
            return 0

        return fn()

    def cli_run_and_exit(self) -> ta.NoReturn:
        rc = self.cli_run()
        if not isinstance(rc, int):
            rc = 0
        raise SystemExit(rc)

    def __call__(self, *, exit: bool = False) -> ta.Optional[int]:  # noqa
        if exit:
            return self.cli_run_and_exit()
        else:
            return self.cli_run()

    #

    async def async_cli_run(
            self,
            *,
            force_async: bool = False,
    ) -> ta.Optional[int]:
        if (fn := self.prepare_cli_run()) is None:
            return 0

        if force_async:
            is_async = True
        else:
            tfn = fn
            if isinstance(tfn, ArgparseCmd):
                tfn = tfn.fn
            is_async = inspect.iscoroutinefunction(tfn)

        if is_async:
            return await fn()
        else:
            return fn()


########################################
# ../../../omlish/formats/yaml/goyaml/errors.py


##


class YamlError(Exception, Abstract):
    @property
    @abc.abstractmethod
    def message(self) -> str:
        raise NotImplementedError


class EofYamlError(YamlError):
    @property
    def message(self) -> str:
        return 'eof'


@dc.dataclass()
class GenericYamlError(YamlError):
    obj: ta.Union[str, Exception]

    @property
    def message(self) -> str:
        if isinstance(self.obj, str):
            return self.obj
        else:
            return str(self.obj)


def yaml_error(obj: ta.Union[YamlError, str, Exception]) -> YamlError:
    if isinstance(obj, YamlError):
        return obj
    elif isinstance(obj, (str, Exception)):
        return GenericYamlError(obj)
    else:
        raise TypeError(obj)


########################################
# ../../../omlish/http/coro/io.py


##


class CoroHttpIo:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    def __init_subclass__(cls, **kwargs):  # noqa
        raise TypeError

    #

    MAX_LINE: ta.ClassVar[int] = 65536

    #

    class Io(Abstract):
        pass

    #

    class AnyLogIo(Io, Abstract):
        pass

    #

    @dc.dataclass(frozen=True)
    class ConnectIo(Io):
        args: ta.Tuple[ta.Any, ...]
        kwargs: ta.Optional[ta.Dict[str, ta.Any]] = None

        server_hostname: ta.Optional[str] = None

    #

    class CloseIo(Io):
        pass

    #

    class AnyReadIo(Io):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class ReadIo(AnyReadIo):
        sz: ta.Optional[int]

    @dc.dataclass(frozen=True)
    class ReadLineIo(AnyReadIo):
        sz: int

    @dc.dataclass(frozen=True)
    class ReadUntilIo(AnyReadIo):
        b: bytes
        sz: ta.Optional[int] = None

    @dc.dataclass(frozen=True)
    class PeekIo(AnyReadIo):
        sz: int

    #

    @dc.dataclass(frozen=True)
    class WriteIo(Io):
        data: bytes


########################################
# ../../../omlish/http/parsing.py
"""
Parses a complete HTTP/1.x start-line + header fields + final CRLF from a ``bytes`` object. Does NOT handle message
bodies, chunked transfer decoding, trailers, or HTTP/2+.

TODO:
 - mapping from error code to outbound http status code
"""


##


class StartLineHttpParseErrorCode(enum.Enum):
    MALFORMED_REQUEST_LINE = enum.auto()
    MALFORMED_STATUS_LINE = enum.auto()
    UNSUPPORTED_HTTP_VERSION = enum.auto()
    INVALID_METHOD = enum.auto()
    INVALID_REQUEST_TARGET = enum.auto()
    INVALID_STATUS_CODE = enum.auto()


class HeaderFieldHttpParseErrorCode(enum.Enum):
    INVALID_FIELD_NAME = enum.auto()
    INVALID_FIELD_VALUE = enum.auto()
    OBS_FOLD_NOT_ALLOWED = enum.auto()
    SPACE_BEFORE_COLON = enum.auto()
    MISSING_COLON = enum.auto()
    BARE_CARRIAGE_RETURN = enum.auto()
    BARE_LF = enum.auto()
    NUL_IN_HEADER = enum.auto()
    MISSING_TERMINATOR = enum.auto()
    TRAILING_DATA = enum.auto()
    TOO_MANY_HEADERS = enum.auto()
    EMPTY_FIELD_NAME = enum.auto()


class SemanticHeaderHttpParseErrorCode(enum.Enum):
    DUPLICATE_CONTENT_LENGTH = enum.auto()
    CONFLICTING_CONTENT_LENGTH = enum.auto()
    CONTENT_LENGTH_WITH_TRANSFER_ENCODING = enum.auto()
    MISSING_HOST_HEADER = enum.auto()
    MULTIPLE_HOST_HEADERS = enum.auto()
    CONFLICTING_HOST_HEADERS = enum.auto()
    INVALID_CONTENT_LENGTH = enum.auto()
    INVALID_TRANSFER_ENCODING = enum.auto()
    INVALID_CONTENT_TYPE = enum.auto()
    FORBIDDEN_TRAILER_FIELD = enum.auto()
    INVALID_HOST = enum.auto()
    INVALID_EXPECT = enum.auto()
    INVALID_DATE = enum.auto()
    INVALID_CACHE_CONTROL = enum.auto()
    INVALID_ACCEPT_ENCODING = enum.auto()
    INVALID_ACCEPT = enum.auto()
    INVALID_AUTHORIZATION = enum.auto()
    TE_WITHOUT_CHUNKED_LAST = enum.auto()
    TE_IN_HTTP10 = enum.auto()


class EncodingHttpParseErrorCode(enum.Enum):
    NON_ASCII_IN_FIELD_NAME = enum.auto()
    OBS_TEXT_IN_FIELD_VALUE = enum.auto()


HttpParseErrorCode = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    StartLineHttpParseErrorCode,
    HeaderFieldHttpParseErrorCode,
    SemanticHeaderHttpParseErrorCode,
    EncodingHttpParseErrorCode,
]


##


class HttpParseError(Exception):
    pass


@dc.dataclass()
class ErrorCodeHttpParseError(HttpParseError):
    """Base exception for all HTTP header parsing errors."""

    code: HttpParseErrorCode
    message: str = ''
    line: int = 0
    offset: int = 0

    def __post_init__(self) -> None:
        Exception.__init__(self, str(self))

    def __str__(self) -> str:
        return f'[{self.code.name}] line {self.line}, offset {self.offset}: {self.message}'


@dc.dataclass()
class StartLineHttpParseError(ErrorCodeHttpParseError):
    """Errors in the request-line or status-line."""

    code: StartLineHttpParseErrorCode = dc.field(default=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE)


@dc.dataclass()
class HeaderFieldHttpParseError(ErrorCodeHttpParseError):
    """Errors in header field syntax."""

    code: HeaderFieldHttpParseErrorCode = dc.field(default=HeaderFieldHttpParseErrorCode.INVALID_FIELD_NAME)


@dc.dataclass()
class SemanticHeaderHttpParseError(ErrorCodeHttpParseError):
    """Errors in header field semantics / cross-field validation."""

    code: SemanticHeaderHttpParseErrorCode = dc.field(default=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH)


@dc.dataclass()
class EncodingHttpParseError(ErrorCodeHttpParseError):
    """Errors in character encoding within headers."""

    code: EncodingHttpParseErrorCode = dc.field(default=EncodingHttpParseErrorCode.NON_ASCII_IN_FIELD_NAME)


@dc.dataclass()
class NoCombineHeaderHttpParseError(HttpParseError):
    """Errors in headers where duplicate values are not allowed."""

    name: str


##


@ta.final
class ParsedHttpHeaders:
    """
    Normalized, case-insensitive header mapping.

    Field names are stored in lowercase. Values are decoded as Latin-1. Multiple values for the same field-name are
    stored individually and combined with ``", "`` on access (except Set-Cookie, which is never combined).
    """

    def __init__(self) -> None:
        # normalized name -> list of individual values
        self._entries: ta.Dict[str, ta.List[str]] = {}

        # insertion-ordered unique names
        self._order: ta.List[str] = []

    def _add(self, name: str, value: str) -> None:
        if name not in self._entries:
            self._entries[name] = []
            self._order.append(name)
        self._entries[name].append(value)

    @property
    def entries(self) -> ta.Mapping[str, ta.Sequence[str]]:
        return self._entries

    def __contains__(self, name: ta.Any) -> bool:
        if not isinstance(name, str):
            return False
        return name.lower() in self._entries

    # Headers where duplicate values are comma-combined per RFC 7230 §3.2.2. Set-Cookie is the notable exception.
    _NO_COMBINE_HEADERS: ta.ClassVar[ta.FrozenSet[str]] = frozenset({
        'set-cookie',
    })

    def __getitem__(self, name: str) -> str:
        key = name.lower()
        values = self._entries[key]
        if key in self._NO_COMBINE_HEADERS:
            raise NoCombineHeaderHttpParseError(name)
        return ', '.join(values)

    def get(self, name: str, default: ta.Optional[str] = None) -> ta.Optional[str]:
        try:
            return self[name]
        except KeyError:
            return default

    def get_all(self, name: str) -> ta.List[str]:
        return list(self._entries.get(name.lower(), []))

    def items(self) -> ta.List[ta.Tuple[str, str]]:
        result: ta.List[ta.Tuple[str, str]] = []
        for name in self._order:
            values = self._entries[name]
            if name in self._NO_COMBINE_HEADERS:
                for v in values:
                    result.append((name, v))
            else:
                result.append((name, ', '.join(values)))
        return result

    def keys(self) -> ta.List[str]:
        return list(self._order)

    def __iter__(self) -> ta.Iterator[str]:
        return iter(self._order)

    def __len__(self) -> int:
        return len(self._order)

    def __repr__(self) -> str:
        return f'ParsedHttpHeaders({dict(self.items())})'


@dc.dataclass()
class PreparedParsedHttpHeaders:
    content_length: ta.Optional[int] = None

    transfer_encoding: ta.Optional[ta.List[str]] = None

    host: ta.Optional[str] = None

    connection: ta.Optional[ta.FrozenSet[str]] = None
    keep_alive: ta.Optional[bool] = None

    @dc.dataclass(frozen=True)
    class ContentType:
        media_type: str
        params: ta.Dict[str, str]

        @property
        def charset(self) -> ta.Optional[str]:
            return self.params.get('charset')

    content_type: ta.Optional[ContentType] = None

    te: ta.Optional[ta.List[str]] = None

    upgrade: ta.Optional[ta.List[str]] = None

    trailer: ta.Optional[ta.FrozenSet[str]] = None

    expect: ta.Optional[str] = None
    expect_100_continue: ta.Optional[bool] = None

    date: ta.Optional[datetime.datetime] = None

    cache_control: ta.Optional[ta.Dict[str, ta.Optional[str]]] = None

    @dc.dataclass(frozen=True)
    class AcceptEncodingItem:
        coding: str
        q: float = 1.0

    accept_encoding: ta.Optional[ta.List[AcceptEncodingItem]] = None

    @dc.dataclass(frozen=True)
    class AcceptItem:
        media_range: str
        q: float = 1.0
        params: ta.Dict[str, str] = dc.field(default_factory=dict)

    accept: ta.Optional[ta.List[AcceptItem]] = None

    @dc.dataclass(frozen=True)
    class AuthorizationValue:
        scheme: str
        credentials: str

    authorization: ta.Optional[AuthorizationValue] = None

    def __repr__(self) -> str:
        return ''.join([
            f'{self.__class__.__name__}(',
            ', '.join([
                f'{f.name}={v!r}'
                for f in dc.fields(self)
                if (v := getattr(self, f.name) is not None)
            ]),
            ')',
        ])


@dc.dataclass(frozen=True)
class RawParsedHttpHeader:
    name: bytes
    value: bytes

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r}, {self.value!r})'


@dc.dataclass()
class ParsedHttpMessage:
    class Kind(enum.Enum):
        REQUEST = 'request'
        RESPONSE = 'response'

    kind: Kind

    @dc.dataclass(frozen=True)
    class RequestLine:
        method: str
        request_target: bytes
        http_version: HttpVersion

    request_line: ta.Optional[RequestLine]

    @dc.dataclass(frozen=True)
    class StatusLine:
        http_version: HttpVersion
        status_code: int
        reason_phrase: str

    status_line: ta.Optional[StatusLine]

    raw_headers: ta.List[RawParsedHttpHeader]
    headers: ParsedHttpHeaders

    prepared: PreparedParsedHttpHeaders


@dc.dataclass(frozen=True)
class ParsedHttpTrailers:
    """Result of parsing HTTP trailer fields."""

    raw_headers: ta.List[RawParsedHttpHeader]
    headers: ParsedHttpHeaders


##


class HttpParser:
    """Strict HTTP/1.x parser."""

    @dc.dataclass(frozen=True)
    class Config:
        """Strictness knobs. Defaults are maximally strict."""

        allow_obs_fold: bool = False
        allow_space_before_colon: bool = False  # DANGEROUS - upstreams may not handle well
        allow_multiple_content_lengths: bool = False
        allow_content_length_with_te: bool = False
        allow_bare_lf: bool = False
        allow_missing_host: bool = False
        allow_multiple_hosts: bool = False
        allow_unknown_transfer_encoding: bool = False
        allow_empty_header_values: bool = True
        allow_bare_cr_in_value: bool = False
        allow_te_without_chunked_in_response: bool = False
        allow_transfer_encoding_http10: bool = False
        reject_multi_value_content_length: bool = False
        reject_obs_text: bool = False
        reject_non_visible_ascii_request_target: bool = False
        max_header_count: int = 128
        max_header_length: ta.Optional[int] = 8192
        max_content_length_str_len: ta.Optional[int] = None

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

    # Public API

    class Mode(enum.Enum):
        REQUEST = 'request'
        RESPONSE = 'response'
        AUTO = 'auto'

    def parse_message(self, data: bytes, mode: Mode = Mode.AUTO) -> ParsedHttpMessage:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f'Expected bytes, got {type(data).__name__}')

        ctx = _HttpParseContext(
            data=bytes(data),
            config=self._config,
            mode=mode,
        )

        # 1. Verify terminator
        ctx.verify_terminator()

        # 2. Split off start-line
        start_line_end = ctx.find_line_end(0)
        start_line_bytes = data[:start_line_end]

        # 3. Determine message kind
        kind = ctx.detect_kind(start_line_bytes)

        # 4. Parse start-line
        request_line: ta.Optional[ParsedHttpMessage.RequestLine] = None
        status_line: ta.Optional[ParsedHttpMessage.StatusLine] = None
        if kind == ParsedHttpMessage.Kind.REQUEST:
            request_line = ctx.parse_request_line(start_line_bytes)
        else:
            status_line = ctx.parse_status_line(start_line_bytes)

        http_version = (
            request_line.http_version if request_line else
            status_line.http_version if status_line else
            HttpVersions.HTTP_1_1
        )

        # 5. Parse header fields
        # Position after start-line CRLF (or LF if bare LF allowed)
        header_start = start_line_end + ctx.line_ending_len(start_line_end)
        raw_headers = ctx.parse_header_fields(header_start)

        # 6. Build normalized headers
        headers = ParsedHttpHeaders()
        for rh in raw_headers:
            name_str = rh.name.decode('ascii').lower()
            value_str = rh.value.decode('latin-1')
            headers._add(name_str, value_str)  # noqa

        # 7. Build prepared headers
        prepared = ctx.prepare_headers(headers, kind, http_version)

        return ParsedHttpMessage(
            kind=kind,
            request_line=request_line,
            status_line=status_line,
            raw_headers=raw_headers,
            headers=headers,
            prepared=prepared,
        )

    def parse_trailers(
        self,
        data: bytes,
    ) -> ParsedHttpTrailers:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(f'Expected bytes, got {type(data).__name__}')

        # Special case: empty trailers (just the terminating empty line, no fields)
        if data == b'\r\n' or (self._config.allow_bare_lf and data == b'\n'):
            return ParsedHttpTrailers(
                raw_headers=[],
                headers=ParsedHttpHeaders(),
            )

        ctx = _HttpParseContext(
            data=bytes(data),
            config=self._config,
            mode=HttpParser.Mode.AUTO,
        )

        # Verify terminator (trailers end with an empty CRLF line, same as headers)
        ctx.verify_terminator()

        # Parse fields starting at position 0 (no start-line)
        raw_headers = ctx.parse_header_fields(0)

        # Build normalized headers
        headers = ParsedHttpHeaders()
        for rh in raw_headers:
            name_str = rh.name.decode('ascii').lower()
            value_str = rh.value.decode('latin-1')
            headers._add(name_str, value_str)  # noqa

        # Enforce forbidden trailer fields (RFC 7230 §4.1.2)
        for name in headers:
            if name in _HttpParseContext._FORBIDDEN_TRAILER_FIELDS:  # noqa
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.FORBIDDEN_TRAILER_FIELD,
                    message=f'Forbidden field in trailers: {name!r}',
                )

        return ParsedHttpTrailers(
            raw_headers=raw_headers,
            headers=headers,
        )


class _HttpParseContext:
    def __init__(
            self,
            data: bytes,
            config: HttpParser.Config,
            mode: HttpParser.Mode,
    ) -> None:
        super().__init__()

        self.data = data
        self.config = config
        self.mode = mode
        self.current_line = 0  # 0-indexed logical line number

    # Character constants

    # RFC 7230 §3.2.6: token = 1*tchar
    # tchar = "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~" / DIGIT / ALPHA
    _TCHAR_EXTRAS: ta.ClassVar[ta.FrozenSet[int]] = frozenset(b"!#$%&'*+-.^_`|~")

    _TCHAR: ta.ClassVar[ta.FrozenSet[int]] = frozenset(
        set(range(0x30, 0x3A)) |  # DIGIT 0-9
        set(range(0x41, 0x5B)) |  # ALPHA A-Z
        set(range(0x61, 0x7B)) |  # ALPHA a-z
        _TCHAR_EXTRAS,
    )

    # VCHAR = %x21-7E
    _VCHAR: ta.ClassVar[ta.FrozenSet[int]] = frozenset(range(0x21, 0x7F))

    # obs-text = %x80-FF
    _OBS_TEXT: ta.ClassVar[ta.FrozenSet[int]] = frozenset(range(0x80, 0x100))

    _SP = 0x20
    _HTAB = 0x09
    _CR = 0x0D
    _LF = 0x0A
    _COLON = 0x3A
    _NUL = 0x00

    # OWS = *( SP / HTAB )
    _OWS_CHARS: ta.ClassVar[ta.FrozenSet[int]] = frozenset({_SP, _HTAB})

    _CRLF = b'\r\n'
    _CRLFCRLF = b'\r\n\r\n'

    # Allowed characters as raw bytes for translate()
    _TCHAR_BYTES = bytes(sorted(_TCHAR))
    _VCHAR_BYTES = bytes(range(0x21, 0x7F))

    # Terminator verification

    def verify_terminator(self) -> None:
        data = self.data

        idx = data.find(self._CRLFCRLF)
        if idx >= 0:
            after = idx + 4
            if after < len(data):
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.TRAILING_DATA,
                    message=f'Unexpected {len(data) - after} byte(s) after header terminator',
                    line=0,
                    offset=after,
                )
            return

        # Bare-LF mode: require the header block to END with LF LF, not just contain it.
        if self.config.allow_bare_lf:
            if data.endswith(b'\n\n'):
                return
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.MISSING_TERMINATOR,
                message='Header block does not end with LFLF',
                line=0,
                offset=len(data),
            )

        raise HeaderFieldHttpParseError(
            code=HeaderFieldHttpParseErrorCode.MISSING_TERMINATOR,
            message='Header block does not end with CRLFCRLF',
            line=0,
            offset=len(data),
        )

    # Line utilities

    def find_line_end(self, start: int) -> int:
        """
        Find the end of the current line (position of CR before CRLF, or LF if bare-LF allowed). Returns the index of
        the first byte of the line-ending sequence.

        Uses bytes.find() for NUL/CR/LF rather than iterating byte-by-byte in Python. Only loops when a bare CR must be
        skipped (allow_bare_cr_in_value mode).
        """

        data = self.data
        length = len(data)
        pos = start

        while True:
            # Let C-level .find() locate the first occurrence of each interesting byte.
            nul_at = data.find(b'\x00', pos)
            cr_at = data.find(b'\r', pos)
            lf_at = data.find(b'\n', pos)

            # Replace "not found" (-1) with length so min() picks the real hits.
            if nul_at < 0:
                nul_at = length
            if cr_at < 0:
                cr_at = length
            if lf_at < 0:
                lf_at = length

            first = min(nul_at, cr_at, lf_at)

            if first == length:
                # None of the three bytes found before end of data.
                break

            # NUL: always an error
            if first == nul_at and nul_at <= cr_at and nul_at <= lf_at:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                    message='NUL byte in header data',
                    line=self.current_line,
                    offset=nul_at,
                )

            # CR: check for CRLF vs bare CR
            if first == cr_at and cr_at <= lf_at:
                if cr_at + 1 < length and data[cr_at + 1] == self._LF:
                    return cr_at  # CRLF - this is the line ending

                # Bare CR (not followed by LF)
                if not self.config.allow_bare_cr_in_value:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.BARE_CARRIAGE_RETURN,
                        message='Bare CR not followed by LF',
                        line=self.current_line,
                        offset=cr_at,
                    )

                # Bare CR is allowed in values - skip past it and search again.
                pos = cr_at + 1
                continue

            # LF: bare LF (if it were preceded by CR we'd have returned above)
            if self.config.allow_bare_lf:
                return lf_at

            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.BARE_LF,
                message='Bare LF without preceding CR',
                line=self.current_line,
                offset=lf_at,
            )

        raise HeaderFieldHttpParseError(
            code=HeaderFieldHttpParseErrorCode.MISSING_TERMINATOR,
            message='Unexpected end of data while scanning for line ending',
            line=self.current_line,
            offset=length,
        )

    def line_ending_len(self, line_end_pos: int) -> int:
        """Return the length of the line ending at *line_end_pos* (1 for LF, 2 for CRLF)."""

        if line_end_pos < len(self.data) and self.data[line_end_pos] == self._LF:
            return 1  # bare LF
        return 2  # CRLF

    # Kind detection

    def detect_kind(self, start_line: bytes) -> ParsedHttpMessage.Kind:
        if self.mode == HttpParser.Mode.REQUEST:
            return ParsedHttpMessage.Kind.REQUEST

        if self.mode == HttpParser.Mode.RESPONSE:
            return ParsedHttpMessage.Kind.RESPONSE

        # AUTO: responses start with "HTTP/"
        if start_line.startswith(b'HTTP/'):
            return ParsedHttpMessage.Kind.RESPONSE

        return ParsedHttpMessage.Kind.REQUEST

    # Start-line parsing

    _REQUEST_TARGET_BYTES: ta.ClassVar[bytes] = bytes(set(_VCHAR_BYTES) | set(range(0x80, 0x100)))

    def parse_request_line(self, line: bytes) -> ParsedHttpMessage.RequestLine:
        """Parse ``method SP request-target SP HTTP-version``."""

        # Must have exactly two SP separators

        first_sp = line.find(b' ')
        if first_sp < 0:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE,
                message='No SP found in request-line',
                line=0,
                offset=0,
            )

        last_sp = line.rfind(b' ')
        if first_sp == last_sp:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE,
                message='Only one SP found in request-line; expected method SP target SP version',
                line=0,
                offset=first_sp,
            )

        method_bytes = line[:first_sp]
        target_bytes = line[first_sp + 1:last_sp]
        version_bytes = line[last_sp + 1:]

        # Validate no extra SP in components: check that second SP search from first_sp+1 matches last_sp - i.e., the
        # target does not contain the last SP. Actually the HTTP spec says request-target can contain spaces? No - it's
        # defined as *visible ASCII*. But to find the correct split: method is a token (no SP), version is fixed format
        # (no SP), and everything in between is the target which is VCHAR (no SP). However, some real URIs... no, VCHAR
        # excludes SP. Let's be strict: Check there are exactly 2 SPs total.
        if line.count(b' ') != 2:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_REQUEST_LINE,
                message=f'Request-line contains {line.count(b" ")} spaces; expected exactly 2',
                line=0,
                offset=0,
            )

        # Validate method

        if not method_bytes:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_METHOD,
                message='Empty method in request-line',
                line=0,
                offset=0,
            )

        if method_bytes.translate(None, self._TCHAR_BYTES):
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_METHOD,
                message=f'Method contains invalid character(s)',
                line=0,
                offset=0,
            )

        # Validate request-target (VCHAR only, non-empty)

        if not target_bytes:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_REQUEST_TARGET,
                message='Empty request-target',
                line=0,
                offset=first_sp + 1,
            )

        if self.config.reject_non_visible_ascii_request_target:
            if target_bytes.translate(None, self._VCHAR_BYTES):
                raise StartLineHttpParseError(
                    code=StartLineHttpParseErrorCode.INVALID_REQUEST_TARGET,
                    message='Request-target contains non-visible-ASCII character(s)',
                    line=0,
                    offset=first_sp + 1,
                )

        else:
            if target_bytes.translate(None, self._REQUEST_TARGET_BYTES):
                raise StartLineHttpParseError(
                    code=StartLineHttpParseErrorCode.INVALID_REQUEST_TARGET,
                    message='Request-target contains invalid character(s)',
                    line=0,
                    offset=first_sp + 1,
                )

        # Validate HTTP version

        version_str = version_bytes.decode('ascii', errors='replace')
        if version_str == 'HTTP/1.0':
            version = HttpVersions.HTTP_1_0
        elif version_str == 'HTTP/1.1':
            version = HttpVersions.HTTP_1_1
        else:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.UNSUPPORTED_HTTP_VERSION,
                message=f'Unsupported HTTP version: {version_str!r}',
                line=0,
                offset=last_sp + 1,
            )

        return ParsedHttpMessage.RequestLine(
            method=method_bytes.decode('ascii'),
            request_target=target_bytes,
            http_version=version,
        )

    # reason-phrase: 0+ bytes of HTAB / SP / VCHAR / obs-text
    _RE_REASON_PHRASE: ta.ClassVar[re.Pattern] = re.compile(rb'^[\x09\x20\x21-\x7e\x80-\xff]*\Z')

    # reason-phrase = *( HTAB / SP / VCHAR / obs-text )
    _REASON_PHRASE_CHARS: ta.ClassVar[ta.FrozenSet[int]] = frozenset(
        {_HTAB, _SP} |
        set(_VCHAR) |
        set(_OBS_TEXT),
    )

    def parse_status_line(self, line: bytes) -> ParsedHttpMessage.StatusLine:
        """Parse ``HTTP-version SP status-code SP reason-phrase``."""

        # First SP separates version from status code

        first_sp = line.find(b' ')
        if first_sp < 0:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_STATUS_LINE,
                message='No SP found in status-line',
                line=0,
                offset=0,
            )

        version_bytes = line[:first_sp]
        rest = line[first_sp + 1:]

        # Second SP separates status code from reason phrase

        second_sp = rest.find(b' ')
        if second_sp < 0:
            # Per RFC 7230:
            #   `status-line = HTTP-version SP status-code SP reason-phrase`.
            # The SP before reason-phrase is required even if reason-phrase is empty.
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.MALFORMED_STATUS_LINE,
                message='Missing second SP in status-line (required before reason-phrase)',
                line=0,
                offset=first_sp + 1 + len(rest),
            )

        status_bytes = rest[:second_sp]
        reason_bytes = rest[second_sp + 1:]

        # Validate HTTP version

        version_str = version_bytes.decode('ascii', errors='replace')
        if version_str == 'HTTP/1.0':
            version = HttpVersions.HTTP_1_0
        elif version_str == 'HTTP/1.1':
            version = HttpVersions.HTTP_1_1
        else:
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.UNSUPPORTED_HTTP_VERSION,
                message=f'Unsupported HTTP version: {version_str!r}',
                line=0,
                offset=0,
            )

        # Validate status code: exactly 3 ASCII digits

        if len(status_bytes) != 3 or not status_bytes.isdigit():
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_STATUS_CODE,
                message=f'Status code is not exactly 3 digits: {status_bytes!r}',
                line=0,
                offset=first_sp + 1,
            )

        status_code = int(status_bytes)
        if not (100 <= status_code <= 599):
            raise StartLineHttpParseError(
                code=StartLineHttpParseErrorCode.INVALID_STATUS_CODE,
                message=f'Status code {status_code} out of range 100-599',
                line=0,
                offset=first_sp + 1,
            )

        # Validate reason-phrase characters

        if not self._RE_REASON_PHRASE.match(reason_bytes):
            # Regex rejected - scan to find the specific bad byte for error reporting
            reason_base_offset = first_sp + 1 + second_sp + 1

            for i, b in enumerate(reason_bytes):
                if b == self._NUL:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                        message='NUL byte in reason-phrase',
                        line=0,
                        offset=reason_base_offset + i,
                    )

                if b not in self._REASON_PHRASE_CHARS:
                    raise StartLineHttpParseError(
                        code=StartLineHttpParseErrorCode.MALFORMED_STATUS_LINE,
                        message=f'Invalid character 0x{b:02x} in reason-phrase',
                        line=0,
                        offset=reason_base_offset + i,
                    )

        return ParsedHttpMessage.StatusLine(
            http_version=version,
            status_code=status_code,
            reason_phrase=reason_bytes.decode('latin-1'),
        )

    # Header field parsing

    def parse_header_fields(self, start: int) -> ta.List[RawParsedHttpHeader]:
        """Parse all header fields from *start* until the empty-line terminator."""

        headers: ta.List[RawParsedHttpHeader] = []
        pos = start
        data = self.data
        self.current_line = 1  # line 0 is the start-line

        while pos < len(data):
            # Check for the empty line that terminates headers
            if data[pos] == self._CR and pos + 1 < len(data) and data[pos + 1] == self._LF:
                # Could be the terminator (\r\n at start of a "line" = empty line)
                break

            if self.config.allow_bare_lf and data[pos] == self._LF:
                break

            # Max header count check
            if len(headers) >= self.config.max_header_count:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.TOO_MANY_HEADERS,
                    message=f'Exceeded maximum header count of {self.config.max_header_count}',
                    line=self.current_line,
                    offset=pos,
                )

            # Find end of this header line
            line_end = self.find_line_end(pos)
            line_data = data[pos:line_end]
            next_pos = line_end + self.line_ending_len(line_end)

            if self.config.max_header_length is not None and len(line_data) > self.config.max_header_length:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                    message='Header line exceeds maximum length',
                    line=self.current_line,
                    offset=next_pos,
                )

            # Handle obs-fold: if the *next* line starts with SP or HTAB, it's a continuation
            obs_buf: ta.Optional[io.BytesIO] = None

            while next_pos < len(data):
                next_byte = data[next_pos]

                if next_byte in self._OWS_CHARS:
                    if not self.config.allow_obs_fold:
                        raise HeaderFieldHttpParseError(
                            code=HeaderFieldHttpParseErrorCode.OBS_FOLD_NOT_ALLOWED,
                            message='Obsolete line folding (obs-fold) encountered but not allowed',
                            line=self.current_line,
                            offset=next_pos,
                        )

                    # Unfold: find the end of the continuation line
                    cont_line_end = self.find_line_end(next_pos)
                    cont_data = data[next_pos:cont_line_end]

                    # Replace fold with single SP
                    if obs_buf is None:
                        obs_buf = io.BytesIO()
                        obs_buf.write(line_data)
                    obs_buf.write(b' ')
                    obs_buf.write(cont_data.lstrip(b' \t'))

                    next_pos = cont_line_end + self.line_ending_len(cont_line_end)

                    if self.config.max_header_length is not None and obs_buf.tell() > self.config.max_header_length:
                        raise HeaderFieldHttpParseError(
                            code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                            message='Unfolded header line exceeds maximum length',
                            line=self.current_line,
                            offset=next_pos,
                        )

                else:
                    break

            if obs_buf is not None:
                line_data = obs_buf.getvalue()

            # Parse field-name : field-value
            header = self._parse_one_header(line_data, pos)
            headers.append(header)

            pos = next_pos
            self.current_line += 1

        return headers

    @classmethod
    def _strip_ows(cls, data: bytes) -> bytes:
        """Strip leading and trailing optional whitespace (SP / HTAB)."""

        return data.strip(b' \t')

    # token: 1+ tchar bytes
    _RE_TOKEN: ta.ClassVar[re.Pattern] = re.compile(rb"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+\Z")

    # Pre-calculate the 4 field-value variants for the translation filter (allow_bare_cr, reject_obs_text)
    _FIELD_VALUE_ALLOWED: ta.ClassVar[ta.Mapping[ta.Tuple[bool, bool], bytes]] = {
        (False, False): bytes({_HTAB, _SP}      | set(range(0x21, 0x7F))   | set(range(0x80, 0x100))),  # noqa
        (False, True):  bytes({_HTAB, _SP}      | set(range(0x21, 0x7F))),  # noqa
        (True, False):  bytes({_HTAB, _CR, _SP} | set(range(0x21, 0x7F))   | set(range(0x80, 0x100))),  # noqa
        (True, True):   bytes({_HTAB, _CR, _SP} | set(range(0x21, 0x7F))),  # noqa
    }

    def _parse_one_header(self, line_data: bytes, line_start_offset: int) -> RawParsedHttpHeader:
        """Parse a single ``field-name: field-value`` line (already unfolded)."""

        colon_idx = line_data.find(b':')
        if colon_idx < 0:
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.MISSING_COLON,
                message='Header line has no colon separator',
                line=self.current_line,
                offset=line_start_offset,
            )

        name_bytes = line_data[:colon_idx]
        value_bytes = line_data[colon_idx + 1:]

        # Validate field-name

        if not name_bytes:
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.EMPTY_FIELD_NAME,
                message='Empty field-name before colon',
                line=self.current_line,
                offset=line_start_offset,
            )

        # Check for space before colon
        if name_bytes[-1] in self._OWS_CHARS:
            if not self.config.allow_space_before_colon:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.SPACE_BEFORE_COLON,
                    message='Whitespace between field-name and colon',
                    line=self.current_line,
                    offset=line_start_offset + len(name_bytes) - 1,
                )

            # Strip trailing whitespace from name if allowed
            name_bytes = name_bytes.rstrip(b' \t')
            if not name_bytes:
                raise HeaderFieldHttpParseError(
                    code=HeaderFieldHttpParseErrorCode.EMPTY_FIELD_NAME,
                    message='Field-name is only whitespace before colon',
                    line=self.current_line,
                    offset=line_start_offset,
                )

        # Validate name characters (regex fast-path; fallback scan on failure)
        if not self._RE_TOKEN.match(name_bytes):
            for i, b in enumerate(name_bytes):
                if b == self._NUL:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                        message='NUL byte in field-name',
                        line=self.current_line,
                        offset=line_start_offset + i,
                    )

                if b >= 0x80:
                    raise EncodingHttpParseError(
                        code=EncodingHttpParseErrorCode.NON_ASCII_IN_FIELD_NAME,
                        message=f'Non-ASCII byte 0x{b:02x} in field-name',
                        line=self.current_line,
                        offset=line_start_offset + i,
                    )

                if b not in self._TCHAR:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_NAME,
                        message=f'Invalid character 0x{b:02x} in field-name',
                        line=self.current_line,
                        offset=line_start_offset + i,
                    )

        # Process field-value

        # Strip OWS
        value_stripped = self._strip_ows(value_bytes)

        # Check for empty value
        if not value_stripped and not self.config.allow_empty_header_values:
            raise HeaderFieldHttpParseError(
                code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                message='Empty header field value not allowed',
                line=self.current_line,
                offset=line_start_offset + colon_idx + 1,
            )

        # Validate value characters (Translation fast-path)
        allowed_bytes = self._FIELD_VALUE_ALLOWED[(
            self.config.allow_bare_cr_in_value,
            self.config.reject_obs_text,
        )]

        # This is the "Pedantic" C-speed check. translate(None, allowed_bytes) removes all valid characters. If any
        # bytes remain, the input is invalid.
        invalid_chars = value_stripped.translate(None, allowed_bytes)

        if invalid_chars:
            value_base_offset = line_start_offset + colon_idx + 1
            # We only enter this Python loop if we ALREADY found an error.
            # This keeps the "happy path" fast while maintaining detailed error reporting.
            for i, b in enumerate(value_stripped):
                if b == self._NUL:
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.NUL_IN_HEADER,
                        message='NUL byte in field-value',
                        line=self.current_line,
                        offset=value_base_offset + i,
                    )

                if b == self._CR:
                    if not self.config.allow_bare_cr_in_value:
                        raise HeaderFieldHttpParseError(
                            code=HeaderFieldHttpParseErrorCode.BARE_CARRIAGE_RETURN,
                            message='Bare CR in field-value',
                            line=self.current_line,
                            offset=value_base_offset + i,
                        )
                    continue

                if b not in allowed_bytes:
                    # Specific error logic for obs-text/bare CR
                    if b >= 0x80 and self.config.reject_obs_text:
                        raise EncodingHttpParseError(
                            code=EncodingHttpParseErrorCode.OBS_TEXT_IN_FIELD_VALUE,
                            message=f'obs-text byte 0x{b:02x} rejected by config',
                            line=self.current_line,
                            offset=value_base_offset + i,
                        )

                    # General character error
                    raise HeaderFieldHttpParseError(
                        code=HeaderFieldHttpParseErrorCode.INVALID_FIELD_VALUE,
                        message=f'Invalid character 0x{b:02x} in field-value',
                        line=self.current_line,
                        offset=value_base_offset + i,
                    )

        return RawParsedHttpHeader(
            name=name_bytes,
            value=value_stripped,
        )

    # Prepared header construction

    def prepare_headers(
        self,
        headers: ParsedHttpHeaders,
        kind: ParsedHttpMessage.Kind,
        http_version: HttpVersion,
    ) -> PreparedParsedHttpHeaders:
        prepared = PreparedParsedHttpHeaders()

        self._prepare_content_length(headers, prepared)
        self._prepare_transfer_encoding(headers, prepared, kind, http_version)
        self._prepare_host(headers, prepared, kind, http_version)
        self._prepare_connection(headers, prepared, http_version)
        self._prepare_content_type(headers, prepared)
        self._prepare_te(headers, prepared)
        self._prepare_upgrade(headers, prepared)
        self._prepare_trailer(headers, prepared)
        self._prepare_expect(headers, prepared)
        self._prepare_date(headers, prepared)
        self._prepare_cache_control(headers, prepared)
        self._prepare_accept_encoding(headers, prepared)
        self._prepare_accept(headers, prepared)
        self._prepare_authorization(headers, prepared)

        # Cross-field: Content-Length + Transfer-Encoding conflict
        if (
            prepared.content_length is not None and
            prepared.transfer_encoding is not None and
            not self.config.allow_content_length_with_te
        ):
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.CONTENT_LENGTH_WITH_TRANSFER_ENCODING,
                message='Content-Length and Transfer-Encoding are both present',
            )

        return prepared

    def _prepare_content_length(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        values = headers.get_all('content-length')
        if not values:
            return

        parsed_values: ta.List[int] = []
        for v in values:
            # A single Content-Length header might itself be a comma-separated list (some implementations do this). We
            # parse each element.
            if self.config.reject_multi_value_content_length and ',' in v:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                    message=f'Content-Length with multiple values is forbidden: {v!r}',
                )

            for part in v.split(','):
                stripped = part.strip()

                if not stripped.isdigit():
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                        message=f'Content-Length value is not a valid non-negative integer: {stripped!r}',
                    )

                if (
                        self.config.max_content_length_str_len is not None and
                        len(stripped) > self.config.max_content_length_str_len
                ):
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                        message=f'Content-Length value string too long: {stripped!r}',
                    )

                parsed_values.append(int(stripped))

        if not parsed_values:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                message='Content-Length header present but empty',
            )

        unique = set(parsed_values)
        if len(unique) > 1:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.CONFLICTING_CONTENT_LENGTH,
                message=f'Conflicting Content-Length values: {sorted(unique)}',
            )

        if len(parsed_values) > 1:
            if not self.config.allow_multiple_content_lengths:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.DUPLICATE_CONTENT_LENGTH,
                    message=(
                        f'Multiple Content-Length values (all {parsed_values[0]}); '
                        f'set allow_multiple_content_lengths to accept'
                    ),
                )

        val = parsed_values[0]
        if val < 0:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_LENGTH,
                message=f'Content-Length is negative: {val}',
            )

        prepared.content_length = val

    _KNOWN_CODINGS: ta.ClassVar[ta.FrozenSet[str]] = frozenset([
        'chunked',
        'compress',
        'deflate',
        'gzip',
        'x-gzip',
        'x-compress',
    ])

    def _prepare_transfer_encoding(
        self,
        headers: ParsedHttpHeaders,
        prepared: PreparedParsedHttpHeaders,
        kind: ParsedHttpMessage.Kind,
        http_version: HttpVersion,
    ) -> None:
        if 'transfer-encoding' not in headers:
            return

        combined = headers['transfer-encoding']
        codings = [c.strip().lower() for c in combined.split(',') if c.strip()]

        if not codings:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_TRANSFER_ENCODING,
                message='Transfer-Encoding header present but empty',
            )

        # HTTP/1.0 check
        if http_version == HttpVersions.HTTP_1_0 and not self.config.allow_transfer_encoding_http10:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.TE_IN_HTTP10,
                message='Transfer-Encoding is not defined for HTTP/1.0',
            )

        # Validate known codings
        if not self.config.allow_unknown_transfer_encoding:
            for c in codings:
                if c not in self._KNOWN_CODINGS:
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_TRANSFER_ENCODING,
                        message=f'Unknown transfer-coding: {c!r}',
                    )

        # chunked positioning
        if 'chunked' in codings:
            if codings[-1] != 'chunked':
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.TE_WITHOUT_CHUNKED_LAST,
                    message='chunked must be the last (outermost) transfer-coding',
                )

            if codings.count('chunked') > 1:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_TRANSFER_ENCODING,
                    message='chunked appears more than once in Transfer-Encoding',
                )

        else:
            # No chunked present
            if kind == ParsedHttpMessage.Kind.REQUEST:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.TE_WITHOUT_CHUNKED_LAST,
                    message='Transfer-Encoding in a request must include chunked as the last coding',
                )

            elif kind == ParsedHttpMessage.Kind.RESPONSE:
                if not self.config.allow_te_without_chunked_in_response:
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.TE_WITHOUT_CHUNKED_LAST,
                        message=(
                            'Transfer-Encoding in a response without chunked; '
                            'set allow_te_without_chunked_in_response to accept'
                        ),
                    )

        prepared.transfer_encoding = codings

    # Host header: reject control chars 0x00-0x1F and SP 0x20. # Operates on str (already latin-1 decoded).
    _RE_HOST_VALID: ta.ClassVar[re.Pattern] = re.compile(r'^[^\x00-\x20]*\Z')

    def _prepare_host(
        self,
        headers: ParsedHttpHeaders,
        prepared: PreparedParsedHttpHeaders,
        kind: ParsedHttpMessage.Kind,
        http_version: HttpVersion,
    ) -> None:
        values = headers.get_all('host')

        if kind == ParsedHttpMessage.Kind.REQUEST and http_version == HttpVersions.HTTP_1_1:
            if not values and not self.config.allow_missing_host:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.MISSING_HOST_HEADER,
                    message='Host header is required in HTTP/1.1 requests',
                )

        if len(values) > 1:
            if not self.config.allow_multiple_hosts:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.MULTIPLE_HOST_HEADERS,
                    message=f'Multiple Host headers found ({len(values)})',
                )

            # If allowed, all values must be identical
            unique = set(values)
            if len(unique) > 1:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.CONFLICTING_HOST_HEADERS,
                    message=f'Multiple Host headers with different values: {sorted(unique)}',
                )

        if values:
            host_val = values[0].strip()

            # Minimal validation: reject any whitespace/control chars. Host is an authority, and
            # allowing OWS creates parsing inconsistencies across components.
            if not host_val and kind == ParsedHttpMessage.Kind.REQUEST:
                # Empty Host is technically allowed for certain request-targets (authority form, etc.), but let's just
                # accept it - the URI layer handles that.
                pass

            # Reject any SP / HTAB anywhere.
            if ' ' in host_val or '\t' in host_val:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_HOST,
                    message='Whitespace not allowed in Host header',
                )

            # Reject other C0 controls (including NUL) if present (defense in depth). (Host is a str decoded as Latin-1
            # in your ParsedHttpHeaders container.)
            if not self._RE_HOST_VALID.match(host_val):
                for i, ch in enumerate(host_val):
                    if ord(ch) < 0x21:  # includes 0x00-0x20; we've already rejected SP/HTAB explicitly
                        raise SemanticHeaderHttpParseError(
                            code=SemanticHeaderHttpParseErrorCode.INVALID_HOST,
                            message=f'Invalid character in Host header at position {i}',
                        )

            prepared.host = host_val

    @classmethod
    def _parse_comma_list(cls, value: str) -> ta.List[str]:
        """Split a comma-separated header value into trimmed, non-empty tokens."""

        parts: ta.List[str] = []
        for part in value.split(','):
            stripped = part.strip()
            if stripped:
                parts.append(stripped)
        return parts

    def _prepare_connection(
        self,
        headers: ParsedHttpHeaders,
        prepared: PreparedParsedHttpHeaders,
        http_version: HttpVersion,
    ) -> None:
        if 'connection' in headers:
            tokens = {t.lower() for t in self._parse_comma_list(headers['connection'])}
            prepared.connection = frozenset(tokens)
        else:
            prepared.connection = frozenset()

        # Derive keep_alive
        if 'close' in prepared.connection:
            prepared.keep_alive = False
        elif 'keep-alive' in prepared.connection:
            prepared.keep_alive = True
        else:
            # Default: HTTP/1.1 = keep-alive, HTTP/1.0 = close
            prepared.keep_alive = (http_version == HttpVersions.HTTP_1_1)

    @classmethod
    def _parse_quoted_string(cls, data: str, pos: int) -> ta.Tuple[str, int]:
        """
        Parse a quoted-string starting at *pos* (which must point at the opening DQUOTE). Returns (unescaped_value,
        position_after_closing_DQUOTE).
        """

        if pos >= len(data) or data[pos] != '"':
            raise ValueError('Expected opening double-quote')

        pos += 1  # skip opening "

        result: ta.List[str] = []
        while pos < len(data):
            ch = data[pos]

            if ch == '"':
                return ''.join(result), pos + 1

            if ch == '\\':
                pos += 1
                if pos >= len(data):
                    raise ValueError('Backslash at end of quoted-string')
                result.append(data[pos])
                pos += 1

            else:
                result.append(ch)
                pos += 1

        raise ValueError('Unterminated quoted-string')

    @classmethod
    def _parse_media_type_params(cls, params_str: str) -> ta.Dict[str, str]:
        """
        Parse ``;param=value`` segments from a Content-Type or Accept header. Values may be tokens or quoted-strings.
        """

        params: ta.Dict[str, str] = {}

        remaining = params_str.strip()
        while remaining:
            if not remaining.startswith(';'):
                break

            remaining = remaining[1:].strip()
            if not remaining:
                break

            eq_idx = remaining.find('=')
            if eq_idx < 0:
                # parameter name without value - skip to next semicolon or end
                semi_idx = remaining.find(';')
                if semi_idx < 0:
                    break

                remaining = remaining[semi_idx:]
                continue

            pname = remaining[:eq_idx].strip().lower()
            remaining = remaining[eq_idx + 1:].strip()

            if remaining.startswith('"'):
                try:
                    pvalue, end_pos = cls._parse_quoted_string(remaining, 0)
                except ValueError:
                    break
                remaining = remaining[end_pos:].strip()

            else:
                semi_idx = remaining.find(';')

                if semi_idx < 0:
                    pvalue = remaining.strip()
                    remaining = ''
                else:
                    pvalue = remaining[:semi_idx].strip()
                    remaining = remaining[semi_idx:]

            if pname:
                params[pname] = pvalue

        return params

    def _prepare_content_type(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'content-type' not in headers:
            return

        raw = headers['content-type']

        # media-type = type "/" subtype *( OWS ";" OWS parameter )
        semi_idx = raw.find(';')
        if semi_idx < 0:
            media_type = raw.strip().lower()
            params: ta.Dict[str, str] = {}
        else:
            media_type = raw[:semi_idx].strip().lower()
            params = self._parse_media_type_params(raw[semi_idx:])

        if '/' not in media_type:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_TYPE,
                message=f'Content-Type missing "/" in media-type: {media_type!r}',
            )

        parts = media_type.split('/', 1)
        if not parts[0] or not parts[1]:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_CONTENT_TYPE,
                message=f'Content-Type has empty type or subtype: {media_type!r}',
            )

        prepared.content_type = PreparedParsedHttpHeaders.ContentType(
            media_type=media_type,
            params=params,
        )

    @classmethod
    def _split_header_element(cls, element: str) -> ta.Tuple[str, float, ta.Dict[str, str]]:
        """
        Split a single header list element like ``"token;q=0.5;param=val"`` into ``(token_lower, q, params_dict)``.

        *token* is lowercased.  ``q`` defaults to ``1.0`` if absent.  The ``q`` key is consumed and **not** included in
        *params_dict*.  Raises ``ValueError`` on a malformed ``q`` value.
        """

        semi_idx = element.find(';')
        if semi_idx < 0:
            return element.strip().lower(), 1.0, {}

        token = element[:semi_idx].strip().lower()
        params = cls._parse_media_type_params(element[semi_idx:])

        q = 1.0
        q_str = params.pop('q', None)
        if q_str is not None:
            q = float(q_str)  # caller wraps ValueError

        return token, q, params

    def _prepare_te(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'te' not in headers:
            return

        codings = [
            self._split_header_element(p)[0]
            for p in self._parse_comma_list(headers['te'])
        ]

        prepared.te = [c for c in codings if c]

    def _prepare_upgrade(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'upgrade' not in headers:
            return

        prepared.upgrade = self._parse_comma_list(headers['upgrade'])

    # Headers that MUST NOT appear in trailers (RFC 7230 §4.1.2)
    _FORBIDDEN_TRAILER_FIELDS: ta.ClassVar[ta.FrozenSet[str]] = frozenset({
        'transfer-encoding',
        'content-length',
        'host',
        'cache-control',
        'expect',
        'max-forwards',
        'pragma',
        'range',
        'te',
        'authorization',
        'proxy-authenticate',
        'proxy-authorization',
        'www-authenticate',
        'content-encoding',
        'content-type',
        'content-range',
        'trailer',
    })

    def _prepare_trailer(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'trailer' not in headers:
            return

        fields = {f.lower() for f in self._parse_comma_list(headers['trailer'])}
        for f in fields:
            if f in self._FORBIDDEN_TRAILER_FIELDS:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.FORBIDDEN_TRAILER_FIELD,
                    message=f'Forbidden field in Trailer header: {f!r}',
                )

        prepared.trailer = frozenset(fields)

    def _prepare_expect(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'expect' not in headers:
            return

        raw = headers['expect'].strip().lower()
        if raw != '100-continue':
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_EXPECT,
                message=f'Only "100-continue" is accepted for Expect; got {raw!r}',
            )

        prepared.expect = raw
        prepared.expect_100_continue = True

    _MONTH_NAMES: ta.ClassVar[ta.Mapping[str, int]] = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12,
    }

    @classmethod
    def _parse_http_date(cls, value: str) -> datetime.datetime:
        """
        Parse an HTTP-date (RFC 7231 §7.1.1.1).

        Supports:
          - IMF-fixdate:  Sun, 06 Nov 1994 08:49:37 GMT
          - RFC 850:      Sunday, 06-Nov-94 08:49:37 GMT
          - asctime:      Sun Nov  6 08:49:37 1994
        """

        value = value.strip()

        # Try IMF-fixdate: day-name "," SP date1 SP time-of-day SP GMT
        # date1 = day SP month SP year (4-digit)
        if ',' in value:
            after_comma = value.split(',', 1)[1].strip()
            parts = after_comma.split()

            if len(parts) == 3 and parts[2].upper() == 'GMT' and '-' in parts[0]:
                # RFC 850: DD-Mon-YY HH:MM:SS GMT
                date_pieces = parts[0].split('-')
                if len(date_pieces) != 3:
                    raise ValueError(f'Invalid date component: {parts[0]}')

                day = int(date_pieces[0])
                month_str = date_pieces[1].lower()
                year_raw = int(date_pieces[2])

                # Two-digit year: RFC 7231 says interpret >= 50 as 19xx, < 50 as 20xx
                if year_raw < 100:
                    year = year_raw + 1900 if year_raw >= 50 else year_raw + 2000
                else:
                    year = year_raw

                time_pieces = parts[1].split(':')
                if len(time_pieces) != 3:
                    raise ValueError(f'Invalid time component: {parts[1]}')

                hour, minute, second = int(time_pieces[0]), int(time_pieces[1]), int(time_pieces[2])

                month = cls._MONTH_NAMES.get(month_str)
                if month is None:
                    raise ValueError(f'Invalid month: {month_str}')

                return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)  # noqa

            elif len(parts) == 5 and parts[4].upper() == 'GMT':
                # IMF-fixdate: DD Mon YYYY HH:MM:SS GMT
                day = int(parts[0])
                month_str = parts[1].lower()
                year = int(parts[2])

                time_pieces = parts[3].split(':')
                if len(time_pieces) != 3:
                    raise ValueError(f'Invalid time component: {parts[3]}')

                hour, minute, second = int(time_pieces[0]), int(time_pieces[1]), int(time_pieces[2])

                month = cls._MONTH_NAMES.get(month_str)
                if month is None:
                    raise ValueError(f'Invalid month: {month_str}')

                return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)  # noqa

            raise ValueError(f'Cannot parse date: {value}')

        else:
            # asctime: Sun Nov  6 08:49:37 1994 (Strict fixed-width check)
            # 012345678901234567890123
            # Sun Nov  6 08:49:37 1994
            if len(value) != 24:
                raise ValueError(f'Invalid asctime length: {len(value)}')

            month_str = value[4:7].lower()
            # Handle the space-padded day (e.g., " 6")
            day_str = value[8:10].replace(' ', '0')
            day = int(day_str)

            time_pieces = value[11:19].split(':')
            if len(time_pieces) != 3:
                raise ValueError('Invalid time component')
            hour, minute, second = map(int, time_pieces)

            year = int(value[20:24])
            month = cls._MONTH_NAMES.get(month_str)
            if month is None:
                raise ValueError(f'Invalid month: {month_str}')

            return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)  # noqa

    def _prepare_date(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'date' not in headers:
            return

        raw = headers['date']
        try:
            prepared.date = self._parse_http_date(raw)
        except (ValueError, IndexError, OverflowError) as e:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_DATE,
                message=f'Cannot parse Date header: {e}',
            ) from None

    def _prepare_cache_control(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'cache-control' not in headers:
            return

        directives: ta.Dict[str, ta.Optional[str]] = {}

        for part in self._parse_comma_list(headers['cache-control']):
            eq_idx = part.find('=')
            if eq_idx < 0:
                directives[part.lower()] = None
                continue

            name = part[:eq_idx].strip().lower()
            value = part[eq_idx + 1:].strip()
            if value.startswith('"'):
                try:
                    value, _ = self._parse_quoted_string(value, 0)
                except ValueError:
                    raise SemanticHeaderHttpParseError(
                        code=SemanticHeaderHttpParseErrorCode.INVALID_CACHE_CONTROL,
                        message=f'Invalid quoted-string in Cache-Control directive: {name}',
                    ) from None

            directives[name] = value

        prepared.cache_control = directives

    def _prepare_accept_encoding(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'accept-encoding' not in headers:
            return

        items: ta.List[PreparedParsedHttpHeaders.AcceptEncodingItem] = []

        for part in self._parse_comma_list(headers['accept-encoding']):
            try:
                coding, q, _ = self._split_header_element(part)
            except ValueError:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_ACCEPT_ENCODING,
                    message=f'Invalid q-value in Accept-Encoding: {part!r}',
                ) from None

            if coding:
                items.append(PreparedParsedHttpHeaders.AcceptEncodingItem(
                    coding=coding,
                    q=q,
                ))

        prepared.accept_encoding = items

    def _prepare_accept(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'accept' not in headers:
            return

        items: ta.List[PreparedParsedHttpHeaders.AcceptItem] = []

        for part in self._parse_comma_list(headers['accept']):
            try:
                media_range, q, params = self._split_header_element(part)
            except ValueError:
                raise SemanticHeaderHttpParseError(
                    code=SemanticHeaderHttpParseErrorCode.INVALID_ACCEPT,
                    message=f'Invalid q-value in Accept: {part!r}',
                ) from None

            items.append(PreparedParsedHttpHeaders.AcceptItem(
                media_range=media_range,
                q=q,
                params=params,
            ))

        prepared.accept = items

    def _prepare_authorization(self, headers: ParsedHttpHeaders, prepared: PreparedParsedHttpHeaders) -> None:
        if 'authorization' not in headers:
            return

        raw = headers['authorization'].strip()
        if not raw:
            raise SemanticHeaderHttpParseError(
                code=SemanticHeaderHttpParseErrorCode.INVALID_AUTHORIZATION,
                message='Authorization header is present but empty',
            )

        # scheme SP credentials (credentials may contain spaces for some schemes)
        sp_idx = raw.find(' ')
        if sp_idx < 0:
            # Scheme only, no credentials (e.g., some edge cases)
            prepared.authorization = PreparedParsedHttpHeaders.AuthorizationValue(
                scheme=raw,
                credentials='',
            )
        else:
            scheme = raw[:sp_idx]
            credentials = raw[sp_idx + 1:]
            prepared.authorization = PreparedParsedHttpHeaders.AuthorizationValue(
                scheme=scheme,
                credentials=credentials,
            )


##


def parse_http_message(
        data: bytes,
        mode: HttpParser.Mode = HttpParser.Mode.AUTO,
        config: ta.Optional[HttpParser.Config] = None,
) -> ParsedHttpMessage:
    parser = HttpParser(**(dict(config=config) if config is not None else {}))
    return parser.parse_message(data, mode=mode)


def parse_http_trailers(
        data: bytes,
        config: ta.Optional[HttpParser.Config] = None,
) -> ParsedHttpTrailers:
    parser = HttpParser(**(dict(config=config) if config is not None else {}))
    return parser.parse_trailers(data)


########################################
# ../../../omlish/lite/marshal.py
"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
 - Options.sequence_cls = list, mapping_cls = dict, ... - def with_mutable_containers() -> Options
"""


##


@dc.dataclass(frozen=True)
class ObjMarshalOptions:
    raw_bytes: bool = False
    non_strict_fields: bool = False


class ObjMarshaler(Abstract):
    @abc.abstractmethod
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        raise NotImplementedError


class NopObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o


class ProxyObjMarshaler(ObjMarshaler):
    def __init__(self, m: ta.Optional[ObjMarshaler] = None) -> None:
        super().__init__()

        self._m = m

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.not_none(self._m).marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.not_none(self._m).unmarshal(o, ctx)


class CastObjMarshaler(ObjMarshaler):
    def __init__(self, ty: type) -> None:
        super().__init__()

        self._ty = ty

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty(o)


class DynamicObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return ctx.manager.marshal_obj(o, opts=ctx.options)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o


class Base64ObjMarshaler(ObjMarshaler):
    def __init__(self, ty: type) -> None:
        super().__init__()

        self._ty = ty

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return base64.b64encode(o).decode('ascii')

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty(base64.b64decode(o))


class BytesSwitchedObjMarshaler(ObjMarshaler):
    def __init__(self, m: ObjMarshaler) -> None:
        super().__init__()

        self._m = m

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if ctx.options.raw_bytes:
            return o
        return self._m.marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if ctx.options.raw_bytes:
            return o
        return self._m.unmarshal(o, ctx)


class EnumObjMarshaler(ObjMarshaler):
    def __init__(self, ty: type) -> None:
        super().__init__()

        self._ty = ty

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o.name

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty.__members__[o]  # type: ignore


class OptionalObjMarshaler(ObjMarshaler):
    def __init__(self, item: ObjMarshaler) -> None:
        super().__init__()

        self._item = item

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if o is None:
            return None
        return self._item.marshal(o, ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if o is None:
            return None
        return self._item.unmarshal(o, ctx)


class PrimitiveUnionObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            pt: ta.Tuple[type, ...],
            x: ta.Optional[ObjMarshaler] = None,
    ) -> None:
        super().__init__()

        self._pt = pt
        self._x = x

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if isinstance(o, self._pt):
            return o
        elif self._x is not None:
            return self._x.marshal(o, ctx)
        else:
            raise TypeError(o)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        if isinstance(o, self._pt):
            return o
        elif self._x is not None:
            return self._x.unmarshal(o, ctx)
        else:
            raise TypeError(o)


class LiteralObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            item: ObjMarshaler,
            vs: frozenset,
    ) -> None:
        super().__init__()

        self._item = item
        self._vs = vs

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._item.marshal(check.in_(o, self._vs), ctx)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return check.in_(self._item.unmarshal(o, ctx), self._vs)


class MappingObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            ty: type,
            km: ObjMarshaler,
            vm: ObjMarshaler,
    ) -> None:
        super().__init__()

        self._ty = ty
        self._km = km
        self._vm = vm

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return {self._km.marshal(k, ctx): self._vm.marshal(v, ctx) for k, v in o.items()}

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty((self._km.unmarshal(k, ctx), self._vm.unmarshal(v, ctx)) for k, v in o.items())


class IterableObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            ty: type,
            item: ObjMarshaler,
    ) -> None:
        super().__init__()

        self._ty = ty
        self._item = item

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return [self._item.marshal(e, ctx) for e in o]

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty(self._item.unmarshal(e, ctx) for e in o)


class FieldsObjMarshaler(ObjMarshaler):
    @dc.dataclass(frozen=True)
    class Field:
        att: str
        key: str
        m: ObjMarshaler

        omit_if_none: bool = False

    def __init__(
            self,
            ty: type,
            fs: ta.Sequence[Field],
            *,
            non_strict: bool = False,
    ) -> None:
        super().__init__()

        self._ty = ty
        self._fs = fs
        self._non_strict = non_strict

        fs_by_att: dict = {}
        fs_by_key: dict = {}
        for f in self._fs:
            check.not_in(check.non_empty_str(f.att), fs_by_att)
            check.not_in(check.non_empty_str(f.key), fs_by_key)
            fs_by_att[f.att] = f
            fs_by_key[f.key] = f

        self._fs_by_att: ta.Mapping[str, FieldsObjMarshaler.Field] = fs_by_att
        self._fs_by_key: ta.Mapping[str, FieldsObjMarshaler.Field] = fs_by_key

    @property
    def ty(self) -> type:
        return self._ty

    @property
    def fs(self) -> ta.Sequence[Field]:
        return self._fs

    #

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        d = {}
        for f in self._fs:
            mv = f.m.marshal(getattr(o, f.att), ctx)
            if mv is None and f.omit_if_none:
                continue
            d[f.key] = mv
        return d

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        kw = {}
        for k, v in o.items():
            if (f := self._fs_by_key.get(k)) is None:
                if not (self._non_strict or ctx.options.non_strict_fields):
                    raise KeyError(k)
                continue
            kw[f.att] = f.m.unmarshal(v, ctx)
        return self._ty(**kw)


class SingleFieldObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            ty: type,
            fld: str,
    ) -> None:
        super().__init__()

        self._ty = ty
        self._fld = fld

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return getattr(o, self._fld)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty(**{self._fld: o})


class PolymorphicObjMarshaler(ObjMarshaler):
    class Impl(ta.NamedTuple):
        ty: type
        tag: str
        m: ObjMarshaler

    def __init__(
            self,
            impls_by_ty: ta.Mapping[type, Impl],
            impls_by_tag: ta.Mapping[str, Impl],
    ) -> None:
        super().__init__()

        self._impls_by_ty = impls_by_ty
        self._impls_by_tag = impls_by_tag

    @classmethod
    def of(cls, impls: ta.Iterable[Impl]) -> 'PolymorphicObjMarshaler':
        return cls(
            {i.ty: i for i in impls},
            {i.tag: i for i in impls},
        )

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        impl = self._impls_by_ty[type(o)]
        return {impl.tag: impl.m.marshal(o, ctx)}

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        [(t, v)] = o.items()
        impl = self._impls_by_tag[t]
        return impl.m.unmarshal(v, ctx)


class DatetimeObjMarshaler(ObjMarshaler):
    def __init__(
            self,
            ty: type,
    ) -> None:
        super().__init__()

        self._ty = ty

    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return o.isoformat()

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return self._ty.fromisoformat(o)  # type: ignore


class DecimalObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return str(check.isinstance(o, decimal.Decimal))

    def unmarshal(self, v: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return decimal.Decimal(check.isinstance(v, str))


class FractionObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        fr = check.isinstance(o, fractions.Fraction)
        return [fr.numerator, fr.denominator]

    def unmarshal(self, v: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        num, denom = check.isinstance(v, list)
        return fractions.Fraction(num, denom)


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any, ctx: 'ObjMarshalContext') -> ta.Any:
        return uuid.UUID(o)


##


_DEFAULT_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in (type(None),)},
    **{t: CastObjMarshaler(t) for t in (int, float, str, bool)},
    **{t: BytesSwitchedObjMarshaler(Base64ObjMarshaler(t)) for t in (bytes, bytearray)},
    **{t: IterableObjMarshaler(t, DynamicObjMarshaler()) for t in (list, tuple, set, frozenset)},
    **{t: MappingObjMarshaler(t, DynamicObjMarshaler(), DynamicObjMarshaler()) for t in (dict,)},

    **{t: DynamicObjMarshaler() for t in (ta.Any, object)},

    **{t: DatetimeObjMarshaler(t) for t in (datetime.date, datetime.time, datetime.datetime)},
    decimal.Decimal: DecimalObjMarshaler(),
    fractions.Fraction: FractionObjMarshaler(),
    uuid.UUID: UuidObjMarshaler(),
}

_OBJ_MARSHALER_GENERIC_MAPPING_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (dict,)},
    **{t: dict for t in (collections.abc.Mapping, collections.abc.MutableMapping)},  # noqa
}

_OBJ_MARSHALER_GENERIC_ITERABLE_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (list, tuple, set, frozenset)},
    collections.abc.Set: frozenset,
    collections.abc.MutableSet: set,
    collections.abc.Sequence: tuple,
    collections.abc.MutableSequence: list,
}

_OBJ_MARSHALER_PRIMITIVE_TYPES: ta.Set[type] = {
    int,
    float,
    bool,
    str,
}


##


_REGISTERED_OBJ_MARSHALERS_BY_TYPE: ta.MutableMapping[type, ObjMarshaler] = weakref.WeakKeyDictionary()


def register_type_obj_marshaler(ty: type, om: ObjMarshaler) -> None:
    _REGISTERED_OBJ_MARSHALERS_BY_TYPE[ty] = om


def register_single_field_type_obj_marshaler(fld, ty=None):
    def inner(ty):  # noqa
        register_type_obj_marshaler(ty, SingleFieldObjMarshaler(ty, fld))
        return ty

    if ty is not None:
        return inner(ty)
    else:
        return inner


##


class ObjMarshalerFieldMetadata:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


class OBJ_MARSHALER_FIELD_KEY(ObjMarshalerFieldMetadata):  # noqa
    pass


class OBJ_MARSHALER_OMIT_IF_NONE(ObjMarshalerFieldMetadata):  # noqa
    pass


##


class ObjMarshalerManager(Abstract):
    @abc.abstractmethod
    def make_obj_marshaler(
            self,
            ty: ta.Any,
            rec: ta.Callable[[ta.Any], ObjMarshaler],
            *,
            non_strict_fields: bool = False,
    ) -> ObjMarshaler:
        raise NotImplementedError

    @abc.abstractmethod
    def set_obj_marshaler(
            self,
            ty: ta.Any,
            m: ObjMarshaler,
            *,
            override: bool = False,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_obj_marshaler(
            self,
            ty: ta.Any,
            *,
            no_cache: bool = False,
            **kwargs: ta.Any,
    ) -> ObjMarshaler:
        raise NotImplementedError

    @abc.abstractmethod
    def make_context(self, opts: ta.Optional[ObjMarshalOptions]) -> 'ObjMarshalContext':
        raise NotImplementedError

    #

    def marshal_obj(
            self,
            o: ta.Any,
            ty: ta.Any = None,
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> ta.Any:
        m = self.get_obj_marshaler(ty if ty is not None else type(o))
        return m.marshal(o, self.make_context(opts))

    def unmarshal_obj(
            self,
            o: ta.Any,
            ty: ta.Union[ta.Type[T], ta.Any],
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> T:
        m = self.get_obj_marshaler(ty)
        return m.unmarshal(o, self.make_context(opts))

    def roundtrip_obj(
            self,
            o: ta.Any,
            ty: ta.Any = None,
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> ta.Any:
        if ty is None:
            ty = type(o)
        m: ta.Any = self.marshal_obj(o, ty, opts)
        u: ta.Any = self.unmarshal_obj(m, ty, opts)
        return u


#


class ObjMarshalerManagerImpl(ObjMarshalerManager):
    def __init__(
            self,
            *,
            default_options: ObjMarshalOptions = ObjMarshalOptions(),

            default_obj_marshalers: ta.Dict[ta.Any, ObjMarshaler] = _DEFAULT_OBJ_MARSHALERS,  # noqa
            generic_mapping_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES,  # noqa
            generic_iterable_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_ITERABLE_TYPES,  # noqa

            registered_obj_marshalers: ta.Mapping[type, ObjMarshaler] = _REGISTERED_OBJ_MARSHALERS_BY_TYPE,
    ) -> None:
        super().__init__()

        self._default_options = default_options

        self._obj_marshalers = dict(default_obj_marshalers)
        self._generic_mapping_types = generic_mapping_types
        self._generic_iterable_types = generic_iterable_types
        self._registered_obj_marshalers = registered_obj_marshalers

        self._lock = threading.RLock()
        self._marshalers: ta.Dict[ta.Any, ObjMarshaler] = dict(_DEFAULT_OBJ_MARSHALERS)
        self._proxies: ta.Dict[ta.Any, ProxyObjMarshaler] = {}

    #

    @classmethod
    def _is_abstract(cls, ty: type) -> bool:
        return abc.ABC in ty.__bases__ or Abstract in ty.__bases__

    #

    def make_obj_marshaler(
            self,
            ty: ta.Any,
            rec: ta.Callable[[ta.Any], ObjMarshaler],
            *,
            non_strict_fields: bool = False,
    ) -> ObjMarshaler:
        if isinstance(ty, type):
            if (reg := self._registered_obj_marshalers.get(ty)) is not None:
                return reg

            if self._is_abstract(ty):
                tn = ty.__name__
                impls: ta.List[ta.Tuple[type, str]] = [  # type: ignore[var-annotated]
                    (ity, ity.__name__)
                    for ity in deep_subclasses(ty)
                    if not self._is_abstract(ity)
                ]

                if all(itn.endswith(tn) for _, itn in impls):
                    impls = [
                        (ity, snake_case(itn[:-len(tn)]))
                        for ity, itn in impls
                    ]

                dupe_tns = sorted(
                    dn
                    for dn, dc in collections.Counter(itn for _, itn in impls).items()
                    if dc > 1
                )
                if dupe_tns:
                    raise KeyError(f'Duplicate impl names for {ty}: {dupe_tns}')

                return PolymorphicObjMarshaler.of([
                    PolymorphicObjMarshaler.Impl(
                        ity,
                        itn,
                        rec(ity),
                    )
                    for ity, itn in impls
                ])

            if issubclass(ty, enum.Enum):
                return EnumObjMarshaler(ty)

            if dc.is_dataclass(ty):
                return FieldsObjMarshaler(
                    ty,
                    [
                        FieldsObjMarshaler.Field(
                            att=f.name,
                            key=check.non_empty_str(fk),
                            m=rec(f.type),
                            omit_if_none=check.isinstance(f.metadata.get(OBJ_MARSHALER_OMIT_IF_NONE, False), bool),
                        )
                        for f in dc.fields(ty)
                        if (fk := f.metadata.get(OBJ_MARSHALER_FIELD_KEY, f.name)) is not None
                    ],
                    non_strict=non_strict_fields,
                )

            if issubclass(ty, tuple) and hasattr(ty, '_fields'):
                return FieldsObjMarshaler(
                    ty,
                    [
                        FieldsObjMarshaler.Field(
                            att=p.name,
                            key=p.name,
                            m=rec(p.annotation),
                        )
                        for p in inspect.signature(ty).parameters.values()
                    ],
                    non_strict=non_strict_fields,
                )

        if is_new_type(ty):
            return rec(get_new_type_supertype(ty))

        if is_literal_type(ty):
            lvs = frozenset(get_literal_type_args(ty))
            if None in lvs:
                is_opt = True
                lvs -= frozenset([None])
            else:
                is_opt = False
            lty = check.single(set(map(type, lvs)))
            lm: ObjMarshaler = LiteralObjMarshaler(rec(lty), lvs)
            if is_opt:
                lm = OptionalObjMarshaler(lm)
            return lm

        if is_generic_alias(ty):
            try:
                mt = self._generic_mapping_types[ta.get_origin(ty)]
            except KeyError:
                pass
            else:
                k, v = ta.get_args(ty)
                return MappingObjMarshaler(mt, rec(k), rec(v))

            try:
                st = self._generic_iterable_types[ta.get_origin(ty)]
            except KeyError:
                pass
            else:
                [e] = ta.get_args(ty)
                return IterableObjMarshaler(st, rec(e))

        if is_union_alias(ty):
            uts = frozenset(ta.get_args(ty))
            if None in uts or type(None) in uts:
                is_opt = True
                uts = frozenset(ut for ut in uts if ut not in (None, type(None)))
            else:
                is_opt = False

            um: ObjMarshaler
            if not uts:
                raise TypeError(ty)
            elif len(uts) == 1:
                um = rec(check.single(uts))
            else:
                pt = tuple({ut for ut in uts if ut in _OBJ_MARSHALER_PRIMITIVE_TYPES})
                np_uts = {ut for ut in uts if ut not in _OBJ_MARSHALER_PRIMITIVE_TYPES}
                if not np_uts:
                    um = PrimitiveUnionObjMarshaler(pt)
                elif len(np_uts) == 1:
                    um = PrimitiveUnionObjMarshaler(pt, x=rec(check.single(np_uts)))
                else:
                    raise TypeError(ty)

            if is_opt:
                um = OptionalObjMarshaler(um)
            return um

        raise TypeError(ty)

    #

    def set_obj_marshaler(
            self,
            ty: ta.Any,
            m: ObjMarshaler,
            *,
            override: bool = False,
    ) -> None:
        with self._lock:
            if not override and ty in self._obj_marshalers:
                raise KeyError(ty)
            self._obj_marshalers[ty] = m

    def get_obj_marshaler(
            self,
            ty: ta.Any,
            *,
            no_cache: bool = False,
            **kwargs: ta.Any,
    ) -> ObjMarshaler:
        with self._lock:
            if not no_cache:
                try:
                    return self._obj_marshalers[ty]
                except KeyError:
                    pass

            try:
                return self._proxies[ty]
            except KeyError:
                pass

            rec = functools.partial(
                self.get_obj_marshaler,
                no_cache=no_cache,
                **kwargs,
            )

            p = ProxyObjMarshaler()
            self._proxies[ty] = p
            try:
                m = self.make_obj_marshaler(ty, rec, **kwargs)
            finally:
                del self._proxies[ty]
            p._m = m  # noqa

            if not no_cache:
                self._obj_marshalers[ty] = m
            return m

    def make_context(self, opts: ta.Optional[ObjMarshalOptions]) -> 'ObjMarshalContext':
        return ObjMarshalContext(
            options=opts or self._default_options,
            manager=self,
        )


def new_obj_marshaler_manager(**kwargs: ta.Any) -> ObjMarshalerManager:
    return ObjMarshalerManagerImpl(**kwargs)


##


@dc.dataclass(frozen=True)
class ObjMarshalContext:
    options: ObjMarshalOptions
    manager: ObjMarshalerManager


##


OBJ_MARSHALER_MANAGER = new_obj_marshaler_manager()

set_obj_marshaler = OBJ_MARSHALER_MANAGER.set_obj_marshaler
get_obj_marshaler = OBJ_MARSHALER_MANAGER.get_obj_marshaler

marshal_obj = OBJ_MARSHALER_MANAGER.marshal_obj
unmarshal_obj = OBJ_MARSHALER_MANAGER.unmarshal_obj


########################################
# ../../../omlish/lite/maybes.py


##


@functools.total_ordering
class Maybe(ta.Generic[T]):
    class ValueNotPresentError(BaseException):
        pass

    #

    @property
    @abc.abstractmethod
    def present(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def must(self) -> T:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        raise NotImplementedError

    #

    @ta.final
    def __ne__(self, other):
        return not (self == other)

    @ta.final
    def __iter__(self) -> ta.Iterator[T]:
        if self.present:
            yield self.must()

    @ta.final
    def __bool__(self) -> ta.NoReturn:
        raise TypeError

    #

    @ta.final
    def if_present(self, consumer: ta.Callable[[T], None]) -> None:
        if self.present:
            consumer(self.must())

    @ta.final
    def filter(self, predicate: ta.Callable[[T], bool]) -> 'Maybe[T]':
        if self.present and predicate(self.must()):
            return self
        else:
            return Maybe.empty()

    @ta.final
    def map(self, mapper: ta.Callable[[T], U]) -> 'Maybe[U]':
        if self.present:
            return Maybe.just(mapper(self.must()))
        else:
            return Maybe.empty()

    @ta.final
    def flat_map(self, mapper: ta.Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self.present:
            if not isinstance(v := mapper(self.must()), Maybe):
                raise TypeError(v)
            return v
        else:
            return Maybe.empty()

    @ta.final
    def or_else(self, other: ta.Union[T, U]) -> ta.Union[T, U]:
        if self.present:
            return self.must()
        else:
            return other

    @ta.final
    def or_none(self) -> ta.Optional[T]:
        if self.present:
            return self.must()
        else:
            return None

    @ta.final
    def or_else_get(self, supplier: ta.Callable[[], ta.Union[T, U]]) -> ta.Union[T, U]:
        if self.present:
            return self.must()
        else:
            return supplier()

    @ta.final
    def or_else_raise(self, exception_supplier: ta.Callable[[], Exception]) -> T:
        if self.present:
            return self.must()
        else:
            raise exception_supplier()

    #

    @classmethod
    def of_optional(cls, v: ta.Optional[T]) -> 'Maybe[T]':
        if v is not None:
            return cls.just(v)
        else:
            return cls.empty()

    @classmethod
    def just(cls, v: T) -> 'Maybe[T]':
        return _JustMaybe(v)

    _empty: ta.ClassVar['Maybe']

    @classmethod
    def empty(cls) -> 'Maybe[T]':
        return Maybe._empty


##


class _Maybe(Maybe[T], Abstract):
    def __lt__(self, other):
        if not isinstance(other, _Maybe):
            return NotImplemented
        sp = self.present
        op = other.present
        if self.present and other.present:
            return self.must() < other.must()
        else:
            return op and not sp


@ta.final
class _JustMaybe(_Maybe[T]):
    __slots__ = ('_v', '_hash')

    def __init__(self, v: T) -> None:
        self._v = v

    @property
    def present(self) -> bool:
        return True

    def must(self) -> T:
        return self._v

    #

    def __repr__(self) -> str:
        return f'just({self._v!r})'

    _hash: int

    def __hash__(self) -> int:
        try:
            return self._hash
        except AttributeError:
            pass
        h = self._hash = hash((_JustMaybe, self._v))
        return h

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and
            self._v == other._v  # noqa
        )


@ta.final
class _EmptyMaybe(_Maybe[T]):
    __slots__ = ()

    @property
    def present(self) -> bool:
        return False

    def must(self) -> T:
        raise Maybe.ValueNotPresentError

    #

    def __repr__(self) -> str:
        return 'empty()'

    def __hash__(self) -> int:
        return hash(_EmptyMaybe)

    def __eq__(self, other):
        return self.__class__ is other.__class__


Maybe._empty = _EmptyMaybe()  # noqa


##


setattr(Maybe, 'just', _JustMaybe)  # noqa
setattr(Maybe, 'empty', functools.partial(operator.attrgetter('_empty'), Maybe))


########################################
# ../../../omlish/lite/runtime.py


##


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


LITE_REQUIRED_PYTHON_VERSION = (3, 8)


def check_lite_runtime_version() -> None:
    if sys.version_info < LITE_REQUIRED_PYTHON_VERSION:
        raise OSError(f'Requires python {LITE_REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../../../omlish/lite/timeouts.py
"""
TODO:
 - Event (/ Predicate)
"""


##


class Timeout(Abstract):
    @property
    @abc.abstractmethod
    def can_expire(self) -> bool:
        """Indicates whether or not this timeout will ever expire."""

        raise NotImplementedError

    @abc.abstractmethod
    def expired(self) -> bool:
        """Return whether or not this timeout has expired."""

        raise NotImplementedError

    @abc.abstractmethod
    def remaining(self) -> float:
        """Returns the time (in seconds) remaining until the timeout expires. May be negative and/or infinite."""

        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self) -> float:
        """Returns the time (in seconds) remaining until the timeout expires, or raises if the timeout has expired."""

        raise NotImplementedError

    @abc.abstractmethod
    def or_(self, o: ta.Any) -> ta.Any:
        """Evaluates time remaining via remaining() if this timeout can expire, otherwise returns `o`."""

        raise NotImplementedError

    #

    @classmethod
    def _now(cls) -> float:
        return time.monotonic()

    #

    class DEFAULT:  # Noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    class _NOT_SPECIFIED:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    @classmethod
    def of(
            cls,
            obj: TimeoutLike,
            default: ta.Union[TimeoutLike, ta.Type[_NOT_SPECIFIED]] = _NOT_SPECIFIED,
    ) -> 'Timeout':
        if isinstance(obj, bool):
            if obj:
                obj = Timeout.DEFAULT
            else:
                obj = None

        if obj is None:
            return InfiniteTimeout()

        if isinstance(obj, Timeout):
            return obj

        if isinstance(obj, (float, int)):
            return DeadlineTimeout(cls._now() + obj)

        # if isinstance(obj, CanInt):
        #     return DeadlineTimeout(cls._now() + int(obj))

        if isinstance(obj, CanFloat):
            return DeadlineTimeout(cls._now() + float(obj))

        if isinstance(obj, ta.Iterable):
            return CompositeTimeout(*[Timeout.of(c) for c in obj])

        if obj is Timeout.DEFAULT:
            if default is Timeout._NOT_SPECIFIED or default is Timeout.DEFAULT:
                raise RuntimeError('Must specify a default timeout')

            else:
                return Timeout.of(default)  # type: ignore[arg-type]

        raise TypeError(obj)

    @classmethod
    def of_deadline(cls, deadline: float) -> 'DeadlineTimeout':
        return DeadlineTimeout(deadline)

    @classmethod
    def of_predicate(cls, expired_fn: ta.Callable[[], bool]) -> 'PredicateTimeout':
        return PredicateTimeout(expired_fn)


class DeadlineTimeout(Timeout):
    def __init__(
            self,
            deadline: float,
            exc: ta.Union[ta.Type[BaseException], BaseException] = TimeoutError,
    ) -> None:
        super().__init__()

        self.deadline = deadline
        self.exc = exc

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.deadline!r}, {self.exc!r})'

    @property
    def can_expire(self) -> bool:
        return True

    def expired(self) -> bool:
        return not (self.remaining() > 0)

    def remaining(self) -> float:
        return self.deadline - self._now()

    def __call__(self) -> float:
        if (rem := self.remaining()) > 0:
            return rem
        raise self.exc

    def or_(self, o: ta.Any) -> ta.Any:
        return self()


class InfiniteTimeout(Timeout):
    def __repr__(self) -> str:
        return f'{type(self).__name__}()'

    @property
    def can_expire(self) -> bool:
        return False

    def expired(self) -> bool:
        return False

    def remaining(self) -> float:
        return float('inf')

    def __call__(self) -> float:
        return float('inf')

    def or_(self, o: ta.Any) -> ta.Any:
        return o


class CompositeTimeout(Timeout):
    def __init__(self, *children: Timeout) -> None:
        super().__init__()

        self.children = children

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.children!r})'

    @property
    def can_expire(self) -> bool:
        return any(c.can_expire for c in self.children)

    def expired(self) -> bool:
        return any(c.expired() for c in self.children)

    def remaining(self) -> float:
        return min(c.remaining() for c in self.children)

    def __call__(self) -> float:
        return min(c() for c in self.children)

    def or_(self, o: ta.Any) -> ta.Any:
        if self.can_expire:
            return self()
        return o


class PredicateTimeout(Timeout):
    def __init__(
            self,
            expired_fn: ta.Callable[[], bool],
            exc: ta.Union[ta.Type[BaseException], BaseException] = TimeoutError,
    ) -> None:
        super().__init__()

        self.expired_fn = expired_fn
        self.exc = exc

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.expired_fn!r}, {self.exc!r})'

    @property
    def can_expire(self) -> bool:
        return True

    def expired(self) -> bool:
        return self.expired_fn()

    def remaining(self) -> float:
        return float('inf')

    def __call__(self) -> float:
        if not self.expired_fn():
            return float('inf')
        raise self.exc

    def or_(self, o: ta.Any) -> ta.Any:
        return self()


########################################
# ../../../omlish/logs/infos.py
"""
TODO:
 - remove redundant info fields only present for std adaptation (Level.name, ...)
"""


##


def logging_context_info(cls):
    return cls


@ta.final
class LoggingContextInfos:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    @logging_context_info
    @ta.final
    class Name(ta.NamedTuple):
        name: str

    @logging_context_info
    @ta.final
    class Level(ta.NamedTuple):
        level: NamedLogLevel
        name: str

        @classmethod
        def build(cls, level: int) -> 'LoggingContextInfos.Level':
            nl: NamedLogLevel = level if level.__class__ is NamedLogLevel else NamedLogLevel(level)  # type: ignore[assignment]  # noqa
            return cls(
                level=nl,
                name=logging.getLevelName(nl),
            )

    @logging_context_info
    @ta.final
    class Msg(ta.NamedTuple):
        msg: str
        args: ta.Union[tuple, ta.Mapping[ta.Any, ta.Any], None]

        @classmethod
        def build(
                cls,
                msg: ta.Union[str, tuple, LoggingMsgFn],
                *args: ta.Any,
        ) -> 'LoggingContextInfos.Msg':
            s: str
            a: ta.Any

            if callable(msg):
                if args:
                    raise TypeError(f'Must not provide both a message function and args: {msg=} {args=}')
                x = msg()
                if isinstance(x, str):
                    s, a = x, ()
                elif isinstance(x, tuple):
                    if x:
                        s, a = x[0], x[1:]
                    else:
                        s, a = '', ()
                else:
                    raise TypeError(x)

            elif isinstance(msg, tuple):
                if args:
                    raise TypeError(f'Must not provide both a tuple message and args: {msg=} {args=}')
                if msg:
                    s, a = msg[0], msg[1:]
                else:
                    s, a = '', ()

            elif isinstance(msg, str):
                s, a = msg, args

            else:
                raise TypeError(msg)

            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L307  # noqa
            if a and len(a) == 1 and isinstance(a[0], collections.abc.Mapping) and a[0]:
                a = a[0]

            return cls(
                msg=s,
                args=a,
            )

    @logging_context_info
    @ta.final
    class Extra(ta.NamedTuple):
        extra: ta.Mapping[ta.Any, ta.Any]

    @logging_context_info
    @ta.final
    class Time(ta.NamedTuple):
        ns: int
        secs: float
        msecs: float
        relative_secs: float

        @classmethod
        def get_std_start_ns(cls) -> int:
            x: ta.Any = logging._startTime  # type: ignore[attr-defined]  # noqa

            # Before 3.13.0b1 this will be `time.time()`, a float of seconds. After that, it will be `time.time_ns()`,
            # an int.
            #
            # See:
            #  - https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
            #
            if isinstance(x, float):
                return int(x * 1e9)
            else:
                return x

        @classmethod
        def build(
                cls,
                ns: int,
                *,
                start_ns: ta.Optional[int] = None,
        ) -> 'LoggingContextInfos.Time':
            # https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
            secs = ns / 1e9  # ns to float seconds

            # Get the number of whole milliseconds (0-999) in the fractional part of seconds.
            # Eg: 1_677_903_920_999_998_503 ns --> 999_998_503 ns--> 999 ms
            # Convert to float by adding 0.0 for historical reasons. See gh-89047
            msecs = (ns % 1_000_000_000) // 1_000_000 + 0.0

            # https://github.com/python/cpython/commit/1500a23f33f5a6d052ff1ef6383d9839928b8ff1
            if msecs == 999.0 and int(secs) != ns // 1_000_000_000:
                # ns -> sec conversion can round up, e.g:
                # 1_677_903_920_999_999_900 ns --> 1_677_903_921.0 sec
                msecs = 0.0

            if start_ns is None:
                start_ns = cls.get_std_start_ns()
            relative_secs = (ns - start_ns) / 1e6

            return cls(
                ns=ns,
                secs=secs,
                msecs=msecs,
                relative_secs=relative_secs,
            )

    @logging_context_info
    @ta.final
    class Exc(ta.NamedTuple):
        info: LoggingExcInfo
        info_tuple: LoggingExcInfoTuple

        @classmethod
        def build(
                cls,
                arg: LoggingExcInfoArg = False,
        ) -> ta.Optional['LoggingContextInfos.Exc']:
            if arg is True:
                sys_exc_info = sys.exc_info()
                if sys_exc_info[0] is not None:
                    arg = sys_exc_info
                else:
                    arg = None
            elif arg is False:
                arg = None
            if arg is None:
                return None

            info: LoggingExcInfo = arg
            if isinstance(info, BaseException):
                info_tuple: LoggingExcInfoTuple = (type(info), info, info.__traceback__)  # noqa
            else:
                info_tuple = info

            return cls(
                info=info,
                info_tuple=info_tuple,
            )

    @logging_context_info
    @ta.final
    class Caller(ta.NamedTuple):
        file_path: str
        line_no: int
        func_name: str
        stack_info: ta.Optional[str]

        @classmethod
        def is_internal_frame(cls, frame: types.FrameType) -> bool:
            file_path = os.path.normcase(frame.f_code.co_filename)

            # Yes, really.
            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L204  # noqa
            # https://github.com/python/cpython/commit/5ca6d7469be53960843df39bb900e9c3359f127f
            if 'importlib' in file_path and '_bootstrap' in file_path:
                return True

            return False

        @classmethod
        def find_frame(cls, stack_offset: int = 0) -> ta.Optional[types.FrameType]:
            f: ta.Optional[types.FrameType] = sys._getframe(2 + stack_offset)  # noqa

            while f is not None:
                # NOTE: We don't check __file__ like stdlib since we may be running amalgamated - we rely on careful,
                # manual stack_offset management.
                if hasattr(f, 'f_code'):
                    return f

                f = f.f_back

            return None

        @classmethod
        def build(
                cls,
                stack_offset: int = 0,
                *,
                stack_info: bool = False,
        ) -> ta.Optional['LoggingContextInfos.Caller']:
            if (f := cls.find_frame(stack_offset + 1)) is None:
                return None

            # https://github.com/python/cpython/blob/08e9794517063c8cd92c48714071b1d3c60b71bd/Lib/logging/__init__.py#L1616-L1623  # noqa
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                sio.close()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]

            return cls(
                file_path=f.f_code.co_filename,
                line_no=f.f_lineno or 0,
                func_name=f.f_code.co_name,
                stack_info=sinfo,
            )

    @logging_context_info
    @ta.final
    class SourceFile(ta.NamedTuple):
        file_name: str
        module: str

        @classmethod
        def build(cls, caller_file_path: ta.Optional[str]) -> ta.Optional['LoggingContextInfos.SourceFile']:
            if caller_file_path is None:
                return None

            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L331-L336  # noqa
            try:
                file_name = os.path.basename(caller_file_path)
                module = os.path.splitext(file_name)[0]
            except (TypeError, ValueError, AttributeError):
                return None

            return cls(
                file_name=file_name,
                module=module,
            )

    @logging_context_info
    @ta.final
    class Thread(ta.NamedTuple):
        ident: int
        native_id: ta.Optional[int]
        name: str

        @classmethod
        def build(cls) -> 'LoggingContextInfos.Thread':
            return cls(
                ident=threading.get_ident(),
                native_id=threading.get_native_id() if hasattr(threading, 'get_native_id') else None,
                name=threading.current_thread().name,
            )

    @logging_context_info
    @ta.final
    class Process(ta.NamedTuple):
        pid: int

        @classmethod
        def build(cls) -> 'LoggingContextInfos.Process':
            return cls(
                pid=os.getpid(),
            )

    @logging_context_info
    @ta.final
    class Multiprocessing(ta.NamedTuple):
        process_name: str

        @classmethod
        def build(cls) -> ta.Optional['LoggingContextInfos.Multiprocessing']:
            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L355-L364  # noqa
            if (mp := sys.modules.get('multiprocessing')) is None:
                return None

            return cls(
                process_name=mp.current_process().name,
            )

    @logging_context_info
    @ta.final
    class AsyncioTask(ta.NamedTuple):
        name: str

        @classmethod
        def build(cls) -> ta.Optional['LoggingContextInfos.AsyncioTask']:
            # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L372-L377  # noqa
            if (asyncio := sys.modules.get('asyncio')) is None:
                return None

            try:
                task = asyncio.current_task()
            except Exception:  # noqa
                return None

            if task is None:
                return None

            return cls(
                name=task.get_name(),  # Always non-None
            )


##


class UnexpectedLoggingStartTimeWarning(LoggingSetupWarning):
    pass


def _check_logging_start_time() -> None:
    if (x := LoggingContextInfos.Time.get_std_start_ns()) < (t := time.time()):
        import warnings  # noqa

        warnings.warn(
            f'Unexpected logging start time detected: '
            f'get_std_start_ns={x}, '
            f'time.time()={t}',
            UnexpectedLoggingStartTimeWarning,
        )


_check_logging_start_time()


########################################
# ../../../omlish/logs/metrics/base.py


##


class LoggerMetricUnit(Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            mut = LOGGER_METRIC_UNIT_TYPES
        except NameError:
            pass
        else:
            bcs = [bc for bc in mut if issubclass(cls, bc)]
            if len(bcs) != 1:
                raise TypeError(f'{cls.__name__} must be a subclass of exactly one of {mut}, got {bcs}.')

        try:
            mtc = LoggerMetric
        except NameError:
            pass
        else:
            if issubclass(cls, mtc):
                mp = cls.__mro__.index(mtc)
                mup = cls.__mro__.index(LoggerMetricUnit)
                if mup > mp:
                    raise TypeError(f'{cls.__name__} must have Metric before MetricUnit in its MRO.')


class CountLoggerMetricUnit(LoggerMetricUnit):
    @classmethod
    def default_value(cls) -> ta.Optional[float]:
        return 1


class RatioLoggerMetricUnit(LoggerMetricUnit):
    pass


class SecondsLoggerMetricUnit(LoggerMetricUnit):
    pass


class BytesLoggerMetricUnit(LoggerMetricUnit):
    pass


LOGGER_METRIC_UNIT_TYPES: ta.Tuple[ta.Type[LoggerMetricUnit], ...] = (
    CountLoggerMetricUnit,
    RatioLoggerMetricUnit,
    SecondsLoggerMetricUnit,
    BytesLoggerMetricUnit,
)


##


class LoggerMetricTag(Abstract):
    pass


##


class LoggerMetric(Abstract):
    @ta.final
    def __init__(self, value: ta.Optional[float] = None, *tags: LoggerMetricTag) -> None:
        if value is None:
            value = self.default_value()
        if value is None:
            raise ValueError(f'{type(self).__name__} has no default value.')

        self.__value = value
        self.__tags = tags

    @property
    def value(self) -> float:
        return self.__value

    @classmethod
    def default_value(cls) -> ta.Optional[float]:
        return None

    @property
    def tags(self) -> ta.Sequence[LoggerMetricTag]:
        return self.__tags

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.value!r}, {", ".join(map(repr, self.tags))})'

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            mtt = LOGGER_METRIC_TYPES
        except NameError:
            pass
        else:
            bcs = [bc for bc in mtt if issubclass(cls, bc)]
            if Abstract in cls.__bases__:
                if len(bcs) > 1:
                    raise TypeError(f'{cls.__name__} must be a subclass of at most one of {mtt}, got {bcs}.')
            else:
                if len(bcs) != 1:
                    raise TypeError(f'{cls.__name__} must be a subclass of exactly one of {mtt}, got {bcs}.')

        # if Abstract not in cls.__bases__ and not issubclass(cls, LoggerMetricUnit):
        #     raise TypeError(f'{cls.__name__} must be a subclass of LoggerMetricUnit.')


class CounterLoggerMetric(CountLoggerMetricUnit, LoggerMetric, Abstract):
    pass


class GaugeLoggerMetric(LoggerMetric, Abstract):
    pass


class HistogramLoggerMetric(LoggerMetric, Abstract):
    pass


LOGGER_METRIC_TYPES: ta.Tuple[ta.Type[LoggerMetric], ...] = (
    CounterLoggerMetric,
    GaugeLoggerMetric,
    HistogramLoggerMetric,
)


##


class AnyLoggerMetricCollector(Abstract, ta.Generic[T]):
    @ta.final
    def metric(self, m: LoggerMetric) -> T:
        return self._metric(m)

    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> T:
        raise NotImplementedError


class LoggerMetricCollector(AnyLoggerMetricCollector[None], Abstract):
    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> None:
        raise NotImplementedError


class AsyncLoggerMetricCollector(AnyLoggerMetricCollector[ta.Awaitable[None]], Abstract):
    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class AnyNopLoggerMetricCollector(AnyLoggerMetricCollector[T], Abstract):
    pass


class NopLoggerMetricCollector(AnyNopLoggerMetricCollector[None], LoggerMetricCollector):
    @ta.final
    def _metric(self, m: LoggerMetric) -> None:
        pass


class AsyncNopLoggerMetricCollector(AnyNopLoggerMetricCollector[ta.Awaitable[None]], AsyncLoggerMetricCollector):
    @ta.final
    async def _metric(self, m: LoggerMetric) -> None:
        pass


########################################
# ../../../omlish/logs/protocols.py


##


@ta.runtime_checkable
class LoggerLike(ta.Protocol):
    """Satisfied by both our Logger and stdlib logging.Logger."""

    def isEnabledFor(self, level: LogLevel) -> bool: ...  # noqa

    def getEffectiveLevel(self) -> LogLevel: ...  # noqa

    #

    def log(self, level: LogLevel, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def debug(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def info(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def warning(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def error(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def exception(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa

    def critical(self, msg: str, /, *args: ta.Any, **kwargs: ta.Any) -> None: ...  # noqa


########################################
# ../../../omlish/logs/std/json.py
"""
TODO:
 - translate json keys
"""


##


class JsonLoggingFormatter(logging.Formatter):
    KEYS: ta.Mapping[str, bool] = {
        'name': False,
        'msg': False,
        'args': False,
        'levelname': False,
        'levelno': False,
        'pathname': False,
        'filename': False,
        'module': False,
        'exc_info': True,
        'exc_text': True,
        'stack_info': True,
        'lineno': False,
        'funcName': False,
        'created': False,
        'msecs': False,
        'relativeCreated': False,
        'thread': False,
        'threadName': False,
        'processName': False,
        'process': False,
    }

    def __init__(
            self,
            *args: ta.Any,
            json_dumps: ta.Optional[ta.Callable[[ta.Any], str]] = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        if json_dumps is None:
            json_dumps = json_dumps_compact
        self._json_dumps = json_dumps

    def format(self, record: logging.LogRecord) -> str:
        dct = {
            k: v
            for k, o in self.KEYS.items()
            for v in [getattr(record, k)]
            if not (o and v is None)
        }
        return self._json_dumps(dct)


########################################
# ../../../omlish/os/temp.py


##


def make_temp_file(**kwargs: ta.Any) -> str:
    file_fd, file = tempfile.mkstemp(**kwargs)
    os.close(file_fd)
    return file


@contextlib.contextmanager
def temp_file_context(**kwargs: ta.Any) -> ta.Iterator[str]:
    path = make_temp_file(**kwargs)
    try:
        yield path
    finally:
        unlink_if_exists(path)


@contextlib.contextmanager
def temp_dir_context(
        root_dir: ta.Optional[str] = None,
        **kwargs: ta.Any,
) -> ta.Iterator[str]:
    path = tempfile.mkdtemp(dir=root_dir, **kwargs)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@contextlib.contextmanager
def temp_named_file_context(
        root_dir: ta.Optional[str] = None,
        cleanup: bool = True,
        **kwargs: ta.Any,
) -> ta.Iterator[tempfile._TemporaryFileWrapper]:  # noqa
    with tempfile.NamedTemporaryFile(dir=root_dir, delete=False, **kwargs) as f:
        try:
            yield f
        finally:
            if cleanup:
                shutil.rmtree(f.name, ignore_errors=True)


########################################
# ../../../omlish/sockets/bind.py
"""
TODO:
 - def parse: (<bind>)?:<port>, unix://, fd://
 - unix chown/chgrp
 - DupSocketBinder
 - udp
"""


##


class SocketBinder(Abstract, ta.Generic[SocketBinderConfigT]):
    @dc.dataclass(frozen=True)
    class Config:
        listen_backlog: int = 5

        allow_reuse_address: bool = True
        allow_reuse_port: bool = True

        set_inheritable: bool = False

        #

        @classmethod
        def of(cls, obj: CanSocketBinderConfig) -> 'SocketBinder.Config':
            if isinstance(obj, SocketBinder.Config):
                return obj

            elif isinstance(obj, int):
                return TcpSocketBinder.Config(
                    port=obj,
                )

            elif isinstance(obj, tuple):
                host, port = obj
                return TcpSocketBinder.Config(
                    host=host,
                    port=port,
                )

            elif isinstance(obj, str):
                return UnixSocketBinder.Config(
                    file=obj,
                )

            else:
                raise TypeError(obj)

    #

    def __init__(self, config: SocketBinderConfigT) -> None:
        super().__init__()

        self._config = config

    #

    @classmethod
    def of(cls, obj: CanSocketBinder) -> 'SocketBinder':
        if isinstance(obj, SocketBinder):
            return obj

        config: SocketBinder.Config
        if isinstance(obj, SocketBinder.Config):
            config = obj

        else:
            config = SocketBinder.Config.of(obj)

        if isinstance(config, TcpSocketBinder.Config):
            return TcpSocketBinder(config)

        elif isinstance(config, UnixSocketBinder.Config):
            return UnixSocketBinder(config)

        else:
            raise TypeError(config)

    #

    class Error(RuntimeError):
        pass

    class NotBoundError(Error):
        pass

    class AlreadyBoundError(Error):
        pass

    #

    @property
    @abc.abstractmethod
    def address_family(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def address(self) -> SocketAddress:
        raise NotImplementedError

    #

    _socket: socket_.socket

    @property
    def is_bound(self) -> bool:
        return hasattr(self, '_socket')

    @property
    def socket(self) -> socket_.socket:
        try:
            return self._socket
        except AttributeError:
            raise self.NotBoundError from None

    _name: str

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            raise self.NotBoundError from None

    _port: ta.Optional[int]

    @property
    def port(self) -> ta.Optional[int]:
        try:
            return self._port
        except AttributeError:
            raise self.NotBoundError from None

    #

    def fileno(self) -> int:
        return self.socket.fileno()

    #

    def __enter__(self: SocketBinderT) -> SocketBinderT:
        self.bind()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    #

    def _init_socket(self) -> None:
        if hasattr(self, '_socket'):
            raise self.AlreadyBoundError

        sock = socket_.socket(self.address_family, socket_.SOCK_STREAM)
        self._socket = sock

        if self._config.allow_reuse_address and hasattr(socket_, 'SO_REUSEADDR'):
            sock.setsockopt(socket_.SOL_SOCKET, socket_.SO_REUSEADDR, 1)

        # Since Linux 6.12.9, SO_REUSEPORT is not allowed on other address families than AF_INET/AF_INET6.
        if (
                self._config.allow_reuse_port and hasattr(socket_, 'SO_REUSEPORT') and
                self.address_family in (socket_.AF_INET, socket_.AF_INET6)
        ):
            try:
                sock.setsockopt(socket_.SOL_SOCKET, socket_.SO_REUSEPORT, 1)
            except OSError as err:
                if err.errno not in (errno.ENOPROTOOPT, errno.EINVAL):
                    raise

        if self._config.set_inheritable and hasattr(sock, 'set_inheritable'):
            sock.set_inheritable(True)

    def _pre_bind(self) -> None:
        pass

    def _post_bind(self) -> None:
        pass

    def bind(self) -> None:
        self._init_socket()

        self._pre_bind()

        self.socket.bind(self.address)

        self._post_bind()

        check.state(all(hasattr(self, a) for a in ('_socket', '_name', '_port')))

    #

    def close(self) -> None:
        if hasattr(self, '_socket'):
            self._socket.close()

    #

    def listen(self) -> None:
        self.socket.listen(self._config.listen_backlog)

    @abc.abstractmethod
    def accept(self, sock: ta.Optional[socket_.socket] = None) -> SocketAndAddress:
        raise NotImplementedError


##


class TcpSocketBinder(SocketBinder):
    @dc.dataclass(frozen=True)
    class Config(SocketBinder.Config):
        DEFAULT_HOST: ta.ClassVar[str] = 'localhost'
        host: str = DEFAULT_HOST

        port: int = 0

        def __post_init__(self) -> None:
            dataclass_maybe_post_init(super())
            check.non_empty_str(self.host)
            check.isinstance(self.port, int)
            check.arg(self.port > 0)

    def __init__(self, config: Config) -> None:
        super().__init__(check.isinstance(config, self.Config))

        self._address = (config.host, config.port)

    #

    address_family = socket_.AF_INET

    @property
    def address(self) -> SocketAddress:
        return self._address

    #

    def _post_bind(self) -> None:
        super()._post_bind()

        host, port, *_ = self.socket.getsockname()

        self._name = socket_.getfqdn(host)
        self._port = port

    #

    def accept(self, sock: ta.Optional[socket_.socket] = None) -> SocketAndAddress:
        if sock is None:
            sock = self.socket

        conn, client_address = sock.accept()
        return SocketAndAddress(conn, client_address)


##


class UnixSocketBinder(SocketBinder):
    @dc.dataclass(frozen=True)
    class Config(SocketBinder.Config):
        file: str = ''

        unlink: bool = False

        def __post_init__(self) -> None:
            dataclass_maybe_post_init(super())
            check.non_empty_str(self.file)

    def __init__(self, config: Config) -> None:
        super().__init__(check.isinstance(config, self.Config))

        self._address = config.file

    #

    address_family = socket_.AF_UNIX

    @property
    def address(self) -> SocketAddress:
        return self._address

    #

    def _pre_bind(self) -> None:
        super()._pre_bind()

        if self._config.unlink:
            try:
                if stat.S_ISSOCK(os.stat(self._config.file).st_mode):
                    os.unlink(self._config.file)
            except FileNotFoundError:
                pass

    def _post_bind(self) -> None:
        super()._post_bind()

        name = self.socket.getsockname()

        os.chmod(name, stat.S_IRWXU | stat.S_IRWXG)  # noqa

        self._name = name
        self._port = None

    #

    def accept(self, sock: ta.Optional[socket_.socket] = None) -> SocketAndAddress:
        if sock is None:
            sock = self.socket

        conn, _ = sock.accept()
        client_address = ('', 0)
        return SocketAndAddress(conn, client_address)


########################################
# ../../../omlish/sockets/handlers.py


##


class SocketHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, addr: SocketAddress, f: SocketIoPair) -> None:
        raise NotImplementedError


class SocketHandlerClose(Exception):  # noqa
    pass


########################################
# ../../../omlish/text/mangle.py


##


@dc.dataclass(frozen=True)
class StringMangler:
    escape: str
    escaped: ta.Sequence[str]

    @classmethod
    def of(cls, escape: str, escaped: ta.Iterable[str]) -> 'StringMangler':
        check.arg(len(escape) == 1)
        return StringMangler(escape, sorted(set(escaped) - {escape}))

    def __post_init__(self) -> None:
        check.non_empty_str(self.escape)
        check.arg(len(self.escape) == 1)
        check.not_in(self.escape, self.escaped)
        check.arg(len(set(self.escaped)) == len(self.escaped))

    #

    @cached_nullary
    def replaced(self) -> ta.Tuple[str, ...]:
        return (self.escape, *self.escaped)

    @cached_nullary
    def replaced_set(self) -> ta.FrozenSet[str]:
        return frozenset(self.replaced())

    @cached_nullary
    def replaced_indexes(self) -> ta.Mapping[str, int]:
        return {s: i for i, s in enumerate(self.replaced())}

    @cached_nullary
    def replaced_pat(self) -> re.Pattern:
        return re.compile('|'.join(re.escape(k) for k in self.replaced()))

    #

    @cached_nullary
    def replacement_pad(self) -> int:
        return len('%x' % (len(self.replaced()),))  # noqa

    @cached_nullary
    def replacements(self) -> ta.Sequence[ta.Tuple[str, str]]:
        fmt = f'%0{self.replacement_pad()}x'
        return [
            (l, self.escape + fmt % (i,))
            for i, l in enumerate(self.replaced())
        ]

    @cached_nullary
    def replacements_dict(self) -> ta.Mapping[str, str]:
        return dict(self.replacements())

    @cached_nullary
    def inverse_replacements_dict(self) -> ta.Mapping[str, str]:
        return {v: k for k, v in self.replacements()}

    @cached_nullary
    def replacements_pat(self) -> re.Pattern:
        return re.compile(''.join([re.escape(self.escape), '.' * self.replacement_pad()]))

    #

    # def mangle(self, s: str) -> str:
    #     ecs = sorted(
    #         frozenset(s) & self.replaced_set(),
    #         key=self.replaced_indexes().__getitem__,
    #         )
    #     rd = self.replacements_dict()
    #     for l in ecs:
    #         r = rd[l]
    #         s = s.replace(l, r)
    #     return s

    def mangle(self, s: str) -> str:
        rd = self.replacements_dict()
        return self.replaced_pat().sub(lambda m: rd[m.group(0)], s)

    #

    # def unmangle(self, s: str) -> str:
    #     for l, r in reversed(self.replacements()):
    #         s = s.replace(r, l)
    #     return s

    def unmangle(self, s: str) -> str:
        ird = self.inverse_replacements_dict()
        return self.replacements_pat().sub(lambda m: ird[m.group(0)], s)


########################################
# ../../dataserver/targets.py


##


@dc.dataclass(frozen=True)
class DataServerTarget(Abstract):
    content_type: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    content_length: ta.Optional[int] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    #

    @classmethod
    def of(
            cls,
            obj: ta.Union[
                'DataServerTarget',
                bytes,
                None,
            ] = None,
            *,

            file_path: ta.Optional[str] = None,
            url: ta.Optional[str] = None,

            **kwargs: ta.Any,
    ) -> 'DataServerTarget':
        if isinstance(obj, DataServerTarget):
            check.none(file_path)
            check.none(url)
            check.empty(kwargs)
            return obj

        elif isinstance(obj, bytes):
            return BytesDataServerTarget(
                data=obj,
                **kwargs,
            )

        elif file_path is not None:
            check.none(obj)
            check.none(url)
            return FileDataServerTarget(
                file_path=file_path,
                **kwargs,
            )

        elif url is not None:
            check.none(obj)
            check.none(file_path)
            return UrlDataServerTarget(
                url=url,
                **kwargs,
            )

        else:
            raise TypeError('No target type provided')

    #

    @classmethod
    def of_bytes(cls, data: bytes) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data,
            content_type='application/octet-stream',
        )

    @classmethod
    def of_text(cls, data: str) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data.encode('utf-8'),
            content_type='text/plain; charset=utf-8',
        )

    @classmethod
    def of_json(cls, data: str) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data.encode('utf-8'),
            content_type='application/json; charset=utf-8',
        )

    @classmethod
    def of_html(cls, data: str) -> 'BytesDataServerTarget':
        return BytesDataServerTarget(
            data=data.encode('utf-8'),
            content_type='text/html; charset=utf-8',
        )


@dc.dataclass(frozen=True)
class BytesDataServerTarget(DataServerTarget):
    data: ta.Optional[bytes] = None  # required


@dc.dataclass(frozen=True)
class FileDataServerTarget(DataServerTarget):
    file_path: ta.Optional[str] = None  # required

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.file_path)


@dc.dataclass(frozen=True)
class UrlDataServerTarget(DataServerTarget):
    url: ta.Optional[str] = None  # required
    methods: ta.Optional[ta.Sequence[str]] = None  # required

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.url)
        check.not_none(self.methods)
        check.not_isinstance(self.methods, str)


########################################
# ../../oci/data.py


##


@dc.dataclass()
class OciDataclass(Abstract):
    pass


##


@dc.dataclass()
class OciImageIndex(OciDataclass):
    manifests: ta.List[ta.Union['OciImageIndex', 'OciImageManifest']]

    annotations: ta.Optional[ta.Dict[str, str]] = None


#


@dc.dataclass()
class OciImageManifest(OciDataclass):
    config: 'OciImageConfig'

    layers: ta.List['OciImageLayer']

    annotations: ta.Optional[ta.Dict[str, str]] = None


#


@dc.dataclass()
class OciImageLayer(OciDataclass):
    class Kind(enum.Enum):
        TAR = enum.auto()
        TAR_GZIP = enum.auto()
        TAR_ZSTD = enum.auto()

        @property
        def compression(self) -> ta.Optional[OciCompression]:
            if self is self.TAR:
                return None
            elif self is self.TAR_GZIP:
                return OciCompression.GZIP
            elif self is self.TAR_ZSTD:
                return OciCompression.ZSTD
            else:
                raise ValueError(self)

        @classmethod
        def from_compression(cls, compression: ta.Optional[OciCompression]) -> 'OciImageLayer.Kind':
            if compression is None:
                return cls.TAR
            elif compression == OciCompression.GZIP:
                return cls.TAR_GZIP
            elif compression == OciCompression.ZSTD:
                return cls.TAR_ZSTD
            else:
                raise ValueError(compression)

    kind: Kind

    data: OciDataRef


#


@dc.dataclass()
class OciImageConfig(OciDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/config.md"""

    architecture: str
    os: str

    @dc.dataclass()
    class RootFs:
        type: str
        diff_ids: ta.List[str]

    rootfs: RootFs

    #

    created: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    author: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    os_version: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'os.version', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    os_features: ta.Optional[ta.List[str]] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'os.features', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    variant: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    """
    config object, OPTIONAL
        User string, OPTIONAL
        ExposedPorts object, OPTIONAL
        Env array of strings, OPTIONAL
        Entrypoint array of strings, OPTIONAL
        Cmd array of strings, OPTIONAL
        Volumes object, OPTIONAL
        WorkingDir string, OPTIONAL
        Labels object, OPTIONAL
        StopSignal string, OPTIONAL
        ArgsEscaped boolean, OPTIONAL
        Memory integer, OPTIONAL
        MemorySwap integer, OPTIONAL
        CpuShares integer, OPTIONAL
        Healthcheck object, OPTIONAL
    """
    config: ta.Optional[ta.Dict[str, ta.Any]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    @dc.dataclass()
    class History:
        created: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        author: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        created_by: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        comment: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
        empty_layer: ta.Optional[bool] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})

    history: ta.Optional[ta.List[History]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})


##


def is_empty_oci_dataclass(obj: OciDataclass) -> bool:
    if not isinstance(obj, OciDataclass):
        raise TypeError(obj)

    elif isinstance(obj, OciImageIndex):
        return not obj.manifests

    elif isinstance(obj, OciImageManifest):
        return not obj.layers

    else:
        return False


##


def get_single_leaf_oci_image_index(image_index: OciImageIndex) -> OciImageIndex:
    while True:
        child_manifest = check.single(image_index.manifests)
        if isinstance(child_manifest, OciImageManifest):
            break
        image_index = check.isinstance(child_manifest, OciImageIndex)

    return image_index


def get_single_oci_image_manifest(image_index: OciImageIndex) -> OciImageManifest:
    child_index = check.single(image_index.manifests)
    return check.isinstance(child_index, OciImageManifest)


########################################
# ../../oci/repositories.py


##


class OciRepository(Abstract):
    @abc.abstractmethod
    def contains_blob(self, digest: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def read_blob(self, digest: str) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def ref_blob(self, digest: str) -> OciDataRef:
        raise NotImplementedError

    @classmethod
    def of(
            cls,
            obj: ta.Union[
                'OciRepository',
                str,
                tarfile.TarFile,
                ta.Mapping[str, bytes],
            ],
    ) -> 'OciRepository':
        if isinstance(obj, OciRepository):
            return obj

        elif isinstance(obj, str):
            check.arg(os.path.isdir(obj))
            return DirectoryOciRepository(obj)

        elif isinstance(obj, tarfile.TarFile):
            return TarFileOciRepository(obj)

        elif isinstance(obj, ta.Mapping):
            return DictOciRepository(obj)

        else:
            raise TypeError(obj)


class FileOciRepository(OciRepository, Abstract):
    @abc.abstractmethod
    def read_file(self, path: str) -> bytes:
        raise NotImplementedError


#


class DirectoryOciRepository(FileOciRepository):
    def __init__(self, data_dir: str) -> None:
        super().__init__()

        self._data_dir = check.non_empty_str(data_dir)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._data_dir!r})'

    def read_file(self, path: str) -> bytes:
        full_path = os.path.join(self._data_dir, path)
        check.arg(is_path_in_dir(self._data_dir, full_path))
        with open(full_path, 'rb') as f:
            return f.read()

    def blob_path(self, digest: str) -> str:
        scheme, value = digest.split(':')
        return os.path.join('blobs', scheme, value)

    def blob_full_path(self, digest: str) -> str:
        path = self.blob_path(digest)
        full_path = os.path.join(self._data_dir, path)
        check.arg(is_path_in_dir(self._data_dir, full_path))
        return full_path

    def contains_blob(self, digest: str) -> bool:
        return os.path.isfile(self.blob_full_path(digest))

    def read_blob(self, digest: str) -> bytes:
        return self.read_file(self.blob_path(digest))

    def ref_blob(self, digest: str) -> OciDataRef:
        return FileOciDataRef(self.blob_full_path(digest))


#


class TarFileOciRepository(FileOciRepository):
    def __init__(self, tar_file: tarfile.TarFile) -> None:
        super().__init__()

        check.arg('r' in tar_file.mode)

        self._tar_file = tar_file

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._tar_file!r})'

    def read_file(self, path: str) -> bytes:
        if (ti := self._tar_file.getmember(path)) is None:
            raise FileNotFoundError(path)
        with check.not_none(self._tar_file.extractfile(ti)) as f:
            return f.read()

    def blob_name(self, digest: str) -> str:
        scheme, value = digest.split(':')
        return os.path.join('blobs', scheme, value)

    def contains_blob(self, digest: str) -> bool:
        try:
            self._tar_file.getmember(self.blob_name(digest))
        except KeyError:
            return False
        else:
            return True

    def read_blob(self, digest: str) -> bytes:
        if (ti := self._tar_file.getmember(self.blob_name(digest))) is None:
            raise KeyError(digest)
        with check.not_none(self._tar_file.extractfile(ti)) as f:
            return f.read()

    def ref_blob(self, digest: str) -> OciDataRef:
        return TarFileOciDataRef(
            tar_file=self._tar_file,
            tar_info=self._tar_file.getmember(self.blob_name(digest)),
        )


#


class DictOciRepository(OciRepository):
    def __init__(self, blobs: ta.Mapping[str, bytes]) -> None:
        super().__init__()

        self._blobs = blobs

    def contains_blob(self, digest: str) -> bool:
        return digest in self._blobs

    def read_blob(self, digest: str) -> bytes:
        return self._blobs[digest]

    def ref_blob(self, digest: str) -> OciDataRef:
        return BytesOciDataRef(self._blobs[digest])


########################################
# ../../oci/tars.py


##


class WrittenOciDataTarFileInfo(ta.NamedTuple):
    compressed_sz: int
    compressed_sha256: str

    tar_sz: int
    tar_sha256: str


class OciDataTarWriter(ExitStacked):
    def __init__(
            self,
            f: ta.BinaryIO,
            compression: ta.Optional[OciCompression] = None,
            *,
            gzip_level: int = 1,
            zstd_level: int = 10,
    ) -> None:
        super().__init__()

        self._f = f
        self._compression = compression

        self._gzip_level = gzip_level
        self._zstd_level = zstd_level

    class _FileWrapper:
        def __init__(self, f):
            super().__init__()

            self._f = f
            self._c = 0
            self._h = hashlib.sha256()

        @property
        def size(self) -> int:
            return self._c

        def sha256(self) -> str:
            return self._h.hexdigest()

        def write(self, d):
            self._c += len(d)
            self._h.update(d)
            self._f.write(d)

        def tell(self) -> int:
            return self._f.tell()

    _cw: _FileWrapper
    _cf: ta.BinaryIO

    _tw: _FileWrapper
    _tf: tarfile.TarFile

    def info(self) -> WrittenOciDataTarFileInfo:
        return WrittenOciDataTarFileInfo(
            compressed_sz=self._cw.size,
            compressed_sha256=self._cw.sha256(),

            tar_sz=self._tw.size,
            tar_sha256=self._tw.sha256(),
        )

    def _enter_contexts(self) -> None:
        self._cw = self._FileWrapper(self._f)

        if self._compression is OciCompression.GZIP:
            self._cf = self._enter_context(
                gzip.GzipFile(  # type: ignore
                    fileobj=self._cw,
                    mode='wb',
                    compresslevel=self._gzip_level,
                ),
            )

        elif self._compression is OciCompression.ZSTD:
            import zstandard  # noqa

            zc = zstandard.ZstdCompressor(
                level=self._zstd_level,
            )
            self._cf = self._enter_context(zc.stream_writer(self._cw))  # type: ignore

        elif self._compression is None:
            self._cf = self._cw  # type: ignore

        else:
            raise ValueError(self._compression)

        #

        self._tw = self._FileWrapper(self._cf)

        self._tf = self._enter_context(
            tarfile.open(  # type: ignore  # noqa
                fileobj=self._tw,
                mode='w',
            ),
        )

    def tar_file(self) -> tarfile.TarFile:
        return self._tf

    def add_file(self, ti: tarfile.TarInfo, f: ta.Optional[ta.BinaryIO] = None) -> None:
        self._tf.addfile(ti, f)


def write_oci_data_tar_file(
        f: ta.BinaryIO,
        data: ta.Mapping[str, OciDataRef],
) -> WrittenOciDataTarFileInfo:
    with OciDataTarWriter(f) as tgw:
        for n, dr in data.items():
            ti = tarfile.TarInfo(name=n)
            ri = OciDataRefInfo(dr)
            ti.size = ri.size()
            with open_oci_data_ref(dr) as df:
                tgw.add_file(ti, df)

    return tgw.info()


########################################
# ../../../omlish/asyncs/asyncio/sockets.py


##


async def asyncio_wait_until_can_connect(
        host: ta.Any = None,
        port: ta.Any = None,
        *,
        timeout: TimeoutLike = None,
        on_fail: ta.Optional[ta.Callable[[BaseException], None]] = None,
        sleep_s: float = .1,
        exception: ta.Union[ta.Type[BaseException], ta.Tuple[ta.Type[BaseException], ...]] = (Exception,),
) -> None:
    timeout = Timeout.of(timeout)

    async def inner():
        while True:
            timeout()

            try:
                reader, writer = await asyncio.open_connection(host, port)

            except asyncio.CancelledError:
                raise

            except exception as e:  # noqa
                if on_fail is not None:
                    on_fail(e)

            else:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=timeout.or_(None))
                break

            await asyncio.sleep(min(sleep_s, timeout.remaining()))

    if timeout() != float('inf'):
        await asyncio.wait_for(inner(), timeout=timeout())
    else:
        await inner()


########################################
# ../../../omlish/asyncs/asyncio/timeouts.py


##


def asyncio_maybe_timeout(
        fut: AwaitableT,
        timeout: TimeoutLike = None,
) -> AwaitableT:
    if timeout is not None:
        fut = asyncio.wait_for(fut, Timeout.of(timeout)())  # type: ignore
    return fut


########################################
# ../../../omlish/formats/yaml/goyaml/tokens.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


@dc.dataclass(frozen=True)
class YamlSyntaxError(YamlError):
    msg: str
    token: ta.Optional['YamlToken']

    @property
    def message(self) -> str:
        return self.msg


##


class YamlChars:
    # SEQUENCE_ENTRY character for sequence entry
    SEQUENCE_ENTRY = '-'
    # MAPPING_KEY character for mapping key
    MAPPING_KEY = '?'
    # MAPPING_VALUE character for mapping value
    MAPPING_VALUE = ':'
    # COLLECT_ENTRY character for collect entry
    COLLECT_ENTRY = ','
    # SEQUENCE_START character for sequence start
    SEQUENCE_START = '['
    # SEQUENCE_END character for sequence end
    SEQUENCE_END = ']'
    # MAPPING_START character for mapping start
    MAPPING_START = '{'
    # MAPPING_END character for mapping end
    MAPPING_END = '}'
    # COMMENT character for comment
    COMMENT = '#'
    # ANCHOR character for anchor
    ANCHOR = '&'
    # ALIAS character for alias
    ALIAS = '*'
    # TAG character for tag
    TAG = '!'
    # LITERAL character for literal
    LITERAL = '|'
    # FOLDED character for folded
    FOLDED = '>'
    # SINGLE_QUOTE character for single quote
    SINGLE_QUOTE = '\''
    # DOUBLE_QUOTE character for double quote
    DOUBLE_QUOTE = '"'
    # DIRECTIVE character for directive
    DIRECTIVE = '%'
    # SPACE character for space
    SPACE = ' '
    # LINE_BREAK character for line break
    LINE_BREAK = '\n'


class YamlTokenType(enum.Enum):
    # UNKNOWN reserve for invalid type
    UNKNOWN = enum.auto()
    # DOCUMENT_HEADER type for DocumentHeader token
    DOCUMENT_HEADER = enum.auto()
    # DOCUMENT_END type for DocumentEnd token
    DOCUMENT_END = enum.auto()
    # SEQUENCE_ENTRY type for SequenceEntry token
    SEQUENCE_ENTRY = enum.auto()
    # MAPPING_KEY type for MappingKey token
    MAPPING_KEY = enum.auto()
    # MAPPING_VALUE type for MappingValue token
    MAPPING_VALUE = enum.auto()
    # MERGE_KEY type for MergeKey token
    MERGE_KEY = enum.auto()
    # COLLECT_ENTRY type for CollectEntry token
    COLLECT_ENTRY = enum.auto()
    # SEQUENCE_START type for SequenceStart token
    SEQUENCE_START = enum.auto()
    # SEQUENCE_END type for SequenceEnd token
    SEQUENCE_END = enum.auto()
    # MAPPING_START type for MappingStart token
    MAPPING_START = enum.auto()
    # MAPPING_END type for MappingEnd token
    MAPPING_END = enum.auto()
    # COMMENT type for Comment token
    COMMENT = enum.auto()
    # ANCHOR type for Anchor token
    ANCHOR = enum.auto()
    # ALIAS type for Alias token
    ALIAS = enum.auto()
    # TAG type for Tag token
    TAG = enum.auto()
    # LITERAL type for Literal token
    LITERAL = enum.auto()
    # FOLDED type for Folded token
    FOLDED = enum.auto()
    # SINGLE_QUOTE type for SingleQuote token
    SINGLE_QUOTE = enum.auto()
    # DOUBLE_QUOTE type for DoubleQuote token
    DOUBLE_QUOTE = enum.auto()
    # DIRECTIVE type for Directive token
    DIRECTIVE = enum.auto()
    # SPACE type for Space token
    SPACE = enum.auto()
    # NULL type for Null token
    NULL = enum.auto()
    # IMPLICIT_NULL type for implicit Null token.
    # This is used when explicit keywords such as null or ~ are not specified. It is distinguished during encoding and
    # output as an empty string.
    IMPLICIT_NULL = enum.auto()
    # INFINITY type for Infinity token
    INFINITY = enum.auto()
    # NAN type for Nan token
    NAN = enum.auto()
    # INTEGER type for Integer token
    INTEGER = enum.auto()
    # BINARY_INTEGER type for BinaryInteger token
    BINARY_INTEGER = enum.auto()
    # OCTET_INTEGER type for OctetInteger token
    OCTET_INTEGER = enum.auto()
    # HEX_INTEGER type for HexInteger token
    HEX_INTEGER = enum.auto()
    # FLOAT type for Float token
    FLOAT = enum.auto()
    # STRING type for String token
    STRING = enum.auto()
    # BOOL type for Bool token
    BOOL = enum.auto()
    # INVALID type for invalid token
    INVALID = enum.auto()


class YamlCharType(enum.Enum):
    # INDICATOR type of indicator character
    INDICATOR = enum.auto()
    # WHITE-SPACE type of white space character
    WHITESPACE = enum.auto()
    # MISCELLANEOUS type of miscellaneous character
    MISCELLANEOUS = enum.auto()
    # ESCAPED type of escaped character
    ESCAPED = enum.auto()
    # INVALID type for an invalid token.
    INVALID = enum.auto()


class YamlIndicator(enum.Enum):
    # NOT not an indicator
    NOT = enum.auto()
    # BLOCK_STRUCTURE indicator for block structure ( '-', '?', ':' )
    BLOCK_STRUCTURE = enum.auto()
    # FLOW_COLLECTION indicator for flow collection ( '[', ']', '{', '}', ',' )
    FLOW_COLLECTION = enum.auto()
    # COMMENT indicator for comment ( '#' )
    COMMENT = enum.auto()
    # NODE_PROPERTY indicator for node property ( '!', '&', '*' )
    NODE_PROPERTY = enum.auto()
    # BLOCK_SCALAR indicator for block scalar ( '|', '>' )
    BLOCK_SCALAR = enum.auto()
    # QUOTED_SCALAR indicator for quoted scalar ( ''', '"' )
    QUOTED_SCALAR = enum.auto()
    # DIRECTIVE indicator for directive ( '%' )
    DIRECTIVE = enum.auto()
    # INVALID_USE_OF_RESERVED indicator for invalid use of reserved keyword ( '@', '`' )
    INVALID_USE_OF_RESERVED = enum.auto()


##


class YamlKeywords:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    RESERVED_NULL_KEYWORDS = (
        'null',
        'Null',
        'NULL',
        '~',
    )

    RESERVED_BOOL_KEYWORDS = (
        'true',
        'True',
        'TRUE',
        'false',
        'False',
        'FALSE',
    )

    # For compatibility with other YAML 1.1 parsers.
    # Note that we use these solely for encoding the bool value with quotes. go-yaml should not treat these as reserved
    # keywords at parsing time. as go-yaml is supposed to be compliant only with YAML 1.2.
    RESERVED_LEGACY_BOOL_KEYWORDS = (
        'y',
        'Y',
        'yes',
        'Yes',
        'YES',
        'n',
        'N',
        'no',
        'No',
        'NO',
        'on',
        'On',
        'ON',
        'off',
        'Off',
        'OFF',
    )

    RESERVED_INF_KEYWORDS = (
        '.inf',
        '.Inf',
        '.INF',
        '-.inf',
        '-.Inf',
        '-.INF',
    )

    RESERVED_NAN_KEYWORDS = (
        '.nan',
        '.NaN',
        '.NAN',
    )

    RESERVED_KEYWORD_MAP: ta.ClassVar[ta.Mapping[str, ta.Callable[[str, str, 'YamlPosition'], 'YamlToken']]]
    RESERVED_ENC_KEYWORD_MAP: ta.ClassVar[ta.Mapping[str, ta.Callable[[str, str, 'YamlPosition'], 'YamlToken']]]


def _yaml_reserved_keyword_token(typ: YamlTokenType, value: str, org: str, pos: 'YamlPosition') -> 'YamlToken':
    return YamlToken(
        type=typ,
        char_type=YamlCharType.MISCELLANEOUS,
        indicator=YamlIndicator.NOT,
        value=value,
        origin=org,
        position=pos,
    )


YamlKeywords.RESERVED_KEYWORD_MAP = {
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.NULL) for keyword in YamlKeywords.RESERVED_NULL_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.BOOL) for keyword in YamlKeywords.RESERVED_BOOL_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.INFINITY) for keyword in YamlKeywords.RESERVED_INF_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.NAN) for keyword in YamlKeywords.RESERVED_NAN_KEYWORDS},  # noqa
}


# RESERVED_ENC_KEYWORD_MAP contains is the keyword map used at encoding time.
# This is supposed to be a superset of RESERVED_KEYWORD_MAP, and used to quote legacy keywords present in YAML 1.1 or
# lesser for compatibility reasons, even though this library is supposed to be YAML 1.2-compliant.
YamlKeywords.RESERVED_ENC_KEYWORD_MAP = {
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.NULL) for keyword in YamlKeywords.RESERVED_NULL_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.BOOL) for keyword in YamlKeywords.RESERVED_BOOL_KEYWORDS},  # noqa
    **{keyword: functools.partial(_yaml_reserved_keyword_token, YamlTokenType.BOOL) for keyword in YamlKeywords.RESERVED_LEGACY_BOOL_KEYWORDS},  # noqa
}


##


YamlReservedTagKeyword = str  # ta.TypeAlias  # omlish-amalg-typing-no-move


class YamlReservedTagKeywords:
    # INTEGER `!!int` tag
    INTEGER = '!!int'
    # FLOAT `!!float` tag
    FLOAT = '!!float'
    # NULL `!!null` tag
    NULL = '!!null'
    # SEQUENCE `!!seq` tag
    SEQUENCE = '!!seq'
    # MAPPING `!!map` tag
    MAPPING = '!!map'
    # STRING `!!str` tag
    STRING = '!!str'
    # BINARY `!!binary` tag
    BINARY = '!!binary'
    # ORDERED_MAP `!!omap` tag
    ORDERED_MAP = '!!omap'
    # SET `!!set` tag
    SET = '!!set'
    # TIMESTAMP `!!timestamp` tag
    TIMESTAMP = '!!timestamp'
    # BOOLEAN `!!bool` tag
    BOOLEAN = '!!bool'
    # MERGE `!!merge` tag
    MERGE = '!!merge'


# RESERVED_TAG_KEYWORD_MAP map for reserved tag keywords
YAML_RESERVED_TAG_KEYWORD_MAP: ta.Mapping[YamlReservedTagKeyword, ta.Callable[[str, str, 'YamlPosition'], 'YamlToken']] = {  # noqa
    YamlReservedTagKeywords.INTEGER: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.FLOAT: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.NULL: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.SEQUENCE: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.MAPPING: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.STRING: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.BINARY: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.ORDERED_MAP: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.SET: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.TIMESTAMP: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.BOOLEAN: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.MERGE: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
}


##


class YamlNumberType(enum.Enum):
    DECIMAL = 'decimal'
    BINARY = 'binary'
    OCTET = 'octet'
    HEX = 'hex'
    FLOAT = 'float'


@dc.dataclass()
class YamlNumberValue:
    type: YamlNumberType
    value: ta.Any
    text: str


def yaml_to_number(value: str) -> ta.Optional[YamlNumberValue]:
    num = _yaml_to_number(value)
    if isinstance(num, YamlError):
        return None

    return num


def _yaml_is_number(value: str) -> bool:
    num = _yaml_to_number(value)
    if isinstance(num, YamlError):
        # var numErr *strconv.NumError
        # if errors.As(err, &numErr) && errors.Is(numErr.Err, strconv.ErrRange) {
        #     return true

        return False

    return num is not None


def _yaml_to_number(value: str) -> YamlErrorOr[ta.Optional[YamlNumberValue]]:
    if not value:
        return None

    if value.startswith('_'):
        return None

    dot_count = value.count('.')
    if dot_count > 1:
        return None

    is_negative = value.startswith('-')
    normalized = value.lstrip('+').lstrip('-').replace('_', '')

    typ: YamlNumberType
    base = 0

    if normalized.startswith('0x'):
        normalized = normalized.lstrip('0x')
        base = 16
        typ = YamlNumberType.HEX
    elif normalized.startswith('0o'):
        normalized = normalized.lstrip('0o')
        base = 8
        typ = YamlNumberType.OCTET
    elif normalized.startswith('0b'):
        normalized = normalized.lstrip('0b')
        base = 2
        typ = YamlNumberType.BINARY
    elif normalized.startswith('0') and len(normalized) > 1 and dot_count == 0:
        base = 8
        typ = YamlNumberType.OCTET
    elif dot_count == 1:
        typ = YamlNumberType.FLOAT
    else:
        typ = YamlNumberType.DECIMAL
        base = 10

    text = normalized
    if is_negative:
        text = '-' + text

    v: ta.Any
    if typ == YamlNumberType.FLOAT:
        try:
            v = float(text)
        except ValueError as e:
            return yaml_error(e)
    else:
        try:
            v = int(text, base)
        except ValueError as e:
            return yaml_error(e)

    return YamlNumberValue(
        type=typ,
        value=v,
        text=text,
    )


##


# This is a subset of the formats permitted by the regular expression defined at http:#yaml.org/type/timestamp.html.
# Note that time.Parse cannot handle: "2001-12-14 21:59:43.10 -5" from the examples.
YAML_TIMESTAMP_FORMATS = (
    '%Y-%m-%dT%H:%M:%S.%fZ',  # RFC3339Nano
    '%Y-%m-%dt%H:%M:%S.%fZ',  # RFC3339Nano with lower-case "t"
    '%Y-%m-%d %H:%M:%S',      # DateTime
    '%Y-%m-%d',               # DateOnly

    # Not in examples, but to preserve backward compatibility by quoting time values
    '%H:%M',
)


def _yaml_is_timestamp(value: str) -> bool:
    for format_str in YAML_TIMESTAMP_FORMATS:
        try:
            datetime.datetime.strptime(value, format_str)  # noqa
            return True
        except ValueError:
            continue
    return False


##


# is_need_quoted checks whether the value needs quote for passed string or not
def _yaml_is_need_quoted(value: str) -> bool:
    if not value:
        return True

    if value in YamlKeywords.RESERVED_ENC_KEYWORD_MAP:
        return True

    if _yaml_is_number(value):
        return True

    if value == '-':
        return True

    if value[0] in ('*', '&', '[', '{', '}', ']', ',', '!', '|', '>', '%', '\'', '"', '@', ' ', '`'):
        return True

    if value[-1] in (':', ' '):
        return True

    if _yaml_is_timestamp(value):
        return True

    for i, c in enumerate(value):
        if c in ('#', '\\'):
            return True
        elif c in (':', '-'):
            if i + 1 < len(value) and value[i + 1] == ' ':
                return True

    return False


# literal_block_header detect literal block scalar header
def yaml_literal_block_header(value: str) -> str:
    lbc = yaml_detect_line_break_char(value)

    if lbc not in value:
        return ''
    elif value.endswith(lbc + lbc):
        return '|+'
    elif value.endswith(lbc):
        return '|'
    else:
        return '|-'


##


# new create reserved keyword token or number token and other string token.
def yaml_new_token(value: str, org: str, pos: 'YamlPosition') -> 'YamlToken':
    fn = YamlKeywords.RESERVED_KEYWORD_MAP.get(value)
    if fn is not None:
        return fn(value, org, pos)

    if (num := yaml_to_number(value)) is not None:
        tk = YamlToken(
            type=YamlTokenType.INTEGER,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value=value,
            origin=org,
            position=pos,
        )
        if num.type == YamlNumberType.FLOAT:
            tk.type = YamlTokenType.FLOAT
        elif num.type == YamlNumberType.BINARY:
            tk.type = YamlTokenType.BINARY_INTEGER
        elif num.type == YamlNumberType.OCTET:
            tk.type = YamlTokenType.OCTET_INTEGER
        elif num.type == YamlNumberType.HEX:
            tk.type = YamlTokenType.HEX_INTEGER
        return tk

    return YamlTokenMakers.new_string(value, org, pos)


# Position type for position in YAML document
@dc.dataclass()
class YamlPosition:
    line: int
    column: int
    offset: int
    indent_num: int
    indent_level: int

    # String position to text
    def __str__(self) -> str:
        return f'[level:{self.indent_level:d},line:{self.line:d},column:{self.column:d},offset:{self.offset:d}]'


# Token type for token
@dc.dataclass()
@ta.final
class YamlToken:
    # Type is a token type.
    type: YamlTokenType
    # CharType is a character type.
    char_type: YamlCharType
    # Indicator is an indicator type.
    indicator: YamlIndicator
    # Value is a string extracted with only meaningful characters, with spaces and such removed.
    value: str
    # Origin is a string that stores the original text as-is.
    origin: str
    # Error keeps error message for InvalidToken.
    error: ta.Optional[YamlError] = None
    # Position is a token position.
    position: YamlPosition = dc.field(default_factory=dataclass_field_required('position'))
    # Next is a next token reference.
    next: ta.Optional['YamlToken'] = dc.field(default=None, repr=False)
    # Prev is a previous token reference.
    prev: ta.Optional['YamlToken'] = dc.field(default=None, repr=False)

    # previous_type previous token type
    def previous_type(self) -> YamlTokenType:
        if self.prev is not None:
            return self.prev.type

        return YamlTokenType.UNKNOWN

    # next_type next token type
    def next_type(self) -> YamlTokenType:
        if self.next is not None:
            return self.next.type

        return YamlTokenType.UNKNOWN

    # add_column append column number to current position of column
    @classmethod
    def add_column(cls, t: ta.Optional['YamlToken'], col: int) -> None:
        if t is None:
            return

        t.position.column += col

    # clone copy token ( preserve Prev/Next reference )
    @classmethod
    def clone(cls, t: ta.Optional['YamlToken']) -> ta.Optional['YamlToken']:
        if t is None:
            return None

        copied = copy.copy(t)
        if t.position is not None:
            pos = copy.copy(t.position)
            copied.position = pos

        return copied


##


# Tokens type of token collection
class YamlTokens(ta.List[YamlToken]):
    def invalid_token(self) -> ta.Optional[YamlToken]:
        for tt in self:
            if tt.type == YamlTokenType.INVALID:
                return tt
        return None

    def _add(self, tk: YamlToken) -> None:
        if not self:
            self.append(tk)
        else:
            last = self[-1]
            last.next = tk
            tk.prev = last
            self.append(tk)

    # add append new some tokens
    def add(self, *tks: YamlToken) -> None:
        for tk in tks:
            self._add(tk)


##


class YamlTokenMakers:  # noqa
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    # new_string create token for String
    @staticmethod
    def new_string(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.STRING,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value=value,
            origin=org,
            position=pos,
        )

    # new_sequence_entry create token for SequenceEntry
    @staticmethod
    def new_sequence_entry(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SEQUENCE_ENTRY,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_STRUCTURE,
            value=YamlChars.SEQUENCE_ENTRY,
            origin=org,
            position=pos,
        )

    # new_mapping_key create token for MappingKey
    @staticmethod
    def new_mapping_key(pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_KEY,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_STRUCTURE,
            value=YamlChars.MAPPING_KEY,
            origin=YamlChars.MAPPING_KEY,
            position=pos,
        )

    # new_mapping_value create token for MappingValue
    @staticmethod
    def new_mapping_value(pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_VALUE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_STRUCTURE,
            value=YamlChars.MAPPING_VALUE,
            origin=YamlChars.MAPPING_VALUE,
            position=pos,
        )

    # new_collect_entry create token for CollectEntry
    @staticmethod
    def new_collect_entry(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.COLLECT_ENTRY,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.COLLECT_ENTRY,
            origin=org,
            position=pos,
        )

    # new_sequence_start create token for SequenceStart
    @staticmethod
    def new_sequence_start(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SEQUENCE_START,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.SEQUENCE_START,
            origin=org,
            position=pos,
        )

    # new_sequence_end create token for SequenceEnd
    @staticmethod
    def new_sequence_end(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SEQUENCE_END,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.SEQUENCE_END,
            origin=org,
            position=pos,
        )

    # new_mapping_start create token for MappingStart
    @staticmethod
    def new_mapping_start(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_START,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.MAPPING_START,
            origin=org,
            position=pos,
        )

    # new_mapping_end create token for MappingEnd
    @staticmethod
    def new_mapping_end(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_END,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.MAPPING_END,
            origin=org,
            position=pos,
        )

    # new_comment create token for Comment
    @staticmethod
    def new_comment(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.COMMENT,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.COMMENT,
            value=value,
            origin=org,
            position=pos,
        )

    # new_anchor create token for Anchor
    @staticmethod
    def new_anchor(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.ANCHOR,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.NODE_PROPERTY,
            value=YamlChars.ANCHOR,
            origin=org,
            position=pos,
        )

    # new_alias create token for Alias
    @staticmethod
    def new_alias(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.ALIAS,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.NODE_PROPERTY,
            value=YamlChars.ALIAS,
            origin=org,
            position=pos,
        )

    # new_tag create token for Tag
    @staticmethod
    def new_tag(value: str, org: str, pos: YamlPosition) -> YamlToken:
        fn = YAML_RESERVED_TAG_KEYWORD_MAP.get(value)
        if fn is not None:
            return fn(value, org, pos)

        return YamlToken(
            type=YamlTokenType.TAG,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.NODE_PROPERTY,
            value=value,
            origin=org,
            position=pos,
        )

    # new_literal create token for Literal
    @staticmethod
    def new_literal(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.LITERAL,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_folded create token for Folded
    @staticmethod
    def new_folded(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.FOLDED,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_single_quote create token for SingleQuote
    @staticmethod
    def new_single_quote(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SINGLE_QUOTE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.QUOTED_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_double_quote create token for DoubleQuote
    @staticmethod
    def new_double_quote(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DOUBLE_QUOTE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.QUOTED_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_directive create token for Directive
    @staticmethod
    def new_directive(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DIRECTIVE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.DIRECTIVE,
            value=YamlChars.DIRECTIVE,
            origin=org,
            position=pos,
        )

    # new_space create token for Space
    @staticmethod
    def new_space(pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SPACE,
            char_type=YamlCharType.WHITESPACE,
            indicator=YamlIndicator.NOT,
            value=YamlChars.SPACE,
            origin=YamlChars.SPACE,
            position=pos,
        )

    # new_merge_key create token for MergeKey
    @staticmethod
    def new_merge_key(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MERGE_KEY,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value='<<',
            origin=org,
            position=pos,
        )

    # new_document_header create token for DocumentHeader
    @staticmethod
    def new_document_header(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DOCUMENT_HEADER,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value='---',
            origin=org,
            position=pos,
        )

    # new_document_end create token for DocumentEnd
    @staticmethod
    def new_document_end(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DOCUMENT_END,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value='...',
            origin=org,
            position=pos,
        )

    @staticmethod
    def new_invalid(err: YamlError, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.INVALID,
            char_type=YamlCharType.INVALID,
            indicator=YamlIndicator.NOT,
            value=org,
            origin=org,
            error=err,
            position=pos,
        )


##


# detect_line_break_char detect line break character in only one inside scalar content scope.
def yaml_detect_line_break_char(src: str) -> str:
    nc = src.count('\n')
    rc = src.count('\r')
    rnc = src.count('\r\n')
    if nc == rnc and rc == rnc:
        return '\r\n'
    elif rc > nc:
        return '\r'
    else:
        return '\n'


########################################
# ../../../omlish/http/handlers.py


##


@dc.dataclass(frozen=True)
class HttpHandlerRequest:
    client_address: SocketAddress
    method: str
    path: str
    headers: ParsedHttpHeaders
    data: ta.Optional[bytes]


@dc.dataclass(frozen=True)
class HttpHandlerResponse:
    status: ta.Union[http.HTTPStatus, int]

    headers: ta.Optional[ta.Mapping[str, str]] = None
    data: ta.Optional[HttpHandlerResponseData] = None
    close_connection: ta.Optional[bool] = None

    def close(self) -> None:
        if isinstance(d := self.data, HttpHandlerResponseStreamedData):
            d.close()


@dc.dataclass(frozen=True)
class HttpHandlerResponseStreamedData:
    iter: ta.Iterable[bytes]
    length: ta.Optional[int] = None

    def close(self) -> None:
        if hasattr(d := self.iter, 'close'):
            d.close()  # noqa


class HttpHandlerError(Exception):
    pass


class UnsupportedMethodHttpHandlerError(Exception):
    pass


class HttpHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class LoggingHttpHandler(HttpHandler_):
    handler: HttpHandler
    log: LoggerLike
    level: int = logging.DEBUG

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        self.log.log(self.level, '%r', req)
        resp = self.handler(req)
        self.log.log(self.level, '%r', resp)
        return resp


@dc.dataclass(frozen=True)
class ExceptionLoggingHttpHandler(HttpHandler_):
    handler: HttpHandler
    log: LoggerLike
    message: ta.Union[str, ta.Callable[[HttpHandlerRequest, BaseException], str]] = 'Error in http handler'

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        try:
            return self.handler(req)
        except Exception as e:  # noqa
            if callable(msg := self.message):
                msg = msg(req, e)
            self.log.exception(msg)
            raise


##


@dc.dataclass(frozen=True)
class BytesResponseHttpHandler(HttpHandler_):
    data: bytes

    status: ta.Union[http.HTTPStatus, int] = 200
    content_type: ta.Optional[str] = 'application/octet-stream'
    headers: ta.Optional[ta.Mapping[str, str]] = None
    close_connection: bool = True

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        return HttpHandlerResponse(
            status=self.status,
            headers={
                **({'Content-Type': self.content_type} if self.content_type else {}),
                'Content-Length': str(len(self.data)),
                **(self.headers or {}),
            },
            data=self.data,
            close_connection=self.close_connection,
        )


@dc.dataclass(frozen=True)
class StringResponseHttpHandler(HttpHandler_):
    data: str

    status: ta.Union[http.HTTPStatus, int] = 200
    content_type: ta.Optional[str] = 'text/plain; charset=utf-8'
    headers: ta.Optional[ta.Mapping[str, str]] = None
    close_connection: bool = True

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        data = self.data.encode('utf-8')
        return HttpHandlerResponse(
            status=self.status,
            headers={
                **({'Content-Type': self.content_type} if self.content_type else {}),
                'Content-Length': str(len(data)),
                **(self.headers or {}),
            },
            data=data,
            close_connection=self.close_connection,
        )


########################################
# ../../../omlish/lite/inject.py


###
# types


@dc.dataclass(frozen=True)
class InjectorKey(ta.Generic[T]):
    # Before PEP-560 typing.Generic was a metaclass with a __new__ that takes a 'cls' arg, so instantiating a dataclass
    # with kwargs (such as through dc.replace) causes `TypeError: __new__() got multiple values for argument 'cls'`.
    # See:
    #  - https://github.com/python/cpython/commit/d911e40e788fb679723d78b6ea11cabf46caed5a
    #  - https://gist.github.com/wrmsr/4468b86efe9f373b6b114bfe85b98fd3
    cls_: InjectorKeyCls

    tag: ta.Any = None
    array: bool = False


def is_valid_injector_key_cls(cls: ta.Any) -> bool:
    return isinstance(cls, type) or is_new_type(cls)


def check_valid_injector_key_cls(cls: T) -> T:
    if not is_valid_injector_key_cls(cls):
        raise TypeError(cls)
    return cls


##


class InjectorProvider(Abstract):
    @abc.abstractmethod
    def provider_fn(self) -> InjectorProviderFn:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class InjectorBinding:
    key: InjectorKey
    provider: InjectorProvider

    def __post_init__(self) -> None:
        check.isinstance(self.key, InjectorKey)
        check.isinstance(self.provider, InjectorProvider)


class InjectorBindings(Abstract):
    @abc.abstractmethod
    def bindings(self) -> ta.Iterator[InjectorBinding]:
        raise NotImplementedError

##


class Injector(Abstract):
    @abc.abstractmethod
    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, key: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def provide_kwargs(
            self,
            obj: ta.Any,
            *,
            skip_args: int = 0,
            skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
    ) -> ta.Mapping[str, ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(
            self,
            obj: ta.Any,
            *,
            args: ta.Optional[ta.Sequence[ta.Any]] = None,
            kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Any:
        raise NotImplementedError

    def __getitem__(
            self,
            target: ta.Union[InjectorKey[T], ta.Type[T]],
    ) -> T:
        return self.provide(target)


###
# exceptions


class InjectorError(Exception):
    pass


@dc.dataclass()
class InjectorKeyError(InjectorError):
    key: InjectorKey

    source: ta.Any = None
    name: ta.Optional[str] = None


class UnboundInjectorKeyError(InjectorKeyError):
    pass


class DuplicateInjectorKeyError(InjectorKeyError):
    pass


class CyclicDependencyInjectorKeyError(InjectorKeyError):
    pass


###
# keys


def as_injector_key(o: ta.Any) -> InjectorKey:
    if o is inspect.Parameter.empty:
        raise TypeError(o)
    if isinstance(o, InjectorKey):
        return o
    if is_valid_injector_key_cls(o):
        return InjectorKey(o)
    raise TypeError(o)


###
# providers


@dc.dataclass(frozen=True)
class FnInjectorProvider(InjectorProvider):
    fn: ta.Any

    def __post_init__(self) -> None:
        check.not_isinstance(self.fn, type)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.fn)

        return pfn


@dc.dataclass(frozen=True)
class CtorInjectorProvider(InjectorProvider):
    cls_: type

    def __post_init__(self) -> None:
        check.isinstance(self.cls_, type)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.cls_)

        return pfn


@dc.dataclass(frozen=True)
class ConstInjectorProvider(InjectorProvider):
    v: ta.Any

    def provider_fn(self) -> InjectorProviderFn:
        return lambda _: self.v


@dc.dataclass(frozen=True)
class SingletonInjectorProvider(InjectorProvider):
    p: InjectorProvider

    def __post_init__(self) -> None:
        check.isinstance(self.p, InjectorProvider)

    def provider_fn(self) -> InjectorProviderFn:
        v = not_set = object()

        def pfn(i: Injector) -> ta.Any:
            nonlocal v
            if v is not_set:
                v = ufn(i)
            return v

        ufn = self.p.provider_fn()
        return pfn


@dc.dataclass(frozen=True)
class LinkInjectorProvider(InjectorProvider):
    k: InjectorKey

    def __post_init__(self) -> None:
        check.isinstance(self.k, InjectorKey)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.provide(self.k)

        return pfn


@dc.dataclass(frozen=True)
class ArrayInjectorProvider(InjectorProvider):
    ps: ta.Sequence[InjectorProvider]

    def provider_fn(self) -> InjectorProviderFn:
        ps = [p.provider_fn() for p in self.ps]

        def pfn(i: Injector) -> ta.Any:
            rv = []
            for ep in ps:
                o = ep(i)
                rv.append(o)
            return rv

        return pfn


###
# bindings


@dc.dataclass(frozen=True)
class _InjectorBindings(InjectorBindings):
    bs: ta.Optional[ta.Sequence[InjectorBinding]] = None
    ps: ta.Optional[ta.Sequence[InjectorBindings]] = None

    def bindings(self) -> ta.Iterator[InjectorBinding]:
        if self.bs is not None:
            yield from self.bs
        if self.ps is not None:
            for p in self.ps:
                yield from p.bindings()


def as_injector_bindings(*args: InjectorBindingOrBindings) -> InjectorBindings:
    bs: ta.List[InjectorBinding] = []
    ps: ta.List[InjectorBindings] = []

    for a in args:
        if isinstance(a, InjectorBindings):
            ps.append(a)
        elif isinstance(a, InjectorBinding):
            bs.append(a)
        else:
            raise TypeError(a)

    return _InjectorBindings(
        bs or None,
        ps or None,
    )


##


def build_injector_provider_map(bs: InjectorBindings) -> ta.Mapping[InjectorKey, InjectorProvider]:
    pm: ta.Dict[InjectorKey, InjectorProvider] = {}
    am: ta.Dict[InjectorKey, ta.List[InjectorProvider]] = {}

    for b in bs.bindings():
        if b.key.array:
            al = am.setdefault(b.key, [])
            if isinstance(b.provider, ArrayInjectorProvider):
                al.extend(b.provider.ps)
            else:
                al.append(b.provider)
        else:
            if b.key in pm:
                raise KeyError(b.key)
            pm[b.key] = b.provider

    if am:
        for k, aps in am.items():
            pm[k] = ArrayInjectorProvider(aps)

    return pm


###
# overrides


@dc.dataclass(frozen=True)
class OverridesInjectorBindings(InjectorBindings):
    p: InjectorBindings
    m: ta.Mapping[InjectorKey, InjectorBinding]

    def bindings(self) -> ta.Iterator[InjectorBinding]:
        for b in self.p.bindings():
            yield self.m.get(b.key, b)


def injector_override(p: InjectorBindings, *args: InjectorBindingOrBindings) -> InjectorBindings:
    m: ta.Dict[InjectorKey, InjectorBinding] = {}

    for b in as_injector_bindings(*args).bindings():
        if b.key in m:
            raise DuplicateInjectorKeyError(b.key)
        m[b.key] = b

    return OverridesInjectorBindings(p, m)


###
# scopes


class InjectorScope(Abstract):
    def __init__(
            self,
            *,
            _i: Injector,
    ) -> None:
        super().__init__()

        self._i = _i

        all_seeds: ta.Iterable[_InjectorScopeSeed] = self._i.provide(InjectorKey(_InjectorScopeSeed, array=True))
        self._sks = {s.k for s in all_seeds if s.sc is type(self)}

    #

    @dc.dataclass(frozen=True)
    class State:
        seeds: ta.Dict[InjectorKey, ta.Any]
        provisions: ta.Dict[InjectorKey, ta.Any] = dc.field(default_factory=dict)

    def new_state(self, vs: ta.Mapping[InjectorKey, ta.Any]) -> State:
        vs = dict(vs)
        check.equal(set(vs.keys()), self._sks)
        return InjectorScope.State(vs)

    #

    @abc.abstractmethod
    def state(self) -> State:
        raise NotImplementedError

    @abc.abstractmethod
    def enter(self, vs: ta.Mapping[InjectorKey, ta.Any]) -> ta.ContextManager[None]:
        raise NotImplementedError


class ExclusiveInjectorScope(InjectorScope, Abstract):
    _st: ta.Optional[InjectorScope.State] = None

    def state(self) -> InjectorScope.State:
        return check.not_none(self._st)

    @contextlib.contextmanager
    def enter(self, vs: ta.Mapping[InjectorKey, ta.Any]) -> ta.Iterator[None]:
        check.none(self._st)
        self._st = self.new_state(vs)
        try:
            yield
        finally:
            self._st = None


class ContextvarInjectorScope(InjectorScope, Abstract):
    _cv: contextvars.ContextVar

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_in(Abstract, cls.__bases__)
        check.not_in(abc.ABC, cls.__bases__)
        check.state(not hasattr(cls, '_cv'))
        cls._cv = contextvars.ContextVar(f'{cls.__name__}_cv')

    def state(self) -> InjectorScope.State:
        return self._cv.get()

    @contextlib.contextmanager
    def enter(self, vs: ta.Mapping[InjectorKey, ta.Any]) -> ta.Iterator[None]:
        try:
            self._cv.get()
        except LookupError:
            pass
        else:
            raise RuntimeError(f'Scope already entered: {self}')
        st = self.new_state(vs)
        tok = self._cv.set(st)
        try:
            yield
        finally:
            self._cv.reset(tok)


#


@dc.dataclass(frozen=True)
class ScopedInjectorProvider(InjectorProvider):
    p: InjectorProvider
    k: InjectorKey
    sc: ta.Type[InjectorScope]

    def __post_init__(self) -> None:
        check.isinstance(self.p, InjectorProvider)
        check.isinstance(self.k, InjectorKey)
        check.issubclass(self.sc, InjectorScope)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            st = i[self.sc].state()
            try:
                return st.provisions[self.k]
            except KeyError:
                pass
            v = ufn(i)
            st.provisions[self.k] = v
            return v

        ufn = self.p.provider_fn()
        return pfn


@dc.dataclass(frozen=True)
class _ScopeSeedInjectorProvider(InjectorProvider):
    k: InjectorKey
    sc: ta.Type[InjectorScope]

    def __post_init__(self) -> None:
        check.isinstance(self.k, InjectorKey)
        check.issubclass(self.sc, InjectorScope)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            st = i[self.sc].state()
            return st.seeds[self.k]
        return pfn


def bind_injector_scope(sc: ta.Type[InjectorScope]) -> InjectorBindingOrBindings:
    return InjectorBinder.bind(sc, singleton=True)


#


@dc.dataclass(frozen=True)
class _InjectorScopeSeed:
    sc: ta.Type['InjectorScope']
    k: InjectorKey

    def __post_init__(self) -> None:
        check.issubclass(self.sc, InjectorScope)
        check.isinstance(self.k, InjectorKey)


def bind_injector_scope_seed(k: ta.Any, sc: ta.Type[InjectorScope]) -> InjectorBindingOrBindings:
    kk = as_injector_key(k)
    return as_injector_bindings(
        InjectorBinding(kk, _ScopeSeedInjectorProvider(kk, sc)),
        InjectorBinder.bind(_InjectorScopeSeed(sc, kk), array=True),
    )


###
# inspection


class _InjectionInspection(ta.NamedTuple):
    signature: inspect.Signature
    type_hints: ta.Mapping[str, ta.Any]
    args_offset: int


_INJECTION_INSPECTION_CACHE: ta.MutableMapping[ta.Any, _InjectionInspection] = weakref.WeakKeyDictionary()


def _do_injection_inspect(obj: ta.Any) -> _InjectionInspection:
    tgt = obj

    # inspect.signature(eval_str=True) was added in 3.10 and we have to support 3.8, so we have to get_type_hints to
    # eval str annotations *in addition to* getting the signature for parameter information.
    uw = tgt
    has_partial = False
    while True:
        if isinstance(uw, functools.partial):
            uw = uw.func
            has_partial = True
        else:
            if (uw2 := inspect.unwrap(uw)) is uw:
                break
            uw = uw2

    has_args_offset = False

    if isinstance(tgt, type) and tgt.__new__ is not object.__new__:
        # Python 3.8's inspect.signature can't handle subclasses overriding __new__, always generating *args/**kwargs.
        #  - https://bugs.python.org/issue40897
        #  - https://github.com/python/cpython/commit/df7c62980d15acd3125dfbd81546dad359f7add7
        tgt = tgt.__init__  # type: ignore[misc]
        has_args_offset = True

    if tgt in (object.__init__, object.__new__):
        # inspect strips self for types but not the underlying methods.
        def dummy(self):
            pass
        tgt = dummy
        has_args_offset = True

    if has_partial and has_args_offset:
        # TODO: unwrap partials masking parameters like modern python
        raise InjectorError(
            'Injector inspection does not currently support both an args offset and a functools.partial: '
            f'{obj}',
        )

    return _InjectionInspection(
        inspect.signature(tgt),
        ta.get_type_hints(uw),
        1 if has_args_offset else 0,
    )


def _injection_inspect(obj: ta.Any) -> _InjectionInspection:
    try:
        return _INJECTION_INSPECTION_CACHE[obj]
    except TypeError:
        return _do_injection_inspect(obj)
    except KeyError:
        pass
    insp = _do_injection_inspect(obj)
    _INJECTION_INSPECTION_CACHE[obj] = insp
    return insp


class InjectionKwarg(ta.NamedTuple):
    name: str
    key: InjectorKey
    has_default: bool


class InjectionKwargsTarget(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Sequence[InjectionKwarg]


def build_injection_kwargs_target(
        obj: ta.Any,
        *,
        skip_args: int = 0,
        skip_kwargs: ta.Optional[ta.Iterable[str]] = None,
        raw_optional: bool = False,
) -> InjectionKwargsTarget:
    insp = _injection_inspect(obj)

    params = list(insp.signature.parameters.values())

    skip_names: ta.Set[str] = set()
    if skip_kwargs is not None:
        skip_names.update(check.not_isinstance(skip_kwargs, str))

    seen: ta.Set[InjectorKey] = set()
    kws: ta.List[InjectionKwarg] = []
    for p in params[insp.args_offset + skip_args:]:
        if p.name in skip_names:
            continue

        if p.annotation is inspect.Signature.empty:
            if p.default is not inspect.Parameter.empty:
                raise KeyError(f'{obj}, {p.name}')
            continue

        if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            raise TypeError(insp)

        # 3.8 inspect.signature doesn't eval_str but typing.get_type_hints does, so prefer that.
        ann = insp.type_hints.get(p.name, p.annotation)
        if (
                not raw_optional and
                is_optional_alias(ann)
        ):
            ann = get_optional_alias_arg(ann)

        k = as_injector_key(ann)

        if k in seen:
            raise DuplicateInjectorKeyError(k)
        seen.add(k)

        kws.append(InjectionKwarg(
            p.name,
            k,
            p.default is not inspect.Parameter.empty,
        ))

    return InjectionKwargsTarget(
        obj,
        kws,
    )


###
# injector


_INJECTOR_INJECTOR_KEY: InjectorKey[Injector] = InjectorKey(Injector)


@dc.dataclass(frozen=True)
class _InjectorEager:
    key: InjectorKey


_INJECTOR_EAGER_ARRAY_KEY: InjectorKey[_InjectorEager] = InjectorKey(_InjectorEager, array=True)


class _Injector(Injector):
    _DEFAULT_BINDINGS: ta.ClassVar[ta.List[InjectorBinding]] = []

    def __init__(self, bs: InjectorBindings, p: ta.Optional[Injector] = None) -> None:
        super().__init__()

        self._bs = check.isinstance(bs, InjectorBindings)
        self._p: ta.Optional[Injector] = check.isinstance(p, (Injector, type(None)))

        self._pfm = {
            k: v.provider_fn()
            for k, v in build_injector_provider_map(as_injector_bindings(
                *self._DEFAULT_BINDINGS,
                bs,
            )).items()
        }

        if _INJECTOR_INJECTOR_KEY in self._pfm:
            raise DuplicateInjectorKeyError(_INJECTOR_INJECTOR_KEY)

        self.__cur_req: ta.Optional[_Injector._Request] = None

        if _INJECTOR_EAGER_ARRAY_KEY in self._pfm:
            for e in self.provide(_INJECTOR_EAGER_ARRAY_KEY):
                self.provide(e.key)

    class _Request:
        def __init__(self, injector: '_Injector') -> None:
            super().__init__()

            self._injector = injector
            self._provisions: ta.Dict[InjectorKey, Maybe] = {}
            self._seen_keys: ta.Set[InjectorKey] = set()

        def handle_key(self, key: InjectorKey) -> Maybe[Maybe]:
            try:
                return Maybe.just(self._provisions[key])
            except KeyError:
                pass
            if key in self._seen_keys:
                raise CyclicDependencyInjectorKeyError(key)
            self._seen_keys.add(key)
            return Maybe.empty()

        def handle_provision(self, key: InjectorKey, mv: Maybe) -> Maybe:
            check.in_(key, self._seen_keys)
            check.not_in(key, self._provisions)
            self._provisions[key] = mv
            return mv

    @contextlib.contextmanager
    def _current_request(self) -> ta.Generator[_Request, None, None]:
        if (cr := self.__cur_req) is not None:
            yield cr
            return

        cr = self._Request(self)
        try:
            self.__cur_req = cr
            yield cr
        finally:
            self.__cur_req = None

    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        key = as_injector_key(key)

        cr: _Injector._Request
        with self._current_request() as cr:
            if (rv := cr.handle_key(key)).present:
                return rv.must()

            if key == _INJECTOR_INJECTOR_KEY:
                return cr.handle_provision(key, Maybe.just(self))

            fn = self._pfm.get(key)
            if fn is not None:
                return cr.handle_provision(key, Maybe.just(fn(self)))

            if self._p is not None:
                pv = self._p.try_provide(key)
                if pv is not None:
                    return cr.handle_provision(key, Maybe.empty())

            return cr.handle_provision(key, Maybe.empty())

    def provide(self, key: ta.Any) -> ta.Any:
        v = self.try_provide(key)
        if v.present:
            return v.must()
        raise UnboundInjectorKeyError(key)

    def provide_kwargs(
            self,
            obj: ta.Any,
            *,
            skip_args: int = 0,
            skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
    ) -> ta.Mapping[str, ta.Any]:
        kt = build_injection_kwargs_target(
            obj,
            skip_args=skip_args,
            skip_kwargs=skip_kwargs,
        )

        ret: ta.Dict[str, ta.Any] = {}
        for kw in kt.kwargs:
            if kw.has_default:
                if not (mv := self.try_provide(kw.key)).present:
                    continue
                v = mv.must()
            else:
                v = self.provide(kw.key)
            ret[kw.name] = v
        return ret

    def inject(
            self,
            obj: ta.Any,
            *,
            args: ta.Optional[ta.Sequence[ta.Any]] = None,
            kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Any:
        provided = self.provide_kwargs(
            obj,
            skip_args=len(args) if args is not None else 0,
            skip_kwargs=kwargs if kwargs is not None else None,
        )

        return obj(
            *(args if args is not None else ()),
            **(kwargs if kwargs is not None else {}),
            **provided,
        )


###
# binder


class InjectorBinder:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    _FN_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        types.FunctionType,
        types.MethodType,

        classmethod,
        staticmethod,

        functools.partial,
        functools.partialmethod,
    )

    @classmethod
    def _is_fn(cls, obj: ta.Any) -> bool:
        return isinstance(obj, cls._FN_TYPES)

    @classmethod
    def bind_as_fn(cls, icls: ta.Type[T]) -> ta.Type[T]:
        check.isinstance(icls, type)
        if icls not in cls._FN_TYPES:
            cls._FN_TYPES = (*cls._FN_TYPES, icls)
        return icls

    _BANNED_BIND_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        InjectorProvider,
    )

    @classmethod
    def bind(
            cls,
            obj: ta.Any,
            *,
            key: ta.Any = None,
            tag: ta.Any = None,
            array: ta.Optional[bool] = None,  # noqa

            to_fn: ta.Any = None,
            to_ctor: ta.Any = None,
            to_const: ta.Any = None,
            to_key: ta.Any = None,

            in_: ta.Optional[ta.Type[InjectorScope]] = None,
            singleton: bool = False,

            eager: bool = False,
    ) -> InjectorBindingOrBindings:
        if obj is None or obj is inspect.Parameter.empty:
            raise TypeError(obj)
        if isinstance(obj, cls._BANNED_BIND_TYPES):
            raise TypeError(obj)

        #

        if key is not None:
            key = as_injector_key(key)

        #

        has_to = (
            to_fn is not None or
            to_ctor is not None or
            to_const is not None or
            to_key is not None
        )
        if isinstance(obj, InjectorKey):
            if key is None:
                key = obj
        elif isinstance(obj, type):
            if not has_to:
                to_ctor = obj
            if key is None:
                key = InjectorKey(obj)
        elif cls._is_fn(obj) and not has_to:
            to_fn = obj
            if key is None:
                insp = _injection_inspect(obj)
                key_cls: ta.Any = check_valid_injector_key_cls(check.not_none(insp.type_hints.get('return')))
                key = InjectorKey(key_cls)
        else:
            if to_const is not None:
                raise TypeError('Cannot bind instance with to_const')
            to_const = obj
            if key is None:
                key = InjectorKey(type(obj))
        del has_to

        #

        if tag is not None:
            if key.tag is not None:
                raise TypeError('Tag already set')
            key = dc.replace(key, tag=tag)

        if array is not None:
            key = dc.replace(key, array=array)

        #

        providers: ta.List[InjectorProvider] = []
        if to_fn is not None:
            providers.append(FnInjectorProvider(to_fn))
        if to_ctor is not None:
            providers.append(CtorInjectorProvider(to_ctor))
        if to_const is not None:
            providers.append(ConstInjectorProvider(to_const))
        if to_key is not None:
            providers.append(LinkInjectorProvider(as_injector_key(to_key)))
        if not providers:
            raise TypeError('Must specify provider')
        if len(providers) > 1:
            raise TypeError('May not specify multiple providers')
        provider = check.single(providers)

        #

        pws: ta.List[ta.Any] = []
        if in_ is not None:
            check.issubclass(in_, InjectorScope)
            check.not_in(Abstract, in_.__bases__)
            pws.append(functools.partial(ScopedInjectorProvider, k=key, sc=in_))
        if singleton:
            pws.append(SingletonInjectorProvider)
        if len(pws) > 1:
            raise TypeError('May not specify multiple provider wrappers')
        elif pws:
            provider = check.single(pws)(provider)

        #

        binding = InjectorBinding(key, provider)

        #

        extras: ta.List[InjectorBinding] = []

        if eager:
            extras.append(bind_injector_eager_key(key))

        #

        if extras:
            return as_injector_bindings(binding, *extras)
        else:
            return binding


###
# injection helpers


def make_injector_factory(
        fn: ta.Callable[..., T],
        cls: U,
        ann: ta.Any = None,
) -> ta.Callable[..., U]:
    if ann is None:
        ann = cls

    def outer(injector: Injector) -> ann:
        def inner(*args, **kwargs):
            return injector.inject(fn, args=args, kwargs=kwargs)
        return cls(inner)  # type: ignore

    return outer


def bind_injector_array(
        obj: ta.Any = None,
        *,
        tag: ta.Any = None,
) -> InjectorBindingOrBindings:
    key = as_injector_key(obj)
    if tag is not None:
        if key.tag is not None:
            raise ValueError('Must not specify multiple tags')
        key = dc.replace(key, tag=tag)

    if key.array:
        raise ValueError('Key must not be array')

    return InjectorBinding(
        dc.replace(key, array=True),
        ArrayInjectorProvider([]),
    )


def make_injector_array_type(
        ele: ta.Union[InjectorKey, InjectorKeyCls],
        cls: U,
        ann: ta.Any = None,
) -> ta.Callable[..., U]:
    if isinstance(ele, InjectorKey):
        if not ele.array:
            raise InjectorError('Provided key must be array', ele)
        key = ele
    else:
        key = dc.replace(as_injector_key(ele), array=True)

    if ann is None:
        ann = cls

    def inner(injector: Injector) -> ann:
        return cls(injector.provide(key))  # type: ignore[operator]

    return inner


def bind_injector_eager_key(key: ta.Any) -> InjectorBinding:
    return InjectorBinding(_INJECTOR_EAGER_ARRAY_KEY, ConstInjectorProvider(_InjectorEager(as_injector_key(key))))


###
# api


class InjectionApi:
    # keys

    def as_key(self, o: ta.Any) -> InjectorKey:
        return as_injector_key(o)

    def array(self, o: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), array=True)

    def tag(self, o: ta.Any, t: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), tag=t)

    # bindings

    def as_bindings(self, *args: InjectorBindingOrBindings) -> InjectorBindings:
        return as_injector_bindings(*args)

    # overrides

    def override(self, p: InjectorBindings, *args: InjectorBindingOrBindings) -> InjectorBindings:
        return injector_override(p, *args)

    # scopes

    def bind_scope(self, sc: ta.Type[InjectorScope]) -> InjectorBindingOrBindings:
        return bind_injector_scope(sc)

    def bind_scope_seed(self, k: ta.Any, sc: ta.Type[InjectorScope]) -> InjectorBindingOrBindings:
        return bind_injector_scope_seed(k, sc)

    # injector

    def create_injector(self, *args: InjectorBindingOrBindings, parent: ta.Optional[Injector] = None) -> Injector:
        return _Injector(as_injector_bindings(*args), parent)

    # binder

    def bind(
            self,
            obj: ta.Any,
            *,
            key: ta.Any = None,
            tag: ta.Any = None,
            array: ta.Optional[bool] = None,  # noqa

            to_fn: ta.Any = None,
            to_ctor: ta.Any = None,
            to_const: ta.Any = None,
            to_key: ta.Any = None,

            in_: ta.Optional[ta.Type[InjectorScope]] = None,
            singleton: bool = False,

            eager: bool = False,
    ) -> InjectorBindingOrBindings:
        return InjectorBinder.bind(
            obj,

            key=key,
            tag=tag,
            array=array,

            to_fn=to_fn,
            to_ctor=to_ctor,
            to_const=to_const,
            to_key=to_key,

            in_=in_,
            singleton=singleton,

            eager=eager,
        )

    # helpers

    def bind_factory(
            self,
            fn: ta.Callable[..., T],
            cls_: U,
            ann: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return self.bind(make_injector_factory(fn, cls_, ann))

    def bind_array(
            self,
            obj: ta.Any = None,
            *,
            tag: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return bind_injector_array(obj, tag=tag)

    def bind_array_type(
            self,
            ele: ta.Union[InjectorKey, InjectorKeyCls],
            cls_: U,
            ann: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return self.bind(make_injector_array_type(ele, cls_, ann))


inj = InjectionApi()


########################################
# ../../../omlish/logs/contexts.py


##


class LoggingContext(Abstract):
    @abc.abstractmethod
    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        raise NotImplementedError

    @ta.final
    def __getitem__(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self.get_info(ty)

    @ta.final
    def must_get_info(self, ty: ta.Type[LoggingContextInfoT]) -> LoggingContextInfoT:
        if (info := self.get_info(ty)) is None:
            raise TypeError(f'LoggingContextInfo absent: {ty}')
        return info


@ta.final
class SimpleLoggingContext(LoggingContext):
    def __init__(self, *infos: LoggingContextInfo) -> None:
        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {type(i): i for i in infos}

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)


##


class CaptureLoggingContext(LoggingContext, Abstract):
    @abc.abstractmethod
    def set_basic(
            self,
            name: str,

            msg: ta.Union[str, tuple, LoggingMsgFn],
            args: tuple,
    ) -> 'CaptureLoggingContext':
        raise NotImplementedError

    #

    class AlreadyCapturedError(Exception):
        pass

    class NotCapturedError(Exception):
        pass

    @abc.abstractmethod
    def capture(self) -> None:
        """Must be cooperatively called only from the expected locations."""

        raise NotImplementedError


@ta.final
class CaptureLoggingContextImpl(CaptureLoggingContext):
    @ta.final
    class NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    #

    def __init__(
            self,
            level: LogLevel,
            *,
            time_ns: ta.Optional[int] = None,

            exc_info: LoggingExcInfoArg = False,

            caller: ta.Union[LoggingContextInfos.Caller, ta.Type[NOT_SET], None] = NOT_SET,
            stack_offset: int = 0,
            stack_info: bool = False,
    ) -> None:
        if time_ns is None:
            time_ns = time.time_ns()

        # Done early to not trample on sys.exc_info()
        exc = LoggingContextInfos.Exc.build(exc_info)

        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {}
        self._set_info(
            LoggingContextInfos.Level.build(level),
            exc,
            LoggingContextInfos.Time.build(time_ns),
        )

        if caller is not CaptureLoggingContextImpl.NOT_SET:
            self._infos[LoggingContextInfos.Caller] = caller
        else:
            self._stack_offset = stack_offset
            self._stack_info = stack_info

    def _set_info(self, *infos: ta.Optional[LoggingContextInfo]) -> 'CaptureLoggingContextImpl':
        for info in infos:
            if info is not None:
                self._infos[type(info)] = info
        return self

    def get_infos(self) -> ta.Mapping[ta.Type[LoggingContextInfo], LoggingContextInfo]:
        return self._infos

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)

    ##

    def set_basic(
            self,
            name: str,

            msg: ta.Union[str, tuple, LoggingMsgFn],
            args: tuple,
    ) -> 'CaptureLoggingContextImpl':
        return self._set_info(
            LoggingContextInfos.Name(name),
            LoggingContextInfos.Msg.build(msg, *args),
        )

    ##

    _stack_offset: int
    _stack_info: bool

    def inc_stack_offset(self, ofs: int = 1) -> 'CaptureLoggingContextImpl':
        if hasattr(self, '_stack_offset'):
            self._stack_offset += ofs
        return self

    _has_captured: bool = False

    def capture(self) -> None:
        if self._has_captured:
            raise CaptureLoggingContextImpl.AlreadyCapturedError
        self._has_captured = True

        if LoggingContextInfos.Caller not in self._infos:
            self._set_info(LoggingContextInfos.Caller.build(
                self._stack_offset + 1,
                stack_info=self._stack_info,
            ))

        if (caller := self[LoggingContextInfos.Caller]) is not None:
            self._set_info(LoggingContextInfos.SourceFile.build(
                caller.file_path,
            ))

        self._set_info(
            LoggingContextInfos.Thread.build(),
            LoggingContextInfos.Process.build(),
            LoggingContextInfos.Multiprocessing.build(),
            LoggingContextInfos.AsyncioTask.build(),
        )


########################################
# ../../../omlish/logs/std/standard.py
"""
TODO:
 - structured
 - prefixed
 - debug
 - optional noisy? noisy will never be lite - some kinda configure_standard callback mechanism?
"""


##


STANDARD_LOG_FORMAT_PARTS = [
    ('asctime', '%(asctime)-15s'),
    ('process', 'pid=%(process)s'),
    ('thread', 'tid=%(thread)x'),
    ('levelname', '%(levelname)s'),
    ('name', '%(name)s'),
    ('separator', '::'),
    ('message', '%(message)s'),
]


class StandardLoggingFormatter(logging.Formatter):
    @staticmethod
    def build_log_format(parts: ta.Iterable[ta.Tuple[str, str]]) -> str:
        return ' '.join(v for k, v in parts)

    converter = datetime.datetime.fromtimestamp  # type: ignore

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            return ct.strftime(datefmt)  # noqa
        else:
            t = ct.strftime('%Y-%m-%d %H:%M:%S')
            return '%s.%03d' % (t, record.msecs)  # noqa


##


class StandardConfiguredLoggingHandler(ProxyLoggingHandler):
    def __init_subclass__(cls, **kwargs):
        raise TypeError('This class serves only as a marker and should not be subclassed.')


##


@contextlib.contextmanager
def _locking_logging_module_lock() -> ta.Iterator[None]:
    if hasattr(logging, '_acquireLock'):
        logging._acquireLock()  # noqa
        try:
            yield
        finally:
            logging._releaseLock()  # type: ignore  # noqa

    elif hasattr(logging, '_lock'):
        # https://github.com/python/cpython/commit/74723e11109a320e628898817ab449b3dad9ee96
        with logging._lock:  # noqa
            yield

    else:
        raise Exception("Can't find lock in logging module")


def configure_standard_logging(
        level: ta.Union[int, str] = logging.INFO,
        *,
        target: ta.Optional[logging.Logger] = None,

        force: bool = False,

        handler_factory: ta.Optional[ta.Callable[[], logging.Handler]] = None,

        formatter: ta.Optional[logging.Formatter] = None,  # noqa
        json: bool = False,
) -> ta.Optional[StandardConfiguredLoggingHandler]:
    with _locking_logging_module_lock():
        if target is None:
            target = logging.root

        #

        if not force:
            if any(isinstance(h, StandardConfiguredLoggingHandler) for h in list(target.handlers)):
                return None

        #

        if handler_factory is not None:
            handler = handler_factory()
        else:
            handler = logging.StreamHandler()

        #

        if formatter is None:
            if json:
                formatter = JsonLoggingFormatter()
            else:
                formatter = StandardLoggingFormatter(StandardLoggingFormatter.build_log_format(STANDARD_LOG_FORMAT_PARTS))  # noqa
        handler.setFormatter(formatter)

        #

        handler.addFilter(TidLoggingFilter())

        #

        target.addHandler(handler)

        #

        if level is not None:
            target.setLevel(level)

        #

        return StandardConfiguredLoggingHandler(handler)


########################################
# ../../../omlish/logs/utils.py


##


def exception_logging(log, exc_cls=Exception):  # noqa
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exc_cls as e:  # noqa
                log.exception('Error in %r', fn)
                raise

        return inner

    return outer


def async_exception_logging(alog, exc_cls=Exception):  # noqa
    def outer(fn):
        @functools.wraps(fn)
        async def inner(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except exc_cls as e:  # noqa
                await alog.exception('Error in %r', fn)
                raise

        return inner

    return outer


##


class LogTimingContext:
    DEFAULT_LOG: ta.ClassVar[ta.Optional[LoggerLike]] = None

    class _NOT_SPECIFIED:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def __init__(
            self,
            description: str,
            *,
            log: ta.Union[LoggerLike, ta.Type[_NOT_SPECIFIED], None] = _NOT_SPECIFIED,  # noqa
            level: int = logging.DEBUG,
    ) -> None:
        super().__init__()

        self._description = description
        if log is self._NOT_SPECIFIED:
            log = self.DEFAULT_LOG  # noqa
        self._log: ta.Optional[LoggerLike] = log  # type: ignore
        self._level = level

    def set_description(self, description: str) -> 'LogTimingContext':
        self._description = description
        return self

    _begin_time: float
    _end_time: float

    def __enter__(self) -> 'LogTimingContext':
        self._begin_time = time.time()

        if self._log is not None:
            self._log.log(self._level, f'Begin : {self._description}')  # noqa

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.time()

        if self._log is not None:
            self._log.log(
                self._level,
                f'End : {self._description} - {self._end_time - self._begin_time:0.2f} s elapsed',
            )


log_timing_context = LogTimingContext


########################################
# ../../../omlish/sockets/server/handlers.py


##


class SocketServerHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, conn: SocketAndAddress) -> None:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class StandardSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler

    timeout: ta.Optional[float] = None

    # http://bugs.python.org/issue6192
    # TODO: https://eklitzke.org/the-caveats-of-tcp-nodelay
    disable_nagle_algorithm: bool = False

    no_close: bool = False

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            if self.timeout is not None:
                conn.socket.settimeout(self.timeout)

            if self.disable_nagle_algorithm:
                conn.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

            self.handler(conn)

        finally:
            close_socket_immediately(conn.socket)


#


@dc.dataclass(frozen=True)
class CallbackWrappedSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler

    before_handle: ta.Optional[SocketServerHandler] = None
    after_handle: ta.Optional[SocketServerHandler] = None

    # Return True if suppress like __exit__
    on_error: ta.Optional[ta.Callable[[SocketAndAddress, Exception], bool]] = None

    finally_: ta.Optional[SocketServerHandler] = None

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            if (before_handle := self.before_handle) is not None:
                before_handle(conn)

            self.handler(conn)

        except Exception as e:
            if (on_error := self.on_error) is not None and on_error(conn, e):
                pass
            else:
                raise

        else:
            if (after_handle := self.after_handle) is not None:
                after_handle(conn)

        finally:
            if (finally_ := self.finally_) is not None:
                finally_(conn)


#


@dc.dataclass(frozen=True)
class SocketHandlerSocketServerHandler(SocketServerHandler_):
    handler: SocketHandler

    r_buf_size: int = -1
    w_buf_size: int = 0

    def __call__(self, conn: SocketAndAddress) -> None:
        fp = SocketIoPair.from_socket(
            conn.socket,
            r_buf_size=self.r_buf_size,
            w_buf_size=self.w_buf_size,
        )

        self.handler(conn.address, fp)


#


@dc.dataclass(frozen=True)
class SocketWrappingSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler
    wrapper: ta.Callable[[SocketAndAddress], SocketAndAddress]

    def __call__(self, conn: SocketAndAddress) -> None:
        wrapped_conn = self.wrapper(conn)
        self.handler(wrapped_conn)


#

@dc.dataclass(frozen=True)
class ExecutorSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler
    executor: cf.Executor

    def __call__(self, conn: SocketAndAddress) -> None:
        self.executor.submit(self.handler, conn)


#


@dc.dataclass(frozen=True)
class ExceptionLoggingSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler
    log: LoggerLike

    ignored: ta.Optional[ta.Container[ta.Type[Exception]]] = None

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            return self.handler(conn)

        except Exception as e:  # noqa
            if (ignored := self.ignored) is None or type(e) not in ignored:
                self.log.exception('Error in handler %r for conn %r', self.handler, conn)

            raise


########################################
# ../../../omlish/subprocesses/run.py


##


@dc.dataclass(frozen=True)
class SubprocessRunOutput(ta.Generic[T]):
    proc: T

    returncode: int  # noqa

    stdout: ta.Optional[bytes] = None
    stderr: ta.Optional[bytes] = None


##


@dc.dataclass(frozen=True)
class SubprocessRun:
    cmd: ta.Sequence[str]
    input: ta.Any = None
    timeout: TimeoutLike = None
    check: bool = False
    capture_output: ta.Optional[bool] = None
    kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None

    #

    _FIELD_NAMES: ta.ClassVar[ta.FrozenSet[str]]

    def replace(self, **kwargs: ta.Any) -> 'SubprocessRun':
        if not kwargs:
            return self

        field_kws = {}
        extra_kws = {}
        for k, v in kwargs.items():
            if k in self._FIELD_NAMES:
                field_kws[k] = v
            else:
                extra_kws[k] = v

        return dc.replace(self, **{
            **dict(kwargs={
                **(self.kwargs or {}),
                **extra_kws,
            }),
            **field_kws,  # passing a kwarg named 'kwargs' intentionally clobbers
        })

    #

    @classmethod
    def of(
            cls,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
            check: bool = False,  # noqa
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> 'SubprocessRun':
        return cls(
            cmd=cmd,
            input=input,
            timeout=timeout,
            check=check,
            capture_output=capture_output,
            kwargs=kwargs,
        )

    #

    _DEFAULT_SUBPROCESSES: ta.ClassVar[ta.Optional[ta.Any]] = None  # AbstractSubprocesses

    def run(
            self,
            subprocesses: ta.Optional[ta.Any] = None,  # AbstractSubprocesses
            **kwargs: ta.Any,
    ) -> SubprocessRunOutput:
        if subprocesses is None:
            subprocesses = self._DEFAULT_SUBPROCESSES
        return check.not_none(subprocesses).run_(self.replace(**kwargs))

    _DEFAULT_ASYNC_SUBPROCESSES: ta.ClassVar[ta.Optional[ta.Any]] = None  # AbstractAsyncSubprocesses

    async def async_run(
            self,
            async_subprocesses: ta.Optional[ta.Any] = None,  # AbstractAsyncSubprocesses
            **kwargs: ta.Any,
    ) -> SubprocessRunOutput:
        if async_subprocesses is None:
            async_subprocesses = self._DEFAULT_ASYNC_SUBPROCESSES
        return await check.not_none(async_subprocesses).run_(self.replace(**kwargs))

    _DEFAULT_MAYSYNC_SUBPROCESSES: ta.ClassVar[ta.Optional[ta.Any]] = None  # AbstractMaysyncSubprocesses

    async def maysync_run(
            self,
            maysync_subprocesses: ta.Optional[ta.Any] = None,  # AbstractMaysyncSubprocesses
            **kwargs: ta.Any,
    ) -> SubprocessRunOutput:
        if maysync_subprocesses is None:
            maysync_subprocesses = self._DEFAULT_MAYSYNC_SUBPROCESSES
        return await check.not_none(maysync_subprocesses).run_(self.replace(**kwargs))


SubprocessRun._FIELD_NAMES = frozenset(fld.name for fld in dc.fields(SubprocessRun))  # noqa


##


class SubprocessRunnable(Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def make_run(self) -> SubprocessRun:
        raise NotImplementedError

    @abc.abstractmethod
    def handle_run_output(self, output: SubprocessRunOutput) -> T:
        raise NotImplementedError

    #

    def run(
            self,
            subprocesses: ta.Optional[ta.Any] = None,  # AbstractSubprocesses
            **kwargs: ta.Any,
    ) -> T:
        return self.handle_run_output(self.make_run().run(subprocesses, **kwargs))

    async def async_run(
            self,
            async_subprocesses: ta.Optional[ta.Any] = None,  # AbstractAsyncSubprocesses
            **kwargs: ta.Any,
    ) -> T:
        return self.handle_run_output(await self.make_run().async_run(async_subprocesses, **kwargs))

    async def maysync_run(
            self,
            maysync_subprocesses: ta.Optional[ta.Any] = None,  # AbstractMaysyncSubprocesses
            **kwargs: ta.Any,
    ) -> T:
        return self.handle_run_output(await self.make_run().maysync_run(maysync_subprocesses, **kwargs))


########################################
# ../../../omlish/subprocesses/wrap.py
"""
This bypasses debuggers attaching to spawned subprocess children that look like python processes. See:

  https://github.com/JetBrains/intellij-community/blob/e9d8f126c286acf9df3ff272f440b305bf2ff585/python/helpers/pydev/_pydev_bundle/pydev_monkey.py
"""


##


_SUBPROCESS_SHELL_WRAP_EXECS = False


def subprocess_shell_wrap_exec(*cmd: str) -> ta.Tuple[str, ...]:
    return ('sh', '-c', ' '.join(map(shlex.quote, cmd)))


def subprocess_maybe_shell_wrap_exec(*cmd: str) -> ta.Tuple[str, ...]:
    if _SUBPROCESS_SHELL_WRAP_EXECS or is_debugger_attached():
        return subprocess_shell_wrap_exec(*cmd)
    else:
        return cmd


########################################
# ../../dataserver/handlers.py


##


@dc.dataclass(frozen=True)
class DataServerRequest:
    method: str
    path: str


@dc.dataclass(frozen=True)
class DataServerResponse:
    status: int
    headers: ta.Optional[ta.Mapping[str, str]] = None
    body: ta.Optional[io.IOBase] = None

    #

    def close(self) -> None:
        if (body := self.body) is not None:
            body.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DataServerError(Exception):
    pass


class DataServerHandler(Abstract):
    @abc.abstractmethod
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        raise NotImplementedError


##


class DataServerTargetHandler(DataServerHandler, Abstract, ta.Generic[DataServerTargetT]):
    def __init__(self, target: DataServerTargetT) -> None:
        super().__init__()

        self._target = target

    #

    @classmethod
    def for_target(cls, tgt: DataServerTarget, **kwargs: ta.Any) -> 'DataServerTargetHandler':
        try:
            hc = _DATA_SERVER_TARGET_HANDLERS[type(tgt)]
        except KeyError:
            raise TypeError(tgt)  # noqa
        else:
            return hc(tgt, **kwargs)

    #

    def _make_headers(self) -> ta.Dict[str, str]:
        dct = {}
        if (ct := self._target.content_type) is not None:
            dct['Content-Type'] = ct
        if (cl := self._target.content_length) is not None:
            dct['Content-Length'] = str(cl)
        return dct


#


_DATA_SERVER_TARGET_HANDLERS: ta.Dict[ta.Type[DataServerTarget], ta.Type[DataServerTargetHandler]] = {}


def _register_data_server_target_handler(*tcs):
    def inner(hc):
        check.issubclass(hc, DataServerTargetHandler)
        for tc in tcs:
            check.issubclass(tc, DataServerTarget)
            check.not_in(tc, _DATA_SERVER_TARGET_HANDLERS)
            _DATA_SERVER_TARGET_HANDLERS[tc] = hc
        return hc
    return inner


#


@_register_data_server_target_handler(BytesDataServerTarget)
class BytesDataServerTargetHandler(DataServerTargetHandler[BytesDataServerTarget]):
    def _make_headers(self) -> ta.Dict[str, str]:
        dct = super()._make_headers()
        if 'Content-Length' not in dct and self._target.data is not None:
            dct['Content-Length'] = str(len(self._target.data))
        return dct

    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method not in ('GET', 'HEAD'):
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)

        return DataServerResponse(
            http.HTTPStatus.OK,
            headers=self._make_headers(),
            body=io.BytesIO(self._target.data) if self._target.data is not None and req.method == 'GET' else None,
        )


#


@_register_data_server_target_handler(FileDataServerTarget)
class FileDataServerTargetHandler(DataServerTargetHandler[FileDataServerTarget]):
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method == 'HEAD':
            try:
                st = os.stat(check.not_none(self._target.file_path))
            except FileNotFoundError:
                return DataServerResponse(http.HTTPStatus.NOT_FOUND)

            return DataServerResponse(
                http.HTTPStatus.OK,
                headers={
                    'Content-Length': str(st.st_size),
                    **self._make_headers(),
                },
            )

        elif req.method == 'GET':
            try:
                f = open(check.not_none(self._target.file_path), 'rb')  # noqa
            except FileNotFoundError:
                return DataServerResponse(http.HTTPStatus.NOT_FOUND)

            try:
                sz = os.fstat(f.fileno())

                return DataServerResponse(
                    http.HTTPStatus.OK,
                    headers={
                        'Content-Length': str(sz.st_size),
                        **self._make_headers(),
                    },
                    body=f,  # noqa
                )

            except Exception:  # noqa
                f.close()
                raise

        else:
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)


#


@_register_data_server_target_handler(UrlDataServerTarget)
class UrlDataServerTargetHandler(DataServerTargetHandler[UrlDataServerTarget]):
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method not in check.not_none(self._target.methods):
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)

        resp: http.client.HTTPResponse = urllib.request.urlopen(urllib.request.Request(  # noqa
            method=req.method,
            url=check.not_none(self._target.url),
        ))

        try:
            return DataServerResponse(
                resp.status,
                headers=dict(resp.headers.items()),
                body=resp,
            )

        except Exception:  # noqa
            resp.close()
            raise


########################################
# ../../dataserver/routes.py
"""
TODO:
 - generate to nginx config
"""


##


@dc.dataclass(frozen=True)
class DataServerRoute:
    paths: ta.Sequence[str]
    target: DataServerTarget

    @classmethod
    def of(cls, obj: ta.Union[
        'DataServerRoute',
        ta.Tuple[
            ta.Union[str, ta.Iterable[str]],
            DataServerTarget,
        ],
    ]) -> 'DataServerRoute':
        if isinstance(obj, cls):
            return obj

        elif isinstance(obj, tuple):
            p, t = obj

            if isinstance(p, str):
                p = [p]

            return cls(
                paths=tuple(p),
                target=check.isinstance(t, DataServerTarget),
            )

        else:
            raise TypeError(obj)

    @classmethod
    def of_(cls, *objs: ta.Any) -> ta.List['DataServerRoute']:
        return [cls.of(obj) for obj in objs]


########################################
# ../../oci/media.py


##


OCI_MEDIA_FIELDS: ta.Collection[str] = frozenset([
    'schema_version',
    'media_type',
])


@dc.dataclass()
class OciMediaDataclass(Abstract):
    SCHEMA_VERSION: ta.ClassVar[int]

    @property
    def schema_version(self) -> int:
        raise TypeError

    MEDIA_TYPE: ta.ClassVar[str]

    @property
    def media_type(self) -> str:
        raise TypeError

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        for a in OCI_MEDIA_FIELDS:
            check.in_(a, cls.__dict__)


_REGISTERED_OCI_MEDIA_DATACLASSES: ta.Dict[str, ta.Type[OciMediaDataclass]] = {}


def _register_oci_media_dataclass(cls):
    check.issubclass(cls, OciMediaDataclass)
    check.arg(dc.is_dataclass(cls))
    mt = check.non_empty_str(cls.__dict__['MEDIA_TYPE'])
    check.not_in(mt, _REGISTERED_OCI_MEDIA_DATACLASSES)
    _REGISTERED_OCI_MEDIA_DATACLASSES[mt] = cls
    return cls


def get_registered_oci_media_dataclass(media_type: str) -> ta.Optional[ta.Type[OciMediaDataclass]]:
    return _REGISTERED_OCI_MEDIA_DATACLASSES.get(media_type)


def unmarshal_oci_media_dataclass(
        dct: ta.Mapping[str, ta.Any],
        *,
        media_type: ta.Optional[str] = None,
) -> ta.Any:
    if media_type is None:
        media_type = check.non_empty_str(dct['mediaType'])
    cls = _REGISTERED_OCI_MEDIA_DATACLASSES[media_type]
    return unmarshal_obj(dct, cls)


##


@dc.dataclass()
class OciMediaDescriptor:
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/descriptor.md#properties"""  # noqa

    media_type: str = dc.field(metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})
    digest: str
    size: int

    #

    urls: ta.Optional[ta.Sequence[str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa
    data: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})
    artifact_type: ta.Optional[str] = dc.field(default=None, metadata={OBJ_MARSHALER_FIELD_KEY: 'artifactType', OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    platform: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa


##


@_register_oci_media_dataclass
@dc.dataclass()
class OciMediaImageIndex(OciMediaDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/image-index.md"""

    manifests: ta.Sequence[OciMediaDescriptor]  # -> OciMediaImageIndex | OciMediaImageManifest

    #

    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.index.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


#


@_register_oci_media_dataclass
@dc.dataclass()
class OciMediaImageManifest(OciMediaDataclass):
    """https://github.com/opencontainers/image-spec/blob/92353b0bee778725c617e7d57317b568a7796bd0/manifest.md"""

    config: OciMediaDescriptor  # -> OciMediaImageConfig

    layers: ta.Sequence[OciMediaDescriptor]

    #

    annotations: ta.Optional[ta.Mapping[str, str]] = dc.field(default=None, metadata={OBJ_MARSHALER_OMIT_IF_NONE: True})  # noqa

    #

    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.manifest.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


#


OCI_IMAGE_LAYER_KIND_MEDIA_TYPES: ta.Mapping[OciImageLayer.Kind, str] = {
    OciImageLayer.Kind.TAR: 'application/vnd.oci.image.layer.v1.tar',
    OciImageLayer.Kind.TAR_GZIP: 'application/vnd.oci.image.layer.v1.tar+gzip',
    OciImageLayer.Kind.TAR_ZSTD: 'application/vnd.oci.image.layer.v1.tar+zstd',
}

OCI_IMAGE_LAYER_KIND_MEDIA_TYPES_: ta.Mapping[str, OciImageLayer.Kind] = {
    v: k
    for k, v in OCI_IMAGE_LAYER_KIND_MEDIA_TYPES.items()
}


#


@_register_oci_media_dataclass
@dc.dataclass()
class OciMediaImageConfig(OciImageConfig, OciMediaDataclass):
    SCHEMA_VERSION: ta.ClassVar[int] = 2
    schema_version: int = dc.field(default=SCHEMA_VERSION, metadata={OBJ_MARSHALER_FIELD_KEY: 'schemaVersion'})

    MEDIA_TYPE: ta.ClassVar[str] = 'application/vnd.oci.image.config.v1+json'
    media_type: str = dc.field(default=MEDIA_TYPE, metadata={OBJ_MARSHALER_FIELD_KEY: 'mediaType'})


##


OCI_MANIFEST_MEDIA_TYPES: ta.AbstractSet[str] = frozenset([
    OciMediaImageIndex.MEDIA_TYPE,
    OciMediaImageManifest.MEDIA_TYPE,
])


########################################
# ../../oci/pack/packing.py


##


class OciLayerPacker(ExitStacked):
    def __init__(
            self,
            input_file_path: str,
            output_file_paths: ta.Sequence[str],
            *,
            compression: ta.Optional[OciCompression] = None,
    ) -> None:
        super().__init__()

        self._input_file_path = input_file_path
        self._output_file_paths = list(output_file_paths)
        self._compression = compression

        self._output_file_indexes_by_name: ta.Dict[str, int] = {}

    #

    @cached_nullary
    def _input_tar_file(self) -> tarfile.TarFile:
        # FIXME: check uncompressed
        return self._enter_context(tarfile.open(self._input_file_path))

    #

    @cached_nullary
    def _entries_by_name(self) -> ta.Mapping[str, tarfile.TarInfo]:
        return {
            info.name: info
            for info in self._input_tar_file().getmembers()
        }

    #

    class _CategorizedEntries(ta.NamedTuple):
        files_by_name: ta.Mapping[str, tarfile.TarInfo]
        non_files_by_name: ta.Mapping[str, tarfile.TarInfo]
        links_by_name: ta.Mapping[str, tarfile.TarInfo]

    @cached_nullary
    def _categorized_entries(self) -> _CategorizedEntries:
        files_by_name: ta.Dict[str, tarfile.TarInfo] = {}
        non_files_by_name: ta.Dict[str, tarfile.TarInfo] = {}
        links_by_name: ta.Dict[str, tarfile.TarInfo] = {}

        for name, info in self._entries_by_name().items():
            if info.type in tarfile.REGULAR_TYPES:
                files_by_name[name] = info
            elif info.type in (tarfile.LNKTYPE, tarfile.GNUTYPE_LONGLINK):
                links_by_name[name] = info
            else:
                non_files_by_name[name] = info

        return self._CategorizedEntries(
            files_by_name=files_by_name,
            non_files_by_name=non_files_by_name,
            links_by_name=links_by_name,
        )

    #

    @cached_nullary
    def _non_files_sorted_by_name(self) -> ta.Sequence[tarfile.TarInfo]:
        return sorted(
            self._categorized_entries().non_files_by_name.values(),
            key=lambda info: info.name,
        )

    @cached_nullary
    def _files_descending_by_size(self) -> ta.Sequence[tarfile.TarInfo]:
        return sorted(
            self._categorized_entries().files_by_name.values(),
            key=lambda info: -check.isinstance(info.size, int),
        )

    #

    @cached_nullary
    def _output_files(self) -> ta.Sequence[ta.BinaryIO]:
        return [
            self._enter_context(open(output_file_path, 'wb'))
            for output_file_path in self._output_file_paths
        ]

    @cached_nullary
    def _output_tar_writers(self) -> ta.Sequence[OciDataTarWriter]:
        return [
            self._enter_context(
                OciDataTarWriter(
                    output_file,
                    compression=self._compression,
                ),
            )
            for output_file in self._output_files()
        ]

    #

    def _write_entry(
            self,
            info: tarfile.TarInfo,
            output_file_idx: int,
    ) -> None:
        check.not_in(info.name, self._output_file_indexes_by_name)

        writer = self._output_tar_writers()[output_file_idx]

        if info.type in tarfile.REGULAR_TYPES:
            with check.not_none(self._input_tar_file().extractfile(info)) as f:
                writer.add_file(info, f)  # type: ignore

        else:
            writer.add_file(info)

        self._output_file_indexes_by_name[info.name] = output_file_idx

    @cached_nullary
    def _write_non_files(self) -> None:
        for non_file in self._non_files_sorted_by_name():
            self._write_entry(non_file, 0)

    @cached_nullary
    def _write_files(self) -> None:
        writers = self._output_tar_writers()

        bins = [
            (writer.info().compressed_sz, i)
            for i, writer in enumerate(writers)
        ]

        heapq.heapify(bins)

        for file in self._files_descending_by_size():
            _, bin_index = heapq.heappop(bins)

            writer = writers[bin_index]

            self._write_entry(file, bin_index)

            bin_size = writer.info().compressed_sz

            heapq.heappush(bins, (bin_size, bin_index))

    @cached_nullary
    def _write_links(self) -> None:
        for link in self._categorized_entries().links_by_name.values():
            link_name = check.non_empty_str(link.linkname)

            output_file_idx = self._output_file_indexes_by_name[link_name]

            self._write_entry(link, output_file_idx)

    @cached_nullary
    def write(self) -> ta.Mapping[str, WrittenOciDataTarFileInfo]:
        writers = self._output_tar_writers()

        self._write_non_files()
        self._write_files()
        self._write_links()

        for output_tar_writer in writers:
            output_tar_writer.tar_file().close()

        return {
            output_file_path: output_tar_writer.info()
            for output_file_path, output_tar_writer in zip(self._output_file_paths, writers)
        }


########################################
# ../../../omlish/formats/yaml/goyaml/ast.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


@dc.dataclass()
class UnexpectedNodeTypeYamlError(YamlError):
    actual: 'YamlNodeType'
    expected: 'YamlNodeType'
    token: YamlToken

    @property
    def message(self) -> str:
        return f'unexpected node type: expected {self.expected.name}, got {self.actual.name}, at {self.token.position}'


##


class YamlAstErrors:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    INVALID_TOKEN_TYPE = yaml_error('invalid token type')
    INVALID_ANCHOR_NAME = yaml_error('invalid anchor name')
    INVALID_ALIAS_NAME = yaml_error('invalid alias name')


class YamlNodeType(enum.Enum):
    # UNKNOWN type identifier for default
    UNKNOWN = enum.auto()
    # DOCUMENT type identifier for document node
    DOCUMENT = enum.auto()
    # NULL type identifier for null node
    NULL = enum.auto()
    # BOOL type identifier for boolean node
    BOOL = enum.auto()
    # INTEGER type identifier for integer node
    INTEGER = enum.auto()
    # FLOAT type identifier for float node
    FLOAT = enum.auto()
    # INFINITY type identifier for infinity node
    INFINITY = enum.auto()
    # NAN type identifier for nan node
    NAN = enum.auto()
    # STRING type identifier for string node
    STRING = enum.auto()
    # MERGE_KEY type identifier for merge key node
    MERGE_KEY = enum.auto()
    # LITERAL type identifier for literal node
    LITERAL = enum.auto()
    # MAPPING type identifier for mapping node
    MAPPING = enum.auto()
    # MAPPING_KEY type identifier for mapping key node
    MAPPING_KEY = enum.auto()
    # MAPPING_VALUE type identifier for mapping value node
    MAPPING_VALUE = enum.auto()
    # SEQUENCE type identifier for sequence node
    SEQUENCE = enum.auto()
    # SEQUENCE_ENTRY type identifier for sequence entry node
    SEQUENCE_ENTRY = enum.auto()
    # ANCHOR type identifier for anchor node
    ANCHOR = enum.auto()
    # ALIAS type identifier for alias node
    ALIAS = enum.auto()
    # DIRECTIVE type identifier for directive node
    DIRECTIVE = enum.auto()
    # TAG type identifier for tag node
    TAG = enum.auto()
    # COMMENT type identifier for comment node
    COMMENT = enum.auto()
    # COMMENT_GROUP type identifier for comment group node
    COMMENT_GROUP = enum.auto()


# String node type identifier to YAML Structure name based on https://yaml.org/spec/1.2/spec.html
YAML_NODE_TYPE_YAML_NAMES: ta.Mapping[YamlNodeType, str] = {
    YamlNodeType.UNKNOWN: 'unknown',
    YamlNodeType.DOCUMENT: 'document',
    YamlNodeType.NULL: 'null',
    YamlNodeType.BOOL: 'boolean',
    YamlNodeType.INTEGER: 'int',
    YamlNodeType.FLOAT: 'float',
    YamlNodeType.INFINITY: 'inf',
    YamlNodeType.NAN: 'nan',
    YamlNodeType.STRING: 'string',
    YamlNodeType.MERGE_KEY: 'merge key',
    YamlNodeType.LITERAL: 'scalar',
    YamlNodeType.MAPPING: 'mapping',
    YamlNodeType.MAPPING_KEY: 'key',
    YamlNodeType.MAPPING_VALUE: 'value',
    YamlNodeType.SEQUENCE: 'sequence',
    YamlNodeType.SEQUENCE_ENTRY: 'value',
    YamlNodeType.ANCHOR: 'anchor',
    YamlNodeType.ALIAS: 'alias',
    YamlNodeType.DIRECTIVE: 'directive',
    YamlNodeType.TAG: 'tag',
    YamlNodeType.COMMENT: 'comment',
    YamlNodeType.COMMENT_GROUP: 'comment',
}


##


# Node type of node
class YamlNode(Abstract):
    # io.Reader

    def __str__(self) -> ta.NoReturn:
        raise TypeError

    @abc.abstractmethod
    def string(self) -> str:
        # FIXME: migrate off - ensure all sprintfy things explicitly call .string()
        raise NotImplementedError

    # get_token returns token instance
    @abc.abstractmethod
    def get_token(self) -> ta.Optional[YamlToken]:
        raise NotImplementedError

    # type returns type of node
    @abc.abstractmethod
    def type(self) -> YamlNodeType:
        raise NotImplementedError

    # add_column add column number to child nodes recursively
    @abc.abstractmethod
    def add_column(self, column: int) -> None:
        raise NotImplementedError

    # set_comment set comment token to node
    @abc.abstractmethod
    def set_comment(self, node: ta.Optional['CommentGroupYamlNode']) -> ta.Optional[YamlError]:
        raise NotImplementedError

    # comment returns comment token instance
    @abc.abstractmethod
    def get_comment(self) -> ta.Optional['CommentGroupYamlNode']:
        raise NotImplementedError

    # get_path returns YAMLPath for the current node
    @abc.abstractmethod
    def get_path(self) -> str:
        raise NotImplementedError

    # set_path set YAMLPath for the current node
    @abc.abstractmethod
    def set_path(self, path: str) -> None:
        raise NotImplementedError

    # marshal_yaml
    @abc.abstractmethod
    def marshal_yaml(self) -> YamlErrorOr[str]:
        raise NotImplementedError

    # already read length
    @abc.abstractmethod
    def read_len(self) -> int:
        raise NotImplementedError

    # append read length
    @abc.abstractmethod
    def append_read_len(self, n: int) -> None:
        raise NotImplementedError

    # clean read length
    @abc.abstractmethod
    def clear_len(self) -> None:
        raise NotImplementedError


# MapKeyNode type for map key node
class MapKeyYamlNode(YamlNode, Abstract):
    @abc.abstractmethod
    def is_merge_key(self) -> bool:
        raise NotImplementedError

    # String node to text without comment
    @abc.abstractmethod
    def string_without_comment(self) -> str:
        raise NotImplementedError


# ScalarNode type for scalar node
class ScalarYamlNode(MapKeyYamlNode, Abstract):
    @abc.abstractmethod
    def get_value(self) -> ta.Any:
        raise NotImplementedError


##


@dc.dataclass()
class BaseYamlNode(YamlNode, Abstract):
    path: str = ''
    comment: ta.Optional['CommentGroupYamlNode'] = None
    cur_read: int = 0

    def read_len(self) -> int:
        return self.cur_read

    def clear_len(self) -> None:
        self.cur_read = 0

    def append_read_len(self, l: int) -> None:
        self.cur_read += l

    # get_path returns YAMLPath for the current node.
    @ta.final
    def get_path(self: ta.Optional['BaseYamlNode']) -> str:
        if self is None:
            return ''
        return self.path

    # set_path set YAMLPath for the current node.
    @ta.final
    def set_path(self: ta.Optional['BaseYamlNode'], path: str) -> None:
        if self is None:
            return
        self.path = path

    # get_comment returns comment token instance
    def get_comment(self) -> ta.Optional['CommentGroupYamlNode']:
        return self.comment

    # set_comment set comment token
    def set_comment(self, node: ta.Optional['CommentGroupYamlNode']) -> ta.Optional[YamlError]:
        self.comment = node
        return None


def yaml_add_comment_string(base: str, node: 'CommentGroupYamlNode') -> str:
    return f'{base} {node.string()}'


##


def yaml_read_node(p: str, node: YamlNode) -> YamlErrorOr[int]:
    s = node.string()
    read_len = node.read_len()
    remain = len(s) - read_len
    if remain == 0:
        node.clear_len()
        return EofYamlError()

    size = min(remain, len(p))
    for idx, b in enumerate(s[read_len:read_len + size]):
        p[idx] = b  # type: ignore[index]  # FIXME: lol

    node.append_read_len(size)
    return size


def yaml_check_line_break(t: YamlToken) -> bool:
    if t.prev is not None:
        lbc = '\n'
        prev = t.prev
        adjustment = 0
        # if the previous type is sequence entry use the previous type for that
        if prev.type == YamlTokenType.SEQUENCE_ENTRY:
            # as well as switching to previous type count any new lines in origin to account for:
            # -
            #   b: c
            adjustment = t.origin.rstrip(lbc).count(lbc)
            if prev.prev is not None:
                prev = prev.prev

        line_diff = t.position.line - prev.position.line - 1
        if line_diff > 0:
            if prev.type == YamlTokenType.STRING:
                # Remove any line breaks included in multiline string
                adjustment += prev.origin.strip().rstrip(lbc).count(lbc)

            # Due to the way that comment parsing works its assumed that when a null value does not have new line in
            # origin it was squashed therefore difference is ignored.
            # foo:
            #  bar:
            #  # comment
            #  baz: 1
            # becomes
            # foo:
            #  bar: null # comment
            #
            #  baz: 1
            if prev.type in (YamlTokenType.NULL, YamlTokenType.IMPLICIT_NULL):
                return prev.origin.count(lbc) > 0

            if line_diff - adjustment > 0:
                return True

    return False


##


class YamlAsts:
    # Null create node for null value
    @classmethod
    def null(cls, tk: YamlToken) -> 'NullYamlNode':
        return NullYamlNode(
            token=tk,
        )

    _BOOL_TRUE_STRS: ta.ClassVar[ta.AbstractSet[str]] = {'1', 't', 'T', 'true', 'TRUE', 'True'}
    _BOOL_FALSE_STRS: ta.ClassVar[ta.AbstractSet[str]] = {'0', 'f', 'F', 'false', 'FALSE', 'False'}

    @classmethod
    def _parse_bool(cls, s: str) -> bool:
        if s in cls._BOOL_TRUE_STRS:
            return True
        if s in cls._BOOL_FALSE_STRS:
            return False
        raise ValueError(f'"{s}" is not a valid boolean string')

    # bool_ create node for boolean value
    @classmethod
    def bool_(cls, tk: YamlToken) -> 'BoolYamlNode':
        b = cls._parse_bool(tk.value)
        return BoolYamlNode(
            token=tk,
            value=b,
        )

    # integer create node for integer value
    @classmethod
    def integer(cls, tk: YamlToken) -> 'IntegerYamlNode':
        v: ta.Any = None
        if (num := yaml_to_number(tk.value)) is not None:
            v = num.value

        return IntegerYamlNode(
            token=tk,
            value=v,
        )

    # float_ create node for float value
    @classmethod
    def float_(cls, tk: YamlToken) -> 'FloatYamlNode':
        v: float = 0.
        if (num := yaml_to_number(tk.value)) is not None and num.type == YamlNumberType.FLOAT:
            if isinstance(num.value, float):
                v = num.value

        return FloatYamlNode(
            token=tk,
            value=v,
        )

    # infinity create node for .inf or -.inf value
    @classmethod
    def infinity(cls, tk: YamlToken) -> 'InfinityYamlNode':
        if tk.value in ('.inf', '.Inf', '.INF'):
            value = float('inf')
        elif tk.value in ('-.inf', '-.Inf', '-.INF'):
            value = float('-inf')
        node = InfinityYamlNode(
            token=tk,
            value=value,
        )
        return node

    # nan create node for .nan value
    @classmethod
    def nan(cls, tk: YamlToken) -> 'NanYamlNode':
        return NanYamlNode(
            token=tk,
        )

    # string create node for string value
    @classmethod
    def string(cls, tk: YamlToken) -> 'StringYamlNode':
        return StringYamlNode(
            token=tk,
            value=tk.value,
        )

    # comment create node for comment
    @classmethod
    def comment(cls, tk: ta.Optional[YamlToken]) -> 'CommentYamlNode':
        return CommentYamlNode(
            token=tk,
        )

    @classmethod
    def comment_group(cls, comments: ta.Iterable[ta.Optional[YamlToken]]) -> 'CommentGroupYamlNode':
        nodes: ta.List[CommentYamlNode] = []
        for c in comments:
            nodes.append(cls.comment(c))

        return CommentGroupYamlNode(
            comments=nodes,
        )

    # merge_key create node for merge key ( << )
    @classmethod
    def merge_key(cls, tk: YamlToken) -> 'MergeKeyYamlNode':
        return MergeKeyYamlNode(
            token=tk,
        )

    # mapping create node for map
    @classmethod
    def mapping(cls, tk: YamlToken, is_flow_style: bool, *values: 'MappingValueYamlNode') -> 'MappingYamlNode':
        node = MappingYamlNode(
            start=tk,
            is_flow_style=is_flow_style,
            values=[],
        )
        node.values.extend(values)
        return node

    # mapping_value create node for mapping value
    @classmethod
    def mapping_value(cls, tk: YamlToken, key: 'MapKeyYamlNode', value: YamlNode) -> 'MappingValueYamlNode':
        return MappingValueYamlNode(
            start=tk,
            key=key,
            value=value,
        )

    # mapping_key create node for map key ( '?' ).
    @classmethod
    def mapping_key(cls, tk: YamlToken) -> 'MappingKeyYamlNode':
        return MappingKeyYamlNode(
            start=tk,
        )

    # sequence create node for sequence
    @classmethod
    def sequence(cls, tk: YamlToken, is_flow_style: bool) -> 'SequenceYamlNode':
        return SequenceYamlNode(
            start=tk,
            is_flow_style=is_flow_style,
            values=[],
        )

    @classmethod
    def anchor(cls, tk: YamlToken) -> 'AnchorYamlNode':
        return AnchorYamlNode(
            start=tk,
        )

    @classmethod
    def alias(cls, tk: YamlToken) -> 'AliasYamlNode':
        return AliasYamlNode(
            start=tk,
        )

    @classmethod
    def document(cls, tk: ta.Optional[YamlToken], body: ta.Optional[YamlNode]) -> 'DocumentYamlNode':
        return DocumentYamlNode(
            start=tk,
            body=body,
        )

    @classmethod
    def directive(cls, tk: YamlToken) -> 'DirectiveYamlNode':
        return DirectiveYamlNode(
            start=tk,
        )

    @classmethod
    def literal(cls, tk: YamlToken) -> 'LiteralYamlNode':
        return LiteralYamlNode(
            start=tk,
        )

    @classmethod
    def tag(cls, tk: YamlToken) -> 'TagYamlNode':
        return TagYamlNode(
            start=tk,
        )


##


# File contains all documents in YAML file
@dc.dataclass()
class YamlFile:
    name: str = ''
    docs: ta.List['DocumentYamlNode'] = dc.field(default_factory=list)

    # read implements (io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        for doc in self.docs:
            n = doc.read(p)
            if isinstance(n, EofYamlError):
                continue
            return n
        return EofYamlError()

    # string all documents to text
    def string(self) -> str:
        docs: ta.List[str] = []
        for doc in self.docs:
            docs.append(doc.string())
        if len(docs) > 0:
            return '\n'.join(docs) + '\n'
        else:
            return ''


##


# DocumentNode type of Document
@dc.dataclass()
class DocumentYamlNode(BaseYamlNode):
    start: ta.Optional[YamlToken] = dc.field(default_factory=dataclass_field_required('start'))  # position of DocumentHeader ( `---` )  # noqa
    end: ta.Optional[YamlToken] = None  # position of DocumentEnd ( `...` )
    body: ta.Optional[YamlNode] = dc.field(default_factory=dataclass_field_required('body'))

    # read implements (io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns DocumentNodeType
    def type(self) -> YamlNodeType:
        return YamlNodeType.DOCUMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        return check.not_none(self.body).get_token()

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        if self.body is not None:
            self.body.add_column(col)

    # string document to text
    def string(self) -> str:
        doc: ta.List[str] = []
        if self.start is not None:
            doc.append(self.start.value)
        if self.body is not None:
            doc.append(self.body.string())
        if self.end is not None:
            doc.append(self.end.value)
        return '\n'.join(doc)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# NullNode type of null node
@dc.dataclass()
class NullYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns NullType
    def type(self) -> YamlNodeType:
        return YamlNodeType.NULL

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns nil value
    def get_value(self) -> ta.Any:
        return None

    # String returns `null` text
    def string(self) -> str:
        if self.token.type == YamlTokenType.IMPLICIT_NULL:
            if self.comment is not None:
                return self.comment.string()
            return ''
        if self.comment is not None:
            return yaml_add_comment_string('null', self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return 'null'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# IntegerNode type of integer node
@dc.dataclass()
class IntegerYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: ta.Any = dc.field(default_factory=dataclass_field_required('value'))  # int64 or uint64 value

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns IntegerType
    def type(self) -> YamlNodeType:
        return YamlNodeType.INTEGER

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns int64 value
    def get_value(self) -> ta.Any:
        return self.value

    # String int64 to text
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# FloatNode type of float node
@dc.dataclass()
class FloatYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    precision: int = 0
    value: float = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns FloatType
    def type(self) -> YamlNodeType:
        return YamlNodeType.FLOAT

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns float64 value
    def get_value(self) -> ta.Any:
        return self.value

    # String float64 to text
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


def _yaml_go_is_print(char_ord):
    """
    Approximates Go's unicode.IsPrint logic. A rune is printable if it is a letter, mark, number, punctuation, symbol,
    or ASCII space. (Corresponds to Unicode categories L, M, N, P, S, plus U+0020 SPACE).
    """

    if char_ord == 0x20:  # ASCII space
        return True
    # Check if the character is in categories L, M, N, P, S (Graphic characters)
    category = unicodedata.category(chr(char_ord))
    if category.startswith(('L', 'M', 'N', 'P', 'S')):
        return True
    return False


def _yaml_strconv_quote(s: str) -> str:
    """
    Produces a double-quoted string literal with Go-style escapes, similar to Go's strconv.Quote.
    """

    res = ['"']
    for char_val in s:
        char_ord = ord(char_val)

        if char_val == '"':
            res.append('\\"')
        elif char_val == '\\':
            res.append('\\\\')
        elif char_val == '\a':
            res.append('\\a')
        elif char_val == '\b':
            res.append('\\b')
        elif char_val == '\f':
            res.append('\\f')
        elif char_val == '\n':
            res.append('\\n')
        elif char_val == '\r':
            res.append('\\r')
        elif char_val == '\t':
            res.append('\\t')
        elif char_val == '\v':
            res.append('\\v')
        elif char_ord < 0x20 or char_ord == 0x7F:  # C0 controls and DEL
            res.append(f'\\x{char_ord:02x}')
        elif 0x20 <= char_ord < 0x7F:  # Printable ASCII (already handled \, ")
            res.append(char_val)
        # Unicode characters (char_ord >= 0x80) and C1 controls (0x80-0x9F)
        elif _yaml_go_is_print(char_ord):
            res.append(char_val)
        elif char_ord <= 0xFFFF:
            res.append(f'\\u{char_ord:04x}')
        else:
            res.append(f'\\U{char_ord:08x}')

    res.append('"')
    return ''.join(res)


##


# StringNode type of string node
@dc.dataclass()
class StringYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: str = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns StringType
    def type(self) -> YamlNodeType:
        return YamlNodeType.STRING

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns string value
    def get_value(self) -> ta.Any:
        return self.value

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False

    # string string value to text with quote or literal header if required
    def string(self) -> str:
        if self.token.type == YamlTokenType.SINGLE_QUOTE:
            quoted = _yaml_escape_single_quote(self.value)
            if self.comment is not None:
                return yaml_add_comment_string(quoted, self.comment)
            return quoted
        elif self.token.type == YamlTokenType.DOUBLE_QUOTE:
            quoted = _yaml_strconv_quote(self.value)
            if self.comment is not None:
                return yaml_add_comment_string(quoted, self.comment)
            return quoted

        lbc = yaml_detect_line_break_char(self.value)
        if lbc in self.value:
            # This block assumes that the line breaks in this inside scalar content and the Outside scalar content are
            # the same. It works mostly, but inconsistencies occur if line break characters are mixed.
            header = yaml_literal_block_header(self.value)
            space = ' ' * (self.token.position.column - 1)
            indent = ' ' * self.token.position.indent_num
            values: ta.List[str] = []
            for v in self.value.split(lbc):
                values.append(f'{space}{indent}{v}')
            block = lbc.join(values).rstrip(f'{lbc}{indent}{space}').rstrip(f'{indent}{space}')
            return f'{header}{lbc}{block}'
        elif len(self.value) > 0 and (self.value[0] == '{' or self.value[0] == '['):
            return f"'{self.value}'"
        if self.comment is not None:
            return yaml_add_comment_string(self.value, self.comment)
        return self.value

    def string_without_comment(self) -> str:
        if self.token.type == YamlTokenType.SINGLE_QUOTE:
            quoted = f"'{self.value}'"
            return quoted
        elif self.token.type == YamlTokenType.DOUBLE_QUOTE:
            quoted = _yaml_strconv_quote(self.value)
            return quoted

        lbc = yaml_detect_line_break_char(self.value)
        if lbc in self.value:
            # This block assumes that the line breaks in this inside scalar content and the Outside scalar content are
            # the same. It works mostly, but inconsistencies occur if line break characters are mixed.
            header = yaml_literal_block_header(self.value)
            space = ' ' * (self.token.position.column - 1)
            indent = ' ' * self.token.position.indent_num
            values: ta.List[str] = []
            for v in self.value.split(lbc):
                values.append(f'{space}{indent}{v}')
            block = lbc.join(values).rstrip(f'{lbc}{indent}{space}').rstrip(f'  {space}')
            return f'{header}{lbc}{block}'
        elif len(self.value) > 0 and (self.value[0] == '{' or self.value[0] == '['):
            return f"'{self.value}'"
        return self.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


# escape_single_quote escapes s to a single quoted scalar.
# https://yaml.org/spec/1.2.2/#732-single-quoted-style
def _yaml_escape_single_quote(s: str) -> str:
    sb = io.StringIO()
    # growLen = len(s) + # s includes also one ' from the doubled pair
    #     2 + # opening and closing '
    #     strings.Count(s, "'") # ' added by ReplaceAll
    # sb.Grow(growLen)
    sb.write("'")
    sb.write(s.replace("'", "''"))
    sb.write("'")
    return sb.getvalue()


##


# LiteralNode type of literal node
@dc.dataclass()
class LiteralYamlNode(ScalarYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional['StringYamlNode'] = None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns LiteralType
    def type(self) -> YamlNodeType:
        return YamlNodeType.LITERAL

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # get_value returns string value
    def get_value(self) -> ta.Any:
        return self.string()

    # String literal to text
    def string(self) -> str:
        origin = check.not_none(check.not_none(self.value).get_token()).origin
        lit = origin.rstrip(' ').rstrip('\n')
        if self.comment is not None:
            return f'{self.start.value} {self.comment.string()}\n{lit}'
        return f'{self.start.value}\n{lit}'

    def string_without_comment(self) -> str:
        return self.string()

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# MergeKeyNode type of merge key node
@dc.dataclass()
class MergeKeyYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns MergeKeyType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MERGE_KEY

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # get_value returns '<<' value
    def get_value(self) -> ta.Any:
        return self.token.value

    # String returns '<<' value
    def string(self) -> str:
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return str(self)

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return True


##


# BoolNode type of boolean node
@dc.dataclass()
class BoolYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: bool = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns BoolType
    def type(self) -> YamlNodeType:
        return YamlNodeType.BOOL

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns boolean value
    def get_value(self) -> ta.Any:
        return self.value

    # String boolean to text
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# InfinityNode type of infinity node
@dc.dataclass()
class InfinityYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: float = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns InfinityType
    def type(self) -> YamlNodeType:
        return YamlNodeType.INFINITY

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns math.Inf(0) or math.Inf(-1)
    def get_value(self) -> ta.Any:
        return self.value

    # String infinity to text
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# NanNode type of nan node
@dc.dataclass()
class NanYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns NanType
    def type(self) -> YamlNodeType:
        return YamlNodeType.NAN

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns math.NaN()
    def get_value(self) -> ta.Any:
        return float('nan')

    # String returns .nan
    def string(self) -> str:
        if self.comment is not None:
            return yaml_add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# MapNode interface of MappingValueNode / MappingNode
class MapYamlNode(Abstract):
    @abc.abstractmethod
    def map_range(self) -> 'MapYamlNodeIter':
        raise NotImplementedError


YAML_START_RANGE_INDEX = -1


# MapNodeIter is an iterator for ranging over a MapNode
@dc.dataclass()
class MapYamlNodeIter:
    values: ta.List['MappingValueYamlNode']
    idx: int

    # next advances the map iterator and reports whether there is another entry.
    # It returns false when the iterator is exhausted.
    def next(self) -> bool:
        self.idx += 1
        nxt = self.idx < len(self.values)
        return nxt

    # key returns the key of the iterator's current map node entry.
    def key(self) -> MapKeyYamlNode:
        return self.values[self.idx].key

    # value returns the value of the iterator's current map node entry.
    def value(self) -> YamlNode:
        return self.values[self.idx].value

    # key_value returns the MappingValueNode of the iterator's current map node entry.
    def key_value(self) -> 'MappingValueYamlNode':
        return self.values[self.idx]


#


# MappingNode type of mapping node
@dc.dataclass()
class MappingYamlNode(MapYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    end: ta.Optional[YamlToken] = None
    is_flow_style: bool = dc.field(default_factory=dataclass_field_required('is_flow_style'))
    values: ta.List['MappingValueYamlNode'] = dc.field(default_factory=dataclass_field_required('values'))
    foot_comment: ta.Optional['CommentGroupYamlNode'] = None

    def start_pos(self) -> YamlPosition:
        if len(self.values) == 0:
            return self.start.position
        return check.not_none(self.values[0].key.get_token()).position

    # merge merge key/value of map.
    def merge(self, target: 'MappingYamlNode') -> None:
        key_to_map_value_map: ta.Dict[str, MappingValueYamlNode] = {}
        for value in self.values:
            key = value.key.string()
            key_to_map_value_map[key] = value
        column = self.start_pos().column - target.start_pos().column
        target.add_column(column)
        for value in target.values:
            map_value = key_to_map_value_map.get(value.key.string())
            if map_value is not None:
                map_value.value = value.value
            else:
                self.values.append(value)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        for value in self.values:
            value.set_is_flow_style(is_flow)

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns MappingType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MAPPING

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        YamlToken.add_column(self.end, col)
        for value in self.values:
            value.add_column(col)

    def flow_style_string(self, comment_mode: bool) -> str:
        values: ta.List[str] = []
        for value in self.values:
            values.append(value.string().lstrip(' '))
        map_text = f'{{{", ".join(values)}}}'
        if comment_mode and self.comment is not None:
            return yaml_add_comment_string(map_text, self.comment)
        return map_text

    def block_style_string(self, comment_mode: bool) -> str:
        values: ta.List[str] = []
        for value0 in self.values:
            values.append(value0.string())
        map_text = '\n'.join(values)
        if comment_mode and self.comment is not None:
            value1 = values[0]
            space_num = 0
            for i in range(len(value1)):
                if value1[i] != ' ':
                    break
                space_num += 1
            comment = self.comment.string_with_space(space_num)
            return f'{comment}\n{map_text}'
        return map_text

    # String mapping values to text
    def string(self) -> str:
        if len(self.values) == 0:
            if self.comment is not None:
                return yaml_add_comment_string('{}', self.comment)
            return '{}'

        comment_mode = True
        if self.is_flow_style or len(self.values) == 0:
            return self.flow_style_string(comment_mode)

        return self.block_style_string(comment_mode)

    # map_range implements MapNode protocol
    def map_range(self) -> MapYamlNodeIter:
        return MapYamlNodeIter(
            idx=YAML_START_RANGE_INDEX,
            values=self.values,
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# MappingKeyNode type of tag node
@dc.dataclass()
class MappingKeyYamlNode(MapKeyYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional[YamlNode] = None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns MappingKeyType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MAPPING_KEY

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # String tag to text
    def string(self) -> str:
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return f'{self.start.value} {check.not_none(self.value).string()}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyYamlNode):
            return False
        return key.is_merge_key()


##


# MappingValueNode type of mapping value
@dc.dataclass()
class MappingValueYamlNode(MapYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))  # delimiter token ':'.
    collect_entry: ta.Optional[YamlToken] = None  # collect entry token ','.
    key: MapKeyYamlNode = dc.field(default_factory=dataclass_field_required('key'))
    value: YamlNode = dc.field(default_factory=dataclass_field_required('value'))
    foot_comment: ta.Optional['CommentGroupYamlNode'] = None
    is_flow_style: bool = False

    # Replace replace value node.
    def replace(self, value: YamlNode) -> ta.Optional[YamlError]:
        column = check.not_none(self.value.get_token()).position.column - check.not_none(value.get_token()).position.column  # noqa
        value.add_column(column)
        self.value = value
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns MappingValueType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MAPPING_VALUE

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.key is not None:
            self.key.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        if isinstance(self.value, MappingYamlNode):
            self.value.set_is_flow_style(is_flow)
        elif isinstance(self.value, MappingValueYamlNode):
            self.value.set_is_flow_style(is_flow)
        elif isinstance(self.value, SequenceYamlNode):
            self.value.set_is_flow_style(is_flow)

    # String mapping value to text
    def string(self) -> str:
        text: str
        if self.comment is not None:
            text = f'{self.comment.string_with_space(check.not_none(self.key.get_token()).position.column - 1)}\n{self.to_string()}'  # noqa
        else:
            text = self.to_string()

        if self.foot_comment is not None:
            text += f'\n{self.foot_comment.string_with_space(check.not_none(self.key.get_token()).position.column - 1)}'

        return text

    def to_string(self) -> str:
        space = ' ' * (check.not_none(self.key.get_token()).position.column - 1)
        if yaml_check_line_break(check.not_none(self.key.get_token())):
            space = f'\n{space}'

        key_indent_level = check.not_none(self.key.get_token()).position.indent_level
        value_indent_level = check.not_none(self.value.get_token()).position.indent_level
        key_comment = self.key.get_comment()

        if isinstance(self.value, ScalarYamlNode):
            value = self.value.string()
            if value == '':
                # implicit null value.
                return f'{space}{self.key.string()}:'
            return f'{space}{self.key.string()}: {value}'

        elif key_indent_level < value_indent_level and not self.is_flow_style:
            value_str = self.value.string()
            # For flow-style values indented on the next line, we need to add the proper indentation
            if isinstance(self.value, MappingYamlNode) and self.value.is_flow_style:
                value_indent = ' ' * (self.value.get_token().position.column - 1)
                value_str = value_indent + value_str
            elif isinstance(self.value, SequenceYamlNode) and self.value.is_flow_style:
                value_indent = ' ' * (self.value.get_token().position.column - 1)
                value_str = value_indent + value_str
            if key_comment is not None:
                return f'{space}{self.key.string_without_comment()}: {key_comment.string()}\n{value_str}'

            return f'{space}{self.key.string()}:\n{value_str}'

        elif isinstance(self.value, MappingYamlNode) and (self.value.is_flow_style or len(self.value.values) == 0):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, SequenceYamlNode) and (self.value.is_flow_style or len(self.value.values) == 0):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, AnchorYamlNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, AliasYamlNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, TagYamlNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        if key_comment is not None:
            return f'{space}{self.key.string_without_comment()}: {key_comment.string()}\n{self.value.string()}'

        if isinstance(self.value, MappingYamlNode) and self.value.comment is not None:
            return f'{space}{self.key.string()}: {self.value.string().lstrip(" ")}'

        return f'{space}{self.key.string()}:\n{self.value.string()}'

    # map_range implements MapNode protocol
    def map_range(self) -> MapYamlNodeIter:
        return MapYamlNodeIter(
            idx=YAML_START_RANGE_INDEX,
            values=[self],
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# ArrayNode interface of SequenceNode
class ArrayYamlNode(YamlNode, Abstract):
    @abc.abstractmethod
    def array_range(self) -> ta.Optional['ArrayYamlNodeIter']:
        raise NotImplementedError


# ArrayNodeIter is an iterator for ranging over a ArrayNode
@dc.dataclass()
class ArrayYamlNodeIter:
    values: ta.List[YamlNode]
    idx: int

    # next advances the array iterator and reports whether there is another entry.
    # It returns false when the iterator is exhausted.
    def next(self) -> bool:
        self.idx += 1
        nxt = self.idx < len(self.values)
        return nxt

    # Value returns the value of the iterator's current array entry.
    def value(self) -> YamlNode:
        return self.values[self.idx]

    # len returns length of array
    def len(self) -> int:
        return len(self.values)


##


# SequenceNode type of sequence node
@dc.dataclass()
class SequenceYamlNode(BaseYamlNode, ArrayYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    end: ta.Optional[YamlToken] = None
    is_flow_style: bool = dc.field(default_factory=dataclass_field_required('is_flow_style'))
    values: ta.List[ta.Optional[YamlNode]] = dc.field(default_factory=dataclass_field_required('values'))
    value_head_comments: ta.List[ta.Optional['CommentGroupYamlNode']] = dc.field(default_factory=list)
    entries: ta.List['SequenceEntryYamlNode'] = dc.field(default_factory=list)
    foot_comment: ta.Optional['CommentGroupYamlNode'] = None

    # replace replace value node.
    def replace(self, idx: int, value: YamlNode) -> ta.Optional[YamlError]:
        if len(self.values) <= idx:
            return yaml_error(f'invalid index for sequence: sequence length is {len(self.values):d}, but specified {idx:d} index')  # noqa

        column = check.not_none(check.not_none(self.values[idx]).get_token()).position.column - check.not_none(value.get_token()).position.column  # noqa
        value.add_column(column)
        self.values[idx] = value
        return None

    # merge merge sequence value.
    def merge(self, target: 'SequenceYamlNode') -> None:
        column = self.start.position.column - target.start.position.column
        target.add_column(column)
        self.values.extend(target.values)
        if len(target.value_head_comments) == 0:
            self.value_head_comments.extend([None] * len(target.values))
            return

        self.value_head_comments.extend(target.value_head_comments)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        for value in self.values:
            if isinstance(value, MappingYamlNode):
                value.set_is_flow_style(is_flow)
            elif isinstance(value, MappingValueYamlNode):
                value.set_is_flow_style(is_flow)
            elif isinstance(value, SequenceYamlNode):
                value.set_is_flow_style(is_flow)

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns SequenceType
    def type(self) -> YamlNodeType:
        return YamlNodeType.SEQUENCE

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        YamlToken.add_column(self.end, col)
        for value in self.values:
            check.not_none(value).add_column(col)

    def flow_style_string(self) -> str:
        values: ta.List[str] = []
        for value in self.values:
            values.append(check.not_none(value).string())

        seq_text = f'[{", ".join(values)}]'
        if self.comment is not None:
            return yaml_add_comment_string(seq_text, self.comment)

        return seq_text

    def block_style_string(self) -> str:
        space = ' ' * (self.start.position.column - 1)
        values: ta.List[str] = []
        if self.comment is not None:
            values.append(self.comment.string_with_space(self.start.position.column - 1))

        for idx, value in enumerate(self.values):
            if value is None:
                continue

            value_str = value.string()
            new_line_prefix = ''
            if value_str.startswith('\n'):
                value_str = value_str[1:]
                new_line_prefix = '\n'

            splitted_values = value_str.split('\n')
            trimmed_first_value = splitted_values[0].lstrip(' ')
            diff_length = len(splitted_values[0]) - len(trimmed_first_value)
            if (
                    (len(splitted_values) > 1 and value.type() == YamlNodeType.STRING) or
                    value.type() == YamlNodeType.LITERAL
            ):
                # If multi-line string, the space characters for indent have already been added, so delete them.
                prefix = space + '  '
                for i in range(1, len(splitted_values)):
                    splitted_values[i] = splitted_values[i].lstrip(prefix)

            new_values: ta.List[str] = [trimmed_first_value]
            for i in range(1, len(splitted_values)):
                if len(splitted_values[i]) <= diff_length:
                    # this line is \n or white space only
                    new_values.append('')
                    continue

                trimmed = splitted_values[i][diff_length:]
                new_values.append(f'{space}  {trimmed}')

            new_value = '\n'.join(new_values)
            if len(self.value_head_comments) == len(self.values) and self.value_head_comments[idx] is not None:
                values.append(
                    f'{new_line_prefix}'
                    f'{check.not_none(self.value_head_comments[idx]).string_with_space(self.start.position.column - 1)}',  # noqa
                )
                new_line_prefix = ''

            values.append(f'{new_line_prefix}{space}- {new_value}')

        if self.foot_comment is not None:
            values.append(self.foot_comment.string_with_space(self.start.position.column - 1))

        return '\n'.join(values)

    # String sequence to text
    def string(self) -> str:
        if self.is_flow_style or len(self.values) == 0:
            return self.flow_style_string()
        return self.block_style_string()

    # array_range implements ArrayNode protocol
    def array_range(self) -> ta.Optional[ArrayYamlNodeIter]:
        return ArrayYamlNodeIter(
            idx=YAML_START_RANGE_INDEX,
            values=ta.cast('ta.List[YamlNode]', self.values),
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# SequenceEntryNode is the sequence entry.
@dc.dataclass()
class SequenceEntryYamlNode(BaseYamlNode):
    head_comment: ta.Optional['CommentGroupYamlNode'] = dc.field(default_factory=dataclass_field_required('head_commend'))  # head comment.  # noqa
    line_comment: ta.Optional['CommentGroupYamlNode'] = None  # line comment e.g.) - # comment.
    start: ta.Optional[YamlToken] = dc.field(default_factory=dataclass_field_required('start'))  # entry token.
    value: YamlNode = dc.field(default_factory=dataclass_field_required('value'))  # value node.

    # String node to text
    def string(self) -> str:
        return ''  # TODO

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        return self.start

    # type returns type of node
    def type(self) -> YamlNodeType:
        return YamlNodeType.SEQUENCE_ENTRY

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)

    # set_comment set line comment.
    def set_comment(self, node: ta.Optional['CommentGroupYamlNode']) -> ta.Optional[YamlError]:
        self.line_comment = node
        return None

    # comment returns comment token instance
    def get_comment(self) -> ta.Optional['CommentGroupYamlNode']:
        return self.line_comment

    # marshal_yaml
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)


# sequence_entry creates SequenceEntryNode instance.
def yaml_sequence_entry(
        start: ta.Optional[YamlToken],
        value: YamlNode,
        head_comment: ta.Optional['CommentGroupYamlNode'],
) -> SequenceEntryYamlNode:
    return SequenceEntryYamlNode(
        head_comment=head_comment,
        start=start,
        value=value,
    )


# SequenceMergeValue creates SequenceMergeValueNode instance.
def yaml_sequence_merge_value(*values: MapYamlNode) -> 'SequenceMergeValueYamlNode':
    return SequenceMergeValueYamlNode(
        values=list(values),
    )


##


# SequenceMergeValueNode is used to convert the Sequence node specified for the merge key into a MapNode format.
@dc.dataclass()
class SequenceMergeValueYamlNode(MapYamlNode):
    values: ta.List[MapYamlNode] = dc.field(default_factory=dataclass_field_required('values'))

    # map_range returns MapNodeIter instance.
    def map_range(self) -> MapYamlNodeIter:
        ret = MapYamlNodeIter(values=[], idx=YAML_START_RANGE_INDEX)
        for value in self.values:
            it = value.map_range()
            ret.values.extend(it.values)
        return ret


##


# AnchorNode type of anchor node
@dc.dataclass()
class AnchorYamlNode(ScalarYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    name: ta.Optional[YamlNode] = None
    value: ta.Optional[YamlNode] = None

    def string_without_comment(self) -> str:
        return check.not_none(self.value).string()

    def set_name(self, name: str) -> ta.Optional[YamlError]:
        if self.name is None:
            return YamlAstErrors.INVALID_ANCHOR_NAME
        s = self.name
        if not isinstance(s, StringYamlNode):
            return YamlAstErrors.INVALID_ANCHOR_NAME
        s.value = name
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns AnchorType
    def type(self) -> YamlNodeType:
        return YamlNodeType.ANCHOR

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    def get_value(self) -> ta.Any:
        return check.not_none(check.not_none(self.value).get_token()).value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.name is not None:
            self.name.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # String anchor to text
    def string(self) -> str:
        anchor = '&' + check.not_none(self.name).string()
        value = check.not_none(self.value).string()
        if isinstance(self.value, SequenceYamlNode) and not self.value.is_flow_style:
            return f'{anchor}\n{value}'
        elif isinstance(self.value, MappingYamlNode) and not self.value.is_flow_style:
            return f'{anchor}\n{value}'
        if value == '':
            # implicit null value.
            return anchor
        return f'{anchor} {value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyYamlNode):
            return False
        return key.is_merge_key()


##


# AliasNode type of alias node
@dc.dataclass()
class AliasYamlNode(ScalarYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional[YamlNode] = None

    def string_without_comment(self) -> str:
        return check.not_none(self.value).string()

    def set_name(self, name: str) -> ta.Optional[YamlError]:
        if self.value is None:
            return YamlAstErrors.INVALID_ALIAS_NAME
        if not isinstance(self.value, StringYamlNode):
            return YamlAstErrors.INVALID_ALIAS_NAME
        self.value.value = name
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns AliasType
    def type(self) -> YamlNodeType:
        return YamlNodeType.ALIAS

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    def get_value(self) -> ta.Any:
        return check.not_none(check.not_none(self.value).get_token()).value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # String alias to text
    def string(self) -> str:
        return f'*{check.not_none(self.value).string()}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# DirectiveNode type of directive node
@dc.dataclass()
class DirectiveYamlNode(BaseYamlNode):
    # Start is '%' token.
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    # Name is directive name e.g.) "YAML" or "TAG".
    name: ta.Optional[YamlNode] = None
    # Values is directive values e.g.) "1.2" or "!!" and "tag:clarkevans.com,2002:app/".
    values: ta.List[YamlNode] = dc.field(default_factory=list)

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns DirectiveType
    def type(self) -> YamlNodeType:
        return YamlNodeType.DIRECTIVE

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        if self.name is not None:
            self.name.add_column(col)
        for value in self.values:
            value.add_column(col)

    # String directive to text
    def string(self) -> str:
        values: ta.List[str] = []
        for val in self.values:
            values.append(val.string())
        return ' '.join(['%' + check.not_none(self.name).string(), *values])

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# TagNode type of tag node
@dc.dataclass()
class TagYamlNode(ScalarYamlNode, BaseYamlNode, ArrayYamlNode):
    directive: ta.Optional[DirectiveYamlNode] = None
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional[YamlNode] = None

    def get_value(self) -> ta.Any:
        if not isinstance(self.value, ScalarYamlNode):
            return None
        return self.value.get_value()

    def string_without_comment(self) -> str:
        return check.not_none(self.value).string()

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns TagType
    def type(self) -> YamlNodeType:
        return YamlNodeType.TAG

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # String tag to text
    def string(self) -> str:
        value = check.not_none(self.value).string()
        if isinstance(self.value, SequenceYamlNode) and not self.value.is_flow_style:
            return f'{self.start.value}\n{value}'
        elif isinstance(self.value, MappingYamlNode) and not self.value.is_flow_style:
            return f'{self.start.value}\n{value}'

        return f'{self.start.value} {value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyYamlNode):
            return False
        return key.is_merge_key()

    def array_range(self) -> ta.Optional[ArrayYamlNodeIter]:
        arr = self.value
        if not isinstance(arr, ArrayYamlNode):
            return None
        return arr.array_range()


##


# CommentNode type of comment node
@dc.dataclass()
class CommentYamlNode(BaseYamlNode):
    token: ta.Optional[YamlToken] = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns CommentType
    def type(self) -> YamlNodeType:
        return YamlNodeType.COMMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # String comment to text
    def string(self) -> str:
        return f'#{check.not_none(self.token).value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# CommentGroupNode type of comment node
@dc.dataclass()
class CommentGroupYamlNode(BaseYamlNode):
    comments: ta.List[CommentYamlNode] = dc.field(default_factory=dataclass_field_required('comments'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return yaml_read_node(p, self)

    # type returns CommentType
    def type(self) -> YamlNodeType:
        return YamlNodeType.COMMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        if len(self.comments) > 0:
            return self.comments[0].token
        return None

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        for comment in self.comments:
            comment.add_column(col)

    # String comment to text
    def string(self) -> str:
        values: ta.List[str] = []
        for comment in self.comments:
            values.append(comment.string())
        return '\n'.join(values)

    def string_with_space(self, col: int) -> str:
        values: ta.List[str] = []
        space = ' ' * col
        for comment in self.comments:
            spc = space
            if yaml_check_line_break(check.not_none(comment.token)):
                spc = f'\n{spc}'
            values.append(spc + comment.string())
        return '\n'.join(values)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# Visitor has Visit method that is invokded for each node encountered by walk.
# If the result visitor w is not nil, walk visits each of the children of node with the visitor w,
# followed by a call of w.visit(nil).
class YamlAstVisitor(Abstract):
    @abc.abstractmethod
    def visit(self, node: YamlNode) -> ta.Optional['YamlAstVisitor']:
        raise NotImplementedError


# walk traverses an AST in depth-first order: It starts by calling v.visit(node); node must not be nil.
# If the visitor w returned by v.visit(node) is not nil,
# walk is invoked recursively with visitor w for each of the non-nil children of node,
# followed by a call of w.visit(nil).
def yaml_ast_walk(v: YamlAstVisitor, node: YamlNode) -> None:
    if (v_ := v.visit(node)) is None:
        return
    v = v_

    n = node
    if isinstance(n, (CommentYamlNode, NullYamlNode)):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, IntegerYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, FloatYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, StringYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, MergeKeyYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, BoolYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, InfinityYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, NanYamlNode):
        yaml_ast_walk_comment(v, n)
    if isinstance(n, LiteralYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.value))
    if isinstance(n, DirectiveYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.name))
        for value0 in n.values:
            yaml_ast_walk(v, value0)
    if isinstance(n, TagYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.value))
    if isinstance(n, DocumentYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.body))
    if isinstance(n, MappingYamlNode):
        yaml_ast_walk_comment(v, n)
        for value1 in n.values:
            yaml_ast_walk(v, value1)
    if isinstance(n, MappingKeyYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.value))
    if isinstance(n, MappingValueYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, n.key)
        yaml_ast_walk(v, n.value)
    if isinstance(n, SequenceYamlNode):
        yaml_ast_walk_comment(v, n)
        for value2 in n.values:
            yaml_ast_walk(v, check.not_none(value2))
    if isinstance(n, AnchorYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.name))
        yaml_ast_walk(v, check.not_none(n.value))
    if isinstance(n, AliasYamlNode):
        yaml_ast_walk_comment(v, n)
        yaml_ast_walk(v, check.not_none(n.value))


def yaml_ast_walk_comment(v: YamlAstVisitor, base: ta.Optional[BaseYamlNode]) -> None:
    if base is None:
        return
    if base.comment is None:
        return
    yaml_ast_walk(v, base.comment)


#


@dc.dataclass()
class FilterYamlAstWalker(YamlAstVisitor):
    typ: YamlNodeType = dc.field(default_factory=dataclass_field_required('typ'))
    results: ta.List[YamlNode] = dc.field(default_factory=list)

    def visit(self, n: YamlNode) -> YamlAstVisitor:
        if self.typ == n.type():
            self.results.append(n)
        return self


#


@dc.dataclass()
class YamlParentFinder:
    target: YamlNode

    def walk(self, parent: YamlNode, node: ta.Optional[YamlNode]) -> ta.Optional[YamlNode]:
        if self.target == node:
            return parent

        n = node
        if isinstance(n, CommentYamlNode):
            return None
        if isinstance(n, NullYamlNode):
            return None
        if isinstance(n, IntegerYamlNode):
            return None
        if isinstance(n, FloatYamlNode):
            return None
        if isinstance(n, StringYamlNode):
            return None
        if isinstance(n, MergeKeyYamlNode):
            return None
        if isinstance(n, BoolYamlNode):
            return None
        if isinstance(n, InfinityYamlNode):
            return None
        if isinstance(n, NanYamlNode):
            return None
        if isinstance(n, LiteralYamlNode):
            return self.walk(n, n.value)
        if isinstance(n, DirectiveYamlNode):
            if (found := self.walk(n, n.name)) is not None:
                return found
            for value0 in n.values:
                if (found := self.walk(n, value0)) is not None:
                    return found
        if isinstance(n, TagYamlNode):
            return self.walk(n, n.value)
        if isinstance(n, DocumentYamlNode):
            return self.walk(n, n.body)
        if isinstance(n, MappingYamlNode):
            for value1 in n.values:
                if (found := self.walk(n, value1)) is not None:
                    return found
        if isinstance(n, MappingKeyYamlNode):
            return self.walk(n, n.value)
        if isinstance(n, MappingValueYamlNode):
            if (found := self.walk(n, n.key)) is not None:
                return found
            return self.walk(n, n.value)
        if isinstance(n, SequenceYamlNode):
            for value2 in n.values:
                if (found := self.walk(n, value2)) is not None:
                    return found
        if isinstance(n, AnchorYamlNode):
            if (found := self.walk(n, n.name)) is not None:
                return found
            return self.walk(n, n.value)
        if isinstance(n, AliasYamlNode):
            return self.walk(n, n.value)
        return None


# Parent get parent node from child node.
def yaml_parent(root: YamlNode, child: YamlNode) -> ta.Optional[YamlNode]:
    finder = YamlParentFinder(target=child)
    return finder.walk(root, root)


#


# Filter returns a list of nodes that match the given type.
def yaml_filter(typ: YamlNodeType, node: YamlNode) -> ta.List[YamlNode]:
    walker = FilterYamlAstWalker(typ=typ)
    yaml_ast_walk(walker, node)
    return walker.results


# FilterFile returns a list of nodes that match the given type.
def yaml_filter_file(typ: YamlNodeType, file: YamlFile) -> ta.List[YamlNode]:
    results: ta.List[YamlNode] = []
    for doc in file.docs:
        walker = FilterYamlAstWalker(typ=typ)
        yaml_ast_walk(walker, doc)
        results.extend(walker.results)
    return results


#


@dc.dataclass()
class InvalidMergeTypeYamlError(YamlError):
    dst: YamlNode
    src: YamlNode

    @property
    def message(self) -> str:
        return f'cannot merge {self.src.type()} into {self.dst.type()}'


# Merge merge document, map, sequence node.
def yaml_ast_merge(dst: YamlNode, src: YamlNode) -> ta.Optional[YamlError]:
    if isinstance(src, DocumentYamlNode):
        doc: DocumentYamlNode = src
        src = check.not_none(doc.body)

    err = InvalidMergeTypeYamlError(dst=dst, src=src)
    if dst.type() == YamlNodeType.DOCUMENT:
        node0: DocumentYamlNode = check.isinstance(dst, DocumentYamlNode)
        return yaml_ast_merge(check.not_none(node0.body), src)
    if dst.type() == YamlNodeType.MAPPING:
        node1: MappingYamlNode = check.isinstance(dst, MappingYamlNode)
        if not isinstance(src, MappingYamlNode):
            return err
        target0: MappingYamlNode = src
        node1.merge(target0)
        return None
    if dst.type() == YamlNodeType.SEQUENCE:
        node2: SequenceYamlNode = check.isinstance(dst, SequenceYamlNode)
        if not isinstance(src, SequenceYamlNode):
            return err
        target1: SequenceYamlNode = src
        node2.merge(target1)
        return None
    return err


########################################
# ../../../omlish/formats/yaml/goyaml/scanning.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


@dc.dataclass()
class InvalidTokenYamlError(YamlError):
    token: YamlToken

    @property
    def message(self) -> str:
        return check.not_none(self.token.error).message


def _yaml_err_invalid_token(tk: YamlToken) -> InvalidTokenYamlError:
    return InvalidTokenYamlError(
        token=tk,
    )


##


# Context at scanning
@dc.dataclass()
class YamlScanningContext:
    idx: int = 0
    size: int = 0
    not_space_char_pos: int = 0
    not_space_org_char_pos: int = 0
    src: ta.List[str] = dc.field(default_factory=list)
    buf: ta.List[str] = dc.field(default_factory=list)
    obuf: ta.List[str] = dc.field(default_factory=list)
    tokens: YamlTokens = dc.field(default_factory=YamlTokens)
    mstate: ta.Optional['YamlMultiLineState'] = None

    def clear(self) -> None:
        self.reset_buffer()
        self.mstate = None

    def reset(self, src: ta.List[str]) -> None:
        self.idx = 0
        self.size = len(src)
        self.src = list(src)
        self.tokens = YamlTokens()
        self.reset_buffer()
        self.mstate = None

    def reset_buffer(self) -> None:
        self.buf = []
        self.obuf = []
        self.not_space_char_pos = 0
        self.not_space_org_char_pos = 0

    def break_multi_line(self) -> None:
        self.mstate = None

    def get_multi_line_state(self) -> ta.Optional['YamlMultiLineState']:
        return self.mstate

    def set_literal(self, last_delim_column: int, opt: str) -> None:
        mstate = YamlMultiLineState(
            is_literal=True,
            opt=opt,
        )
        indent = _yaml_first_line_indent_column_by_opt(opt)
        if indent > 0:
            mstate.first_line_indent_column = last_delim_column + indent
        self.mstate = mstate

    def set_folded(self, last_delim_column: int, opt: str) -> None:
        mstate = YamlMultiLineState(
            is_folded=True,
            opt=opt,
        )
        indent = _yaml_first_line_indent_column_by_opt(opt)
        if indent > 0:
            mstate.first_line_indent_column = last_delim_column + indent
        self.mstate = mstate

    def set_raw_folded(self, column: int) -> None:
        mstate = YamlMultiLineState(
            is_raw_folded=True,
        )
        mstate.update_indent_column(column)
        self.mstate = mstate

    def add_token(self, tk: ta.Optional[YamlToken]) -> None:
        if tk is None:
            return
        self.tokens.append(tk)  # FIXME: .add??

    def add_buf(self, r: str) -> None:
        if len(self.buf) == 0 and (r == ' ' or r == '\t'):
            return
        self.buf += r
        if r != ' ' and r != '\t':
            self.not_space_char_pos = len(self.buf)

    def add_buf_with_tab(self, r: str) -> None:
        if len(self.buf) == 0 and r == ' ':
            return
        self.buf += r
        if r != ' ':
            self.not_space_char_pos = len(self.buf)

    def add_origin_buf(self, r: str) -> None:
        self.obuf += r
        if r != ' ' and r != '\t':
            self.not_space_org_char_pos = len(self.obuf)

    def remove_right_space_from_buf(self) -> None:
        trimmed_buf = self.obuf[:self.not_space_org_char_pos]
        buflen = len(trimmed_buf)
        diff = len(self.obuf) - buflen
        if diff > 0:
            self.obuf = self.obuf[:buflen]
            self.buf = list(self.buffered_src())

    def is_eos(self) -> bool:
        return len(self.src) - 1 <= self.idx

    def is_next_eos(self) -> bool:
        return len(self.src) <= self.idx + 1

    def next(self) -> bool:
        return self.idx < self.size

    def source(self, s: int, e: int) -> str:
        return ''.join(self.src[s:e])

    def previous_char(self) -> str:
        if self.idx > 0:
            return self.src[self.idx - 1]
        return ''

    def current_char(self) -> str:
        if self.size > self.idx:
            return self.src[self.idx]
        return ''

    def next_char(self) -> str:
        if self.size > self.idx + 1:
            return self.src[self.idx + 1]
        return ''

    def repeat_num(self, r: str) -> int:
        cnt = 0
        for i in range(self.idx, self.size):
            if self.src[i] == r:
                cnt += 1
            else:
                break
        return cnt

    def progress(self, num: int) -> None:
        self.idx += num

    def exists_buffer(self) -> bool:
        return len(self.buffered_src()) != 0

    def is_multi_line(self) -> bool:
        return self.mstate is not None

    def buffered_src(self) -> ta.List[str]:
        src = self.buf[:self.not_space_char_pos]

        if self.is_multi_line():
            mstate = check.not_none(self.get_multi_line_state())

            # remove end '\n' character and trailing empty lines.
            # https://yaml.org/spec/1.2.2/#8112-block-chomping-indicator
            if mstate.has_trim_all_end_newline_opt():
                # If the '-' flag is specified, all trailing newline characters will be removed.
                src = list(''.join(src).rstrip('\n'))

            elif not mstate.has_keep_all_end_newline_opt():
                # Normally, all but one of the trailing newline characters are removed.
                new_line_char_count = 0
                for i in range(len(src) - 1, -1, -1):
                    if src[i] == '\n':
                        new_line_char_count += 1
                        continue
                    break

                removed_new_line_char_count = new_line_char_count - 1
                while removed_new_line_char_count > 0:
                    src = list(''.join(src).rstrip('\n'))
                    removed_new_line_char_count -= 1

            # If the text ends with a space character, remove all of them.
            if mstate.has_trim_all_end_newline_opt():
                src = list(''.join(src).rstrip(' '))

            if src == ['\n']:
                # If the content consists only of a newline, it can be considered as the document ending without any
                # specified value, so it is treated as an empty string.
                src = []

            if mstate.has_keep_all_end_newline_opt() and len(src) == 0:
                src = ['\n']

        return src

    def buffered_token(self, pos: YamlPosition) -> ta.Optional[YamlToken]:
        if self.idx == 0:
            return None

        source = self.buffered_src()
        if len(source) == 0:
            self.buf = self.buf[:0]  # clear value's buffer only.
            return None

        tk: ta.Optional[YamlToken]
        if self.is_multi_line():
            tk = YamlTokenMakers.new_string(''.join(source), ''.join(self.obuf), pos)
        else:
            tk = yaml_new_token(''.join(source), ''.join(self.obuf), pos)

        self.set_token_type_by_prev_tag(tk)
        self.reset_buffer()
        return tk

    def set_token_type_by_prev_tag(self, tk: ta.Optional[YamlToken]) -> None:
        last_tk = self.last_token()
        if last_tk is None:
            return

        if last_tk.type != YamlTokenType.TAG:
            return

        tag = last_tk.value
        if tag not in YAML_RESERVED_TAG_KEYWORD_MAP:
            check.not_none(tk).type = YamlTokenType.STRING

    def last_token(self) -> ta.Optional[YamlToken]:
        if len(self.tokens) != 0:
            return self.tokens[-1]

        return None

    @staticmethod
    def new(src: ta.List[str]) -> 'YamlScanningContext':
        ctx = YamlScanningContext()
        ctx.reset(src)
        return ctx


##


@dc.dataclass()
class YamlMultiLineState:
    opt: str = ''
    first_line_indent_column: int = 0
    prev_line_indent_column: int = 0
    line_indent_column: int = 0
    last_not_space_only_line_indent_column: int = 0
    space_only_indent_column: int = 0
    folded_new_line: bool = False
    is_raw_folded: bool = False
    is_literal: bool = False
    is_folded: bool = False

    def last_delim_column(self) -> int:
        if self.first_line_indent_column == 0:
            return 0
        return self.first_line_indent_column - 1

    def update_indent_column(self, column: int) -> None:
        if self.first_line_indent_column == 0:
            self.first_line_indent_column = column
        if self.line_indent_column == 0:
            self.line_indent_column = column

    def update_space_only_indent_column(self, column: int) -> None:
        if self.first_line_indent_column != 0:
            return
        self.space_only_indent_column = column

    def validate_indent_after_space_only(self, column: int) -> ta.Optional[YamlError]:
        if self.first_line_indent_column != 0:
            return None
        if self.space_only_indent_column > column:
            return yaml_error('invalid number of indent is specified after space only')
        return None

    def validate_indent_column(self) -> ta.Optional[YamlError]:
        if _yaml_first_line_indent_column_by_opt(self.opt) == 0:
            return None
        if self.first_line_indent_column > self.line_indent_column:
            return yaml_error('invalid number of indent is specified in the multi-line header')
        return None

    def update_new_line_state(self) -> None:
        self.prev_line_indent_column = self.line_indent_column
        if self.line_indent_column != 0:
            self.last_not_space_only_line_indent_column = self.line_indent_column
        self.folded_new_line = True
        self.line_indent_column = 0

    def is_indent_column(self, column: int) -> bool:
        if self.first_line_indent_column == 0:
            return column == 1
        return self.first_line_indent_column > column

    def add_indent(self, ctx: YamlScanningContext, column: int) -> None:
        if self.first_line_indent_column == 0:
            return

        # If the first line of the document has already been evaluated, the number is treated as the threshold, since
        # the `first_line_indent_column` is a positive number.
        if column < self.first_line_indent_column:
            return

        # `c.folded_new_line` is a variable that is set to True for every newline.
        if not self.is_literal and self.folded_new_line:
            self.folded_new_line = False

        # Since add_buf ignore space character, add to the buffer directly.
        ctx.buf += ' '
        ctx.not_space_char_pos = len(ctx.buf)

    # update_new_line_in_folded if Folded or RawFolded context and the content on the current line starts at the same
    # column as the previous line, treat the new-line-char as a space.
    def update_new_line_in_folded(self, ctx: YamlScanningContext, column: int) -> None:
        if self.is_literal:
            return

        # Folded or RawFolded.

        if not self.folded_new_line:
            return

        last_char = ''
        prev_last_char = ''
        if len(ctx.buf) != 0:
            last_char = ctx.buf[-1]
        if len(ctx.buf) > 1:
            prev_last_char = ctx.buf[-2]

        if self.line_indent_column == self.prev_line_indent_column:
            # ---
            # >
            #  a
            #  b
            if last_char == '\n':
                ctx.buf[-1] = ' '

        elif self.prev_line_indent_column == 0 and self.last_not_space_only_line_indent_column == column:
            # if previous line is indent-space and new-line-char only, prev_line_indent_column is zero. In this case,
            # last new-line-char is removed.
            # ---
            # >
            #  a
            #
            #  b
            if last_char == '\n' and prev_last_char == '\n':
                ctx.buf = ctx.buf[:len(ctx.buf) - 1]
                ctx.not_space_char_pos = len(ctx.buf)

        self.folded_new_line = False

    def has_trim_all_end_newline_opt(self) -> bool:
        return self.opt.startswith('-') or self.opt.endswith('-') or self.is_raw_folded

    def has_keep_all_end_newline_opt(self) -> bool:
        return self.opt.startswith('+') or self.opt.endswith('+')


##


def _yaml_first_line_indent_column_by_opt(opt: str) -> int:
    opt = opt.lstrip('-')
    opt = opt.lstrip('+')
    opt = opt.rstrip('-')
    opt = opt.rstrip('+')
    try:
        return int(opt, 10)
    except ValueError:
        return 0


##


class YamlIndentState(enum.Enum):
    # EQUAL equals previous indent
    EQUAL = enum.auto()
    # UP more indent than previous
    UP = enum.auto()
    # DOWN less indent than previous
    DOWN = enum.auto()
    # KEEP uses not indent token
    KEEP = enum.auto()


# Scanner holds the scanner's internal state while processing a given text. It can be allocated as part of another data
# structure but must be initialized via init before use.
@dc.dataclass()
class YamlScanner:
    source: ta.List[str] = dc.field(default_factory=list)
    source_pos: int = 0
    source_size: int = 0
    # line number. This number starts from 1.
    line: int = 0
    # column number. This number starts from 1.
    column: int = 0
    # offset represents the offset from the beginning of the source.
    offset: int = 0
    # last_delim_column is the last column needed to compare indent is retained.
    last_delim_column: int = 0
    # indent_num indicates the number of spaces used for indentation.
    indent_num: int = 0
    # prev_line_indent_num indicates the number of spaces used for indentation at previous line.
    prev_line_indent_num: int = 0
    # indent_level indicates the level of indent depth. This value does not match the column value.
    indent_level: int = 0
    is_first_char_at_line: bool = False
    is_anchor: bool = False
    is_alias: bool = False
    is_directive: bool = False
    started_flow_sequence_num: int = 0
    started_flow_map_num: int = 0
    indent_state: YamlIndentState = YamlIndentState.EQUAL
    saved_pos: ta.Optional[YamlPosition] = None

    def pos(self) -> YamlPosition:
        return YamlPosition(
            line=self.line,
            column=self.column,
            offset=self.offset,
            indent_num=self.indent_num,
            indent_level=self.indent_level,
        )

    def buffered_token(self, ctx: YamlScanningContext) -> ta.Optional[YamlToken]:
        if self.saved_pos is not None:
            tk = ctx.buffered_token(self.saved_pos)
            self.saved_pos = None
            return tk

        line = self.line
        column = self.column - len(ctx.buf)
        level = self.indent_level
        if ctx.is_multi_line():
            line -= self.new_line_count(ctx.buf)
            column = ''.join(ctx.obuf).find(''.join(ctx.buf)) + 1
            # Since we are in a literal, folded or raw folded we can use the indent level from the last token.
            last = ctx.last_token()
            if last is not None:  # The last token should never be None here.
                level = last.position.indent_level + 1

        return ctx.buffered_token(YamlPosition(
            line=line,
            column=column,
            offset=self.offset - len(ctx.buf),
            indent_num=self.indent_num,
            indent_level=level,
        ))

    def progress_column(self, ctx: YamlScanningContext, num: int) -> None:
        self.column += num
        self.offset += num
        self.progress(ctx, num)

    def progress_only(self, ctx: YamlScanningContext, num: int) -> None:
        self.offset += num
        self.progress(ctx, num)

    def progress_line(self, ctx: YamlScanningContext) -> None:
        self.prev_line_indent_num = self.indent_num
        self.column = 1
        self.line += 1
        self.offset += 1
        self.indent_num = 0
        self.is_first_char_at_line = True
        self.is_anchor = False
        self.is_alias = False
        self.is_directive = False
        self.progress(ctx, 1)

    def progress(self, ctx: YamlScanningContext, num: int) -> None:
        ctx.progress(num)
        self.source_pos += num

    def is_new_line_char(self, c: str) -> bool:
        if c == '\n':
            return True
        if c == '\r':
            return True
        return False

    def new_line_count(self, src: ta.List[str]) -> int:
        size = len(src)
        cnt = 0
        i = -1
        while True:
            i += 1
            if not (i < size):
                break
            c = src[i]
            if c == '\r':
                if i + 1 < size and src[i + 1] == '\n':
                    i += 1
                cnt += 1
            elif c == '\n':
                cnt += 1
        return cnt

    def update_indent_level(self) -> None:
        if self.prev_line_indent_num < self.indent_num:
            self.indent_level += 1
        elif self.prev_line_indent_num > self.indent_num:
            if self.indent_level > 0:
                self.indent_level -= 1

    def update_indent_state(self, ctx: YamlScanningContext) -> None:
        if self.last_delim_column == 0:
            return

        if self.last_delim_column < self.column:
            self.indent_state = YamlIndentState.UP
        else:
            # If last_delim_column and self.column are the same, treat as Down state since it is the same column as
            # delimiter.
            self.indent_state = YamlIndentState.DOWN

    def update_indent(self, ctx: YamlScanningContext, c: str) -> None:
        if self.is_first_char_at_line and self.is_new_line_char(c):
            return
        if self.is_first_char_at_line and c == ' ':
            self.indent_num += 1
            return
        if self.is_first_char_at_line and c == '\t':
            # Found tab indent. In this case, scan_tab returns error.
            return
        if not self.is_first_char_at_line:
            self.indent_state = YamlIndentState.KEEP
            return
        self.update_indent_level()
        self.update_indent_state(ctx)
        self.is_first_char_at_line = False

    def is_changed_to_indent_state_down(self) -> bool:
        return self.indent_state == YamlIndentState.DOWN

    def is_changed_to_indent_state_up(self) -> bool:
        return self.indent_state == YamlIndentState.UP

    def add_buffered_token_if_exists(self, ctx: YamlScanningContext) -> None:
        ctx.add_token(self.buffered_token(ctx))

    def break_multi_line(self, ctx: YamlScanningContext) -> None:
        ctx.break_multi_line()

    def scan_single_quote(self, ctx: YamlScanningContext) -> YamlErrorOr[YamlToken]:
        ctx.add_origin_buf("'")
        srcpos = self.pos()
        start_index = ctx.idx + 1
        src = ctx.src
        size = len(src)
        value: ta.List[str] = []
        is_first_line_char = False
        is_new_line = False

        idx = start_index - 1
        while True:
            idx += 1
            if not (idx < size):
                break

            if not is_new_line:
                self.progress_column(ctx, 1)
            else:
                is_new_line = False

            c = src[idx]
            ctx.add_origin_buf(c)
            if self.is_new_line_char(c):
                not_space_idx = -1
                for i in range(len(value) - 1, -1, -1):
                    if value[i] == ' ':
                        continue
                    not_space_idx = i
                    break

                if len(value) > not_space_idx:
                    value = value[:not_space_idx + 1]
                if is_first_line_char:
                    value += '\n'
                else:
                    value += ' '

                is_first_line_char = True
                is_new_line = True
                self.progress_line(ctx)
                if idx + 1 < size:
                    if (err := self.validate_document_separator_marker(ctx, src[idx + 1:])) is not None:
                        return err

                continue

            if is_first_line_char and c == ' ':
                continue

            if is_first_line_char and c == '\t':
                if self.last_delim_column >= self.column:
                    return _yaml_err_invalid_token(
                        YamlTokenMakers.new_invalid(
                            yaml_error('tab character cannot be used for indentation in single-quoted text'),
                            ''.join(ctx.obuf),
                            self.pos(),
                        ),
                    )

                continue

            if c != "'":
                value += c
                is_first_line_char = False
                continue

            if idx + 1 < len(ctx.src) and ctx.src[idx + 1] == '\'':
                # '' handle as ' character
                value += c
                ctx.add_origin_buf(c)
                idx += 1
                self.progress_column(ctx, 1)
                continue

            self.progress_column(ctx, 1)
            return YamlTokenMakers.new_single_quote(''.join(value), ''.join(ctx.obuf), srcpos)

        self.progress_column(ctx, 1)
        return _yaml_err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error('could not find end character of single-quoted text'),
                ''.join(ctx.obuf),
                srcpos,
            ),
        )

    def scan_double_quote(self, ctx: YamlScanningContext) -> YamlErrorOr[YamlToken]:
        ctx.add_origin_buf('"')
        srcpos = self.pos()
        start_index = ctx.idx + 1
        src = ctx.src
        size = len(src)
        value: ta.List[str] = []
        is_first_line_char = False
        is_new_line = False

        idx = start_index - 1
        while True:
            idx += 1
            if not (idx < size):
                break

            if not is_new_line:
                self.progress_column(ctx, 1)
            else:
                is_new_line = False

            c = src[idx]
            ctx.add_origin_buf(c)
            if self.is_new_line_char(c):
                not_space_idx = -1
                for i in range(len(value) - 1, -1, -1):
                    if value[i] == ' ':
                        continue
                    not_space_idx = i
                    break

                if len(value) > not_space_idx:
                    value = value[:not_space_idx + 1]

                if is_first_line_char:
                    value += '\n'
                else:
                    value += ' '

                is_first_line_char = True
                is_new_line = True
                self.progress_line(ctx)
                if idx + 1 < size:
                    if (err := self.validate_document_separator_marker(ctx, src[idx + 1:])) is not None:
                        return err

                continue

            if is_first_line_char and c == ' ':
                continue

            if is_first_line_char and c == '\t':
                if self.last_delim_column >= self.column:
                    return _yaml_err_invalid_token(
                        YamlTokenMakers.new_invalid(
                            yaml_error('tab character cannot be used for indentation in double-quoted text'),
                            ''.join(ctx.obuf),
                            self.pos(),
                        ),
                    )

                continue

            if c == '\\':
                is_first_line_char = False
                if idx + 1 >= size:
                    value += c
                    continue

                next_char = src[idx + 1]
                progress = 0

                if next_char == '0':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += chr(0)
                elif next_char == 'a':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x07'
                elif next_char == 'b':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x08'
                elif next_char == 't':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x09'
                elif next_char == 'n':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0A'
                elif next_char == 'v':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0B'
                elif next_char == 'f':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0C'
                elif next_char == 'r':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x0D'
                elif next_char == 'e':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x1B'
                elif next_char == ' ':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x20'
                elif next_char == '"':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x22'
                elif next_char == '/':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x2F'
                elif next_char == '\\':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x5C'
                elif next_char == 'N':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\x85'
                elif next_char == '_':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\xA0'
                elif next_char == 'L':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\u2028'
                elif next_char == 'P':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += '\u2029'

                elif next_char == 'x':
                    if idx + 3 >= size:
                        progress = 1
                        ctx.add_origin_buf(next_char)
                        value += next_char
                    else:
                        progress = 3
                        code_num = _yaml_hex_runes_to_int(src[idx + 2: idx + progress + 1])
                        value += chr(code_num)

                elif next_char == 'u':
                    # \u0000 style must have 5 characters at least.
                    if idx + 5 >= size:
                        return _yaml_err_invalid_token(
                            YamlTokenMakers.new_invalid(
                                yaml_error('not enough length for escaped UTF-16 character'),
                                ''.join(ctx.obuf),
                                self.pos(),
                            ),
                        )

                    progress = 5
                    code_num = _yaml_hex_runes_to_int(src[idx + 2: idx + 6])

                    # handle surrogate pairs.
                    if code_num >= 0xD800 and code_num <= 0xDBFF:
                        high = code_num

                        # \u0000\u0000 style must have 11 characters at least.
                        if idx + 11 >= size:
                            return _yaml_err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('not enough length for escaped UTF-16 surrogate pair'),
                                    ''.join(ctx.obuf),
                                    self.pos(),
                                ),
                            )

                        if src[idx + 6] != '\\' or src[idx + 7] != 'u':
                            return _yaml_err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('found unexpected character after high surrogate for UTF-16 surrogate pair'),  # noqa
                                    ''.join(ctx.obuf),
                                    self.pos(),
                                ),
                            )

                        low = _yaml_hex_runes_to_int(src[idx + 8: idx + 12])
                        if low < 0xDC00 or low > 0xDFFF:
                            return _yaml_err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('found unexpected low surrogate after high surrogate'),
                                    ''.join(ctx.obuf),
                                    self.pos(),
                                ),
                            )

                        code_num = ((high - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000
                        progress += 6

                    value += chr(code_num)

                elif next_char == 'U':
                    # \U00000000 style must have 9 characters at least.
                    if idx + 9 >= size:
                        return _yaml_err_invalid_token(
                            YamlTokenMakers.new_invalid(
                                yaml_error('not enough length for escaped UTF-32 character'),
                                ''.join(ctx.obuf),
                                self.pos(),
                            ),
                        )

                    progress = 9
                    code_num = _yaml_hex_runes_to_int(src[idx + 2: idx + 10])
                    value += chr(code_num)

                elif next_char == '\n':
                    is_first_line_char = True
                    is_new_line = True
                    ctx.add_origin_buf(next_char)
                    self.progress_column(ctx, 1)
                    self.progress_line(ctx)
                    idx += 1
                    continue

                elif next_char == '\r':
                    is_first_line_char = True
                    is_new_line = True
                    ctx.add_origin_buf(next_char)
                    self.progress_line(ctx)
                    progress = 1
                    # Skip \n after \r in CRLF sequences
                    if idx + 2 < size and src[idx + 2] == '\n':
                        ctx.add_origin_buf('\n')
                        progress = 2

                elif next_char == '\t':
                    progress = 1
                    ctx.add_origin_buf(next_char)
                    value += next_char

                else:
                    self.progress_column(ctx, 1)
                    return _yaml_err_invalid_token(
                        YamlTokenMakers.new_invalid(
                            yaml_error(f'found unknown escape character {next_char!r}'),
                            ''.join(ctx.obuf),
                            self.pos(),
                        ),
                    )

                idx += progress
                self.progress_column(ctx, progress)
                continue

            if c == '\t':
                found_not_space_char = False
                progress = 0

                for i in range(idx + 1, size):
                    if src[i] == ' ' or src[i] == '\t':
                        progress += 1
                        continue

                    if self.is_new_line_char(src[i]):
                        break

                    found_not_space_char = True

                if found_not_space_char:
                    value += c
                    if src[idx + 1] != '"':
                        self.progress_column(ctx, 1)

                else:
                    idx += progress
                    self.progress_column(ctx, progress)

                continue

            if c != '"':
                value += c
                is_first_line_char = False
                continue

            self.progress_column(ctx, 1)
            return YamlTokenMakers.new_double_quote(''.join(value), ''.join(ctx.obuf), srcpos)

        self.progress_column(ctx, 1)
        return _yaml_err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error('could not find end character of double-quoted text'),
                ''.join(ctx.obuf),
                srcpos,
            ),
        )

    def validate_document_separator_marker(self, ctx: YamlScanningContext, src: ta.List[str]) -> ta.Optional[YamlError]:
        if self.found_document_separator_marker(src):
            return _yaml_err_invalid_token(
                YamlTokenMakers.new_invalid(
                    yaml_error('found unexpected document separator'),
                    ''.join(ctx.obuf),
                    self.pos(),
                ),
            )

        return None

    def found_document_separator_marker(self, src: ta.List[str]) -> bool:
        if len(src) < 3:
            return False

        marker = ''
        if len(src) == 3:
            marker = ''.join(src)
        else:
            marker = _yaml_trim_right_func(''.join(src[:4]), lambda r: r == ' ' or r == '\t' or r == '\n' or r == '\r')

        return marker == '---' or marker == '...'

    def scan_quote(self, ctx: YamlScanningContext, ch: str) -> YamlErrorOr[bool]:
        if ctx.exists_buffer():
            return False

        if ch == "'":
            tk = self.scan_single_quote(ctx)
            if isinstance(tk, YamlError):
                return tk

            ctx.add_token(tk)

        else:
            tk = self.scan_double_quote(ctx)
            if isinstance(tk, YamlError):
                return tk

            ctx.add_token(tk)

        ctx.clear()
        return True

    def scan_white_space(self, ctx: YamlScanningContext) -> bool:
        if ctx.is_multi_line():
            return False

        if not self.is_anchor and not self.is_directive and not self.is_alias and not self.is_first_char_at_line:
            return False

        if self.is_first_char_at_line:
            self.progress_column(ctx, 1)
            ctx.add_origin_buf(' ')
            return True

        if self.is_directive:
            self.add_buffered_token_if_exists(ctx)
            self.progress_column(ctx, 1)
            ctx.add_origin_buf(' ')
            return True

        self.add_buffered_token_if_exists(ctx)
        self.is_anchor = False
        self.is_alias = False
        return True

    def is_merge_key(self, ctx: YamlScanningContext) -> bool:
        if ctx.repeat_num('<') != 2:
            return False

        src = ctx.src
        size = len(src)
        for idx in range(ctx.idx + 2, size):
            c = src[idx]
            if c == ' ':
                continue

            if c != ':':
                return False

            if idx + 1 < size:
                nc = src[idx + 1]
                if nc == ' ' or self.is_new_line_char(nc):
                    return True

        return False

    def scan_tag(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        if ctx.exists_buffer() or self.is_directive:
            return False

        ctx.add_origin_buf('!')
        self.progress(ctx, 1)  # skip '!' character

        progress = 0
        for idx, c in enumerate(ctx.src[ctx.idx:]):
            progress = idx + 1

            if c == ' ':
                ctx.add_origin_buf(c)
                value = ctx.source(ctx.idx - 1, ctx.idx + idx)
                ctx.add_token(YamlTokenMakers.new_tag(value, ''.join(ctx.obuf), self.pos()))
                self.progress_column(ctx, len(value))
                ctx.clear()
                return True

            elif c == ',':
                if self.started_flow_sequence_num > 0 or self.started_flow_map_num > 0:
                    value = ctx.source(ctx.idx - 1, ctx.idx + idx)
                    ctx.add_token(YamlTokenMakers.new_tag(value, ''.join(ctx.obuf), self.pos()))
                    # progress column before collect-entry for scanning it at scan_flow_entry function.
                    self.progress_column(ctx, len(value) - 1)
                    ctx.clear()
                    return True
                else:
                    ctx.add_origin_buf(c)

            elif c in ('\n', '\r'):
                ctx.add_origin_buf(c)
                value = ctx.source(ctx.idx - 1, ctx.idx + idx)
                ctx.add_token(YamlTokenMakers.new_tag(value, ''.join(ctx.obuf), self.pos()))
                # progress column before new-line-char for scanning new-line-char at scan_new_line function.
                self.progress_column(ctx, len(value) - 1)
                ctx.clear()
                return True

            elif c in ('{', '}'):
                ctx.add_origin_buf(c)
                self.progress_column(ctx, progress)
                invalid_tk = YamlTokenMakers.new_invalid(
                    yaml_error(f'found invalid tag character {c!r}'),
                    ''.join(ctx.obuf),
                    self.pos(),
                )
                return _yaml_err_invalid_token(invalid_tk)

            else:
                ctx.add_origin_buf(c)

        self.progress_column(ctx, progress)
        ctx.clear()
        return True

    def scan_comment(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            c = ctx.previous_char()
            if c != ' ' and c != '\t' and not self.is_new_line_char(c):
                return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('#')
        self.progress(ctx, 1)  # skip '#' character

        for idx, c in enumerate(ctx.src[ctx.idx:]):
            ctx.add_origin_buf(c)
            if not self.is_new_line_char(c):
                continue
            if ctx.previous_char() == '\\':
                continue

            value = ctx.source(ctx.idx, ctx.idx + idx)
            progress = len(value)
            ctx.add_token(YamlTokenMakers.new_comment(''.join(value), ''.join(ctx.obuf), self.pos()))
            self.progress_column(ctx, progress)
            self.progress_line(ctx)
            ctx.clear()
            return True

        # document ends with comment.
        value = ''.join(ctx.src[ctx.idx:])
        ctx.add_token(YamlTokenMakers.new_comment(value, ''.join(ctx.obuf), self.pos()))
        progress = len(value)
        self.progress_column(ctx, progress)
        self.progress_line(ctx)
        ctx.clear()
        return True

    def scan_multi_line(self, ctx: YamlScanningContext, c: str) -> ta.Optional[YamlError]:
        state = check.not_none(ctx.get_multi_line_state())
        ctx.add_origin_buf(c)

        # normalize CR and CRLF to LF
        if c == '\r':
            if ctx.next_char() == '\n':
                ctx.add_origin_buf('\n')
                self.progress(ctx, 1)
                self.offset += 1

            c = '\n'

        if ctx.is_eos():
            if self.is_first_char_at_line and c == ' ':
                state.add_indent(ctx, self.column)
            else:
                ctx.add_buf(c)

            state.update_indent_column(self.column)
            if (err := state.validate_indent_column()) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ''.join(ctx.obuf), self.pos())
                self.progress_column(ctx, 1)
                return _yaml_err_invalid_token(invalid_tk)

            value = ctx.buffered_src()
            ctx.add_token(YamlTokenMakers.new_string(''.join(value), ''.join(ctx.obuf), self.pos()))
            ctx.clear()
            self.progress_column(ctx, 1)

        elif self.is_new_line_char(c):
            ctx.add_buf(c)
            state.update_space_only_indent_column(self.column - 1)
            state.update_new_line_state()
            self.progress_line(ctx)
            if ctx.next():
                if self.found_document_separator_marker(ctx.src[ctx.idx:]):
                    value = ctx.buffered_src()
                    ctx.add_token(YamlTokenMakers.new_string(''.join(value), ''.join(ctx.obuf), self.pos()))
                    ctx.clear()
                    self.break_multi_line(ctx)

        elif self.is_first_char_at_line and c == ' ':
            state.add_indent(ctx, self.column)
            self.progress_column(ctx, 1)

        elif self.is_first_char_at_line and c == '\t' and state.is_indent_column(self.column):
            err = _yaml_err_invalid_token(
                YamlTokenMakers.new_invalid(
                    yaml_error('found a tab character where an indentation space is expected'),
                    ''.join(ctx.obuf),
                    self.pos(),
                ),
            )
            self.progress_column(ctx, 1)
            return err

        elif c == '\t' and not state.is_indent_column(self.column):
            ctx.add_buf_with_tab(c)
            self.progress_column(ctx, 1)

        else:
            if (err := state.validate_indent_after_space_only(self.column)) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ''.join(ctx.obuf), self.pos())
                self.progress_column(ctx, 1)
                return _yaml_err_invalid_token(invalid_tk)

            state.update_indent_column(self.column)
            if (err := state.validate_indent_column()) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ''.join(ctx.obuf), self.pos())
                self.progress_column(ctx, 1)
                return _yaml_err_invalid_token(invalid_tk)

            if (col := state.last_delim_column()) > 0:
                self.last_delim_column = col

            state.update_new_line_in_folded(ctx, self.column)
            ctx.add_buf_with_tab(c)
            self.progress_column(ctx, 1)

        return None

    def scan_new_line(self, ctx: YamlScanningContext, c: str) -> None:
        if len(ctx.buf) > 0 and self.saved_pos is None:
            buf_len = len(ctx.buffered_src())
            self.saved_pos = self.pos()
            self.saved_pos.column -= buf_len
            self.saved_pos.offset -= buf_len

        # if the following case, origin buffer has unnecessary two spaces.
        # So, `removeRightSpaceFromOriginBuf` remove them, also fix column number too.
        # ---
        # a:[space][space]
        #   b: c
        ctx.remove_right_space_from_buf()

        # There is no problem that we ignore CR which followed by LF and normalize it to LF, because of following
        # YAML1.2 spec.
        # > Line breaks inside scalar content must be normalized by the YAML processor. Each such line break must be
        #   parsed into a single line feed character.
        # > Outside scalar content, YAML allows any line break to be used to terminate lines.
        # > -- https://yaml.org/spec/1.2/spec.html
        if c == '\r' and ctx.next_char() == '\n':
            ctx.add_origin_buf('\r')
            self.progress(ctx, 1)
            self.offset += 1
            c = '\n'

        if ctx.is_eos():
            self.add_buffered_token_if_exists(ctx)
        elif self.is_anchor or self.is_alias or self.is_directive:
            self.add_buffered_token_if_exists(ctx)

        if ctx.exists_buffer() and self.is_first_char_at_line:
            if ctx.buf[-1] == ' ':
                ctx.buf[-1] = '\n'
            else:
                ctx.buf += '\n'
        else:
            ctx.add_buf(' ')

        ctx.add_origin_buf(c)
        self.progress_line(ctx)

    def is_flow_mode(self) -> bool:
        if self.started_flow_sequence_num > 0:
            return True

        if self.started_flow_map_num > 0:
            return True

        return False

    def scan_flow_map_start(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer() and not self.is_flow_mode():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('{')
        ctx.add_token(YamlTokenMakers.new_mapping_start(''.join(ctx.obuf), self.pos()))
        self.started_flow_map_num += 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_map_end(self, ctx: YamlScanningContext) -> bool:
        if self.started_flow_map_num <= 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('}')
        ctx.add_token(YamlTokenMakers.new_mapping_end(''.join(ctx.obuf), self.pos()))
        self.started_flow_map_num -= 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_array_start(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer() and not self.is_flow_mode():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('[')
        ctx.add_token(YamlTokenMakers.new_sequence_start(''.join(ctx.obuf), self.pos()))
        self.started_flow_sequence_num += 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_array_end(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer() and self.started_flow_sequence_num <= 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf(']')
        ctx.add_token(YamlTokenMakers.new_sequence_end(''.join(ctx.obuf), self.pos()))
        self.started_flow_sequence_num -= 1
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_flow_entry(self, ctx: YamlScanningContext, c: str) -> bool:
        if self.started_flow_sequence_num <= 0 and self.started_flow_map_num <= 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf(c)
        ctx.add_token(YamlTokenMakers.new_collect_entry(''.join(ctx.obuf), self.pos()))
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_map_delim(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        nc = ctx.next_char()
        if self.is_directive or self.is_anchor or self.is_alias:
            return False

        if (
                self.started_flow_map_num <= 0 and
                nc != ' ' and
                nc != '\t' and
                not self.is_new_line_char(nc) and
                not ctx.is_next_eos()
        ):
            return False

        if self.started_flow_map_num > 0 and nc == '/':
            # like http://
            return False

        if self.started_flow_map_num > 0:
            tk = ctx.last_token()
            if tk is not None and tk.type == YamlTokenType.MAPPING_VALUE:
                return False

        if ''.join(ctx.obuf).lstrip(' ').startswith('\t') and not ''.join(ctx.buf).startswith('\t'):
            invalid_tk = YamlTokenMakers.new_invalid(
                yaml_error('tab character cannot use as a map key directly'),
                ''.join(ctx.obuf),
                self.pos(),
            )
            self.progress_column(ctx, 1)
            return _yaml_err_invalid_token(invalid_tk)

        # mapping value
        tk = self.buffered_token(ctx)
        if tk is not None:
            self.last_delim_column = tk.position.column
            ctx.add_token(tk)

        elif (tk := ctx.last_token()) is not None:
            # If the map key is quote, the buffer does not exist because it has already been cut into tokens.
            # Therefore, we need to check the last token.
            if tk.indicator == YamlIndicator.QUOTED_SCALAR:
                self.last_delim_column = tk.position.column

        ctx.add_token(YamlTokenMakers.new_mapping_value(self.pos()))
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_document_start(self, ctx: YamlScanningContext) -> bool:
        if self.indent_num != 0:
            return False

        if self.column != 1:
            return False

        if ctx.repeat_num('-') != 3:
            return False

        if ctx.size > ctx.idx + 3:
            c = ctx.src[ctx.idx + 3]
            if c != ' ' and c != '\t' and c != '\n' and c != '\r':
                return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_token(YamlTokenMakers.new_document_header(''.join(ctx.obuf) + '---', self.pos()))
        self.progress_column(ctx, 3)
        ctx.clear()
        self.clear_state()
        return True

    def scan_document_end(self, ctx: YamlScanningContext) -> bool:
        if self.indent_num != 0:
            return False

        if self.column != 1:
            return False

        if ctx.repeat_num('.') != 3:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_token(YamlTokenMakers.new_document_end(''.join(ctx.obuf) + '...', self.pos()))
        self.progress_column(ctx, 3)
        ctx.clear()
        return True

    def scan_merge_key(self, ctx: YamlScanningContext) -> bool:
        if not self.is_merge_key(ctx):
            return False

        self.last_delim_column = self.column
        ctx.add_token(YamlTokenMakers.new_merge_key(''.join(ctx.obuf) + '<<', self.pos()))
        self.progress_column(ctx, 2)
        ctx.clear()
        return True

    def scan_raw_folded_char(self, ctx: YamlScanningContext) -> bool:
        if not ctx.exists_buffer():
            return False

        if not self.is_changed_to_indent_state_up():
            return False

        ctx.set_raw_folded(self.column)
        ctx.add_buf('-')
        ctx.add_origin_buf('-')
        self.progress_column(ctx, 1)
        return True

    def scan_sequence(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        if ctx.exists_buffer():
            return False

        nc = ctx.next_char()
        if nc != 0 and nc != ' ' and nc != '\t' and not self.is_new_line_char(nc):
            return False

        if ''.join(ctx.obuf).lstrip(' ').startswith('\t'):
            invalid_tk = YamlTokenMakers.new_invalid(
                yaml_error('tab character cannot use as a sequence delimiter'),
                ''.join(ctx.obuf),
                self.pos(),
            )
            self.progress_column(ctx, 1)
            return _yaml_err_invalid_token(invalid_tk)

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('-')
        tk = YamlTokenMakers.new_sequence_entry(''.join(ctx.obuf), self.pos())
        self.last_delim_column = tk.position.column
        ctx.add_token(tk)
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_multi_line_header(self, ctx: YamlScanningContext) -> YamlErrorOr[bool]:
        if ctx.exists_buffer():
            return False

        if (err := self.scan_multi_line_header_option(ctx)) is not None:
            return err

        self.progress_line(ctx)
        return True

    def validate_multi_line_header_option(self, opt: str) -> ta.Optional[YamlError]:
        if len(opt) == 0:
            return None

        org_opt = opt
        opt = opt.lstrip('-')
        opt = opt.lstrip('+')
        opt = opt.rstrip('-')
        opt = opt.rstrip('+')
        if len(opt) == 0:
            return None

        if opt == '0':
            return yaml_error(f'invalid header option: {org_opt!r}')

        try:
            i = int(opt, 10)
        except ValueError:
            return yaml_error(f'invalid header option: {org_opt!r}')

        if i > 9:
            return yaml_error(f'invalid header option: {org_opt!r}')

        return None

    def scan_multi_line_header_option(self, ctx: YamlScanningContext) -> ta.Optional[YamlError]:
        header = ctx.current_char()
        ctx.add_origin_buf(header)
        self.progress(ctx, 1)  # skip '|' or '>' character

        progress = 0
        crlf = False
        for idx, c in enumerate(ctx.src[ctx.idx:]):
            progress = idx
            ctx.add_origin_buf(c)
            if self.is_new_line_char(c):
                next_idx = ctx.idx + idx + 1
                if c == '\r' and next_idx < len(ctx.src) and ctx.src[next_idx] == '\n':
                    crlf = True
                    continue  # process \n in the next iteration

                break

        end_pos = ctx.idx + progress
        if crlf:
            # Exclude \r
            end_pos = end_pos - 1

        value = ctx.source(ctx.idx, end_pos).rstrip(' ')
        comment_value_index = value.find('#')
        opt = value
        if comment_value_index > 0:
            opt = value[:comment_value_index]

        opt = _yaml_trim_right_func(opt, lambda r: r == ' ' or r == '\t')

        if len(opt) != 0:
            if (err := self.validate_multi_line_header_option(opt)) is not None:
                invalid_tk = YamlTokenMakers.new_invalid(yaml_error(str(err)), ''.join(ctx.obuf), self.pos())
                self.progress_column(ctx, progress)
                return _yaml_err_invalid_token(invalid_tk)

        if self.column == 1:
            self.last_delim_column = 1

        try:
            comment_index = ctx.obuf.index('#')
        except ValueError:
            comment_index = -1
        header_buf = ''.join(ctx.obuf)
        if comment_index > 0:
            header_buf = header_buf[:comment_index]

        if header == '|':
            ctx.add_token(YamlTokenMakers.new_literal('|' + opt, header_buf, self.pos()))
            ctx.set_literal(self.last_delim_column, opt)
        elif header == '>':
            ctx.add_token(YamlTokenMakers.new_folded('>' + opt, header_buf, self.pos()))
            ctx.set_folded(self.last_delim_column, opt)

        if comment_index > 0:
            comment = value[comment_value_index + 1:]
            self.offset += len(header_buf)
            self.column += len(header_buf)
            ctx.add_token(YamlTokenMakers.new_comment(comment, ''.join(ctx.obuf[len(header_buf):]), self.pos()))

        self.indent_state = YamlIndentState.KEEP
        ctx.reset_buffer()
        self.progress_column(ctx, progress)
        return None

    def scan_map_key(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False

        nc = ctx.next_char()
        if nc != ' ' and nc != '\t':
            return False

        tk = YamlTokenMakers.new_mapping_key(self.pos())
        self.last_delim_column = tk.position.column
        ctx.add_token(tk)
        self.progress_column(ctx, 1)
        ctx.clear()
        return True

    def scan_directive(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False
        if self.indent_num != 0:
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('%')
        ctx.add_token(YamlTokenMakers.new_directive(''.join(ctx.obuf), self.pos()))
        self.progress_column(ctx, 1)
        ctx.clear()
        self.is_directive = True
        return True

    def scan_anchor(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('&')
        ctx.add_token(YamlTokenMakers.new_anchor(''.join(ctx.obuf), self.pos()))
        self.progress_column(ctx, 1)
        self.is_anchor = True
        ctx.clear()
        return True

    def scan_alias(self, ctx: YamlScanningContext) -> bool:
        if ctx.exists_buffer():
            return False

        self.add_buffered_token_if_exists(ctx)
        ctx.add_origin_buf('*')
        ctx.add_token(YamlTokenMakers.new_alias(''.join(ctx.obuf), self.pos()))
        self.progress_column(ctx, 1)
        self.is_alias = True
        ctx.clear()
        return True

    def scan_reserved_char(self, ctx: YamlScanningContext, c: str) -> ta.Optional[YamlError]:
        if ctx.exists_buffer():
            return None

        ctx.add_buf(c)
        ctx.add_origin_buf(c)
        err = _yaml_err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error(f'{c!r} is a reserved character'),
                ''.join(ctx.obuf),
                self.pos(),
            ),
        )
        self.progress_column(ctx, 1)
        ctx.clear()
        return err

    def scan_tab(self, ctx: YamlScanningContext, c: str) -> ta.Optional[YamlError]:
        if self.started_flow_sequence_num > 0 or self.started_flow_map_num > 0:
            # tabs character is allowed in flow mode.
            return None

        if not self.is_first_char_at_line:
            return None

        ctx.add_buf(c)
        ctx.add_origin_buf(c)
        err = _yaml_err_invalid_token(
            YamlTokenMakers.new_invalid(
                yaml_error("found character '\t' that cannot start any token"),
                ''.join(ctx.obuf),
                self.pos(),
            ),
        )
        self.progress_column(ctx, 1)
        ctx.clear()
        return err

    def _scan(self, ctx: YamlScanningContext) -> ta.Optional[YamlError]:
        while ctx.next():
            c = ctx.current_char()
            # First, change the IndentState.
            # If the target character is the first character in a line, IndentState is Up/Down/Equal state.
            # The second and subsequent letters are Keep.
            self.update_indent(ctx, c)

            # If IndentState is down, tokens are split, so the buffer accumulated until that point needs to be cutted as
            # a token.
            if self.is_changed_to_indent_state_down():
                self.add_buffered_token_if_exists(ctx)

            if ctx.is_multi_line():
                if self.is_changed_to_indent_state_down():
                    if (tk := ctx.last_token()) is not None:
                        # If literal/folded content is empty, no string token is added.
                        # Therefore, add an empty string token.
                        # But if literal/folded token column is 1, it is invalid at down state.
                        if tk.position.column == 1:
                            return yaml_error(_yaml_err_invalid_token(
                                YamlTokenMakers.new_invalid(
                                    yaml_error('could not find multi-line content'),
                                    ''.join(ctx.obuf),
                                    self.pos(),
                                ),
                            ))

                        if tk.type != YamlTokenType.STRING:
                            ctx.add_token(YamlTokenMakers.new_string('', '', self.pos()))

                    self.break_multi_line(ctx)

                else:
                    if (err := self.scan_multi_line(ctx, c)) is not None:
                        return err

                    continue

            if c == '{':
                if self.scan_flow_map_start(ctx):
                    continue

            elif c == '}':
                if self.scan_flow_map_end(ctx):
                    continue

            elif c == '.':
                if self.scan_document_end(ctx):
                    continue

            elif c == '<':
                if self.scan_merge_key(ctx):
                    continue

            elif c == '-':
                if self.scan_document_start(ctx):
                    continue

                if self.scan_raw_folded_char(ctx):
                    continue

                scanned = self.scan_sequence(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c == '[':
                if self.scan_flow_array_start(ctx):
                    continue

            elif c == ']':
                if self.scan_flow_array_end(ctx):
                    continue

            elif c == ',':
                if self.scan_flow_entry(ctx, c):
                    continue

            elif c == ':':
                scanned = self.scan_map_delim(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c in ('|', '>'):
                scanned = self.scan_multi_line_header(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c == '!':
                scanned = self.scan_tag(ctx)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c == '%':
                if self.scan_directive(ctx):
                    continue

            elif c == '?':
                if self.scan_map_key(ctx):
                    continue

            elif c == '&':
                if self.scan_anchor(ctx):
                    continue

            elif c == '*':
                if self.scan_alias(ctx):
                    continue

            elif c == '#':
                if self.scan_comment(ctx):
                    continue

            elif c in ("'", '"'):
                scanned = self.scan_quote(ctx, c)
                if isinstance(scanned, YamlError):
                    return scanned

                if scanned:
                    continue

            elif c in ('\r', '\n'):
                self.scan_new_line(ctx, c)
                continue

            elif c == ' ':
                if self.scan_white_space(ctx):
                    continue

            elif c in ('@', '`'):
                if (err := self.scan_reserved_char(ctx, c)) is not None:
                    return err

            elif c == '\t':
                if ctx.exists_buffer() and self.last_delim_column == 0:
                    # tab indent for plain text (yaml-test-suite's spec-example-7-12-plain-lines).
                    self.indent_num += 1
                    ctx.add_origin_buf(c)
                    self.progress_only(ctx, 1)
                    continue

                if self.last_delim_column < self.column:
                    self.indent_num += 1
                    ctx.add_origin_buf(c)
                    self.progress_only(ctx, 1)
                    continue

                if (err := self.scan_tab(ctx, c)) is not None:
                    return err

            ctx.add_buf(c)
            ctx.add_origin_buf(c)
            self.progress_column(ctx, 1)

        self.add_buffered_token_if_exists(ctx)
        return None

    # init prepares the scanner s to tokenize the text src by setting the scanner at the beginning of src.
    def init(self, text: str) -> None:
        src = text
        self.source = list(src)
        self.source_pos = 0
        self.source_size = len(src)
        self.line = 1
        self.column = 1
        self.offset = 1
        self.is_first_char_at_line = True
        self.clear_state()

    def clear_state(self) -> None:
        self.prev_line_indent_num = 0
        self.last_delim_column = 0
        self.indent_level = 0
        self.indent_num = 0

    # scan scans the next token and returns the token collection. The source end is indicated by io.EOF.
    def scan(self) -> ta.Tuple[ta.Optional[YamlTokens], ta.Optional[YamlError]]:
        if self.source_pos >= self.source_size:
            return None, EofYamlError()

        ctx = YamlScanningContext.new(self.source[self.source_pos:])

        lst = YamlTokens()
        err = self._scan(ctx)
        lst.extend(ctx.tokens)

        if err is not None:
            # var invalidTokenErr *InvalidTokenError
            # if errors.As(err, &invalidTokenErr):
            #     lst = append(lst, invalidTokenErr.Token)
            return lst, err

        return lst, None


# Tokenize split to token instances from string
def yaml_tokenize(src: str) -> YamlTokens:
    s = YamlScanner()
    s.init(src)

    tks = YamlTokens()
    while True:
        sub_tokens, err = s.scan()
        if isinstance(err, EofYamlError):
            break

        tks.add(*check.not_none(sub_tokens))

    return tks


##


def _yaml_hex_to_int(s: str) -> int:
    if len(s) != 1:
        raise ValueError(s)
    b = s[0]
    if 'A' <= b <= 'F':
        return ord(b) - ord('A') + 10
    if 'a' <= b <= 'f':
        return ord(b) - ord('a') + 10
    return ord(b) - ord('0')


def _yaml_hex_runes_to_int(b: ta.List[str]) -> int:
    n = 0
    for i in range(len(b)):
        n += _yaml_hex_to_int(b[i]) << ((len(b) - i - 1) * 4)
    return n


def _yaml_trim_right_func(s: str, predicate: ta.Callable[[str], bool]) -> str:
    if not s:
        return s

    i = len(s) - 1
    while i >= 0 and predicate(s[i]):
        i -= 1

    return s[:i + 1]


########################################
# ../../../omlish/http/coro/server/server.py
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
"""
"Test suite" lol:

curl -v localhost:8000
curl -v localhost:8000 -d 'foo'
curl -v -XFOO localhost:8000 -d 'foo'
curl -v -XPOST -H 'Expect: 100-Continue' localhost:8000 -d 'foo'

curl -v -0 localhost:8000
curl -v -0 localhost:8000 -d 'foo'
curl -v -0 -XFOO localhost:8000 -d 'foo'

curl -v -XPOST localhost:8000 -d 'foo' --next -XPOST localhost:8000 -d 'bar'
curl -v -XPOST localhost:8000 -d 'foo' --next -XFOO localhost:8000 -d 'bar'
curl -v -XFOO localhost:8000 -d 'foo' --next -XPOST localhost:8000 -d 'bar'
curl -v -XFOO localhost:8000 -d 'foo' --next -XFOO localhost:8000 -d 'bar'
"""


##


class CoroHttpServer:
    """
    Adapted from stdlib:
     - https://github.com/python/cpython/blob/4b4e0dbdf49adc91c35a357ad332ab3abd4c31b1/Lib/http/server.py#L146
    """

    #

    def __init__(
            self,
            client_address: SocketAddress,
            *,
            handler: HttpHandler,
            parser: HttpParser = HttpParser(),

            default_content_type: ta.Optional[str] = None,

            error_message_format: ta.Optional[str] = None,
            error_content_type: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._client_address = client_address

        self._handler = handler
        self._parser = parser

        self._default_content_type = default_content_type or self.DEFAULT_CONTENT_TYPE

        self._error_message_format = error_message_format or self.DEFAULT_ERROR_MESSAGE
        self._error_content_type = error_content_type or self.DEFAULT_ERROR_CONTENT_TYPE

    #

    @property
    def client_address(self) -> SocketAddress:
        return self._client_address

    @property
    def handler(self) -> HttpHandler:
        return self._handler

    #

    def _format_timestamp(self, timestamp: ta.Optional[float] = None) -> str:
        if timestamp is None:
            timestamp = time.time()
        return email.utils.formatdate(timestamp, usegmt=True)

    #

    def _header_encode(self, s: str) -> bytes:
        return s.encode('latin-1', 'strict')

    class _Header(ta.NamedTuple):
        key: str
        value: str

    def _format_header_line(self, h: _Header) -> str:
        return f'{h.key}: {h.value}\r\n'

    def _get_header_close_connection_action(self, h: _Header) -> ta.Optional[bool]:
        if h.key.lower() != 'connection':
            return None
        elif h.value.lower() == 'close':
            return True
        elif h.value.lower() == 'keep-alive':
            return False
        else:
            return None

    def _make_default_headers(self) -> ta.List[_Header]:
        return [
            self._Header('Date', self._format_timestamp()),
        ]

    #

    _STATUS_RESPONSES: ta.Mapping[int, ta.Tuple[str, str]] = {
        v: (v.phrase, v.description)
        for v in http.HTTPStatus.__members__.values()
    }

    def _format_status_line(
            self,
            version: HttpVersion,
            code: ta.Union[http.HTTPStatus, int],
            message: ta.Optional[str] = None,
    ) -> str:
        if message is None:
            if code in self._STATUS_RESPONSES:
                message = self._STATUS_RESPONSES[code][0]
            else:
                message = ''

        return f'{version} {int(code)} {message}\r\n'

    #

    @dc.dataclass(frozen=True)
    class _Response:
        version: HttpVersion
        code: http.HTTPStatus

        message: ta.Optional[str] = None
        headers: ta.Optional[ta.Sequence['CoroHttpServer._Header']] = None
        data: ta.Optional[HttpHandlerResponseData] = None
        close_connection: ta.Optional[bool] = False

        def get_header(self, key: str) -> ta.Optional['CoroHttpServer._Header']:
            for h in self.headers or []:
                if h.key.lower() == key.lower():
                    return h
            return None

        def close(self) -> None:
            if isinstance(d := self.data, HttpHandlerResponseStreamedData):
                d.close()

    #

    def _build_response_head_bytes(self, a: _Response) -> bytes:
        out = io.BytesIO()

        if a.version >= HttpVersions.HTTP_1_0:
            out.write(self._header_encode(self._format_status_line(
                a.version,
                a.code,
                a.message,
            )))

            for h in a.headers or []:
                out.write(self._header_encode(self._format_header_line(h)))

            out.write(b'\r\n')

        return out.getvalue()

    def _yield_response_data(self, a: _Response) -> ta.Iterator[bytes]:
        if a.data is None:
            return

        elif isinstance(a.data, bytes):
            yield a.data
            return

        elif isinstance(a.data, HttpHandlerResponseStreamedData):
            yield from a.data.iter

        else:
            raise TypeError(a.data)

    #

    DEFAULT_CONTENT_TYPE = 'text/plain'

    def _preprocess_response(self, resp: _Response) -> _Response:
        nh: ta.List[CoroHttpServer._Header] = []
        kw: ta.Dict[str, ta.Any] = {}

        if resp.get_header('Content-Type') is None:
            nh.append(self._Header('Content-Type', self._default_content_type))

        if resp.data is not None and resp.get_header('Content-Length') is None:
            cl: ta.Optional[int]
            if isinstance(resp.data, bytes):
                cl = len(resp.data)
            elif isinstance(resp.data, HttpHandlerResponseStreamedData):
                cl = resp.data.length
            else:
                raise TypeError(resp.data)
            if cl is not None:
                nh.append(self._Header('Content-Length', str(cl)))

        if nh:
            kw.update(headers=[*(resp.headers or []), *nh])

        if (clh := resp.get_header('Connection')) is not None:
            if self._get_header_close_connection_action(clh):
                kw.update(close_connection=True)

        if not kw:
            return resp
        return dc.replace(resp, **kw)

    #

    @dc.dataclass(frozen=True)
    class Error:
        version: HttpVersion
        code: http.HTTPStatus
        message: str
        explain: str

        method: ta.Optional[str] = None

    def _build_error(
            self,
            code: ta.Union[http.HTTPStatus, int],
            message: ta.Optional[str] = None,
            explain: ta.Optional[str] = None,
            *,
            version: ta.Optional[HttpVersion] = None,
            method: ta.Optional[str] = None,
    ) -> Error:
        code = http.HTTPStatus(code)

        try:
            short_msg, long_msg = self._STATUS_RESPONSES[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg
        if explain is None:
            explain = long_msg

        if version is None:
            version = HttpVersions.HTTP_1_1

        return self.Error(
            version=version,
            code=code,
            message=message,
            explain=explain,

            method=method,
        )

    #

    DEFAULT_ERROR_MESSAGE = textwrap.dedent("""\
        <!DOCTYPE HTML>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Error response</title>
            </head>
            <body>
                <h1>Error response</h1>
                <p>Error code: %(code)d</p>
                <p>Message: %(message)s.</p>
                <p>Error code explanation: %(code)s - %(explain)s.</p>
            </body>
        </html>
    """)

    DEFAULT_ERROR_CONTENT_TYPE = 'text/html;charset=utf-8'

    def _build_error_response(self, err: Error) -> _Response:
        headers: ta.List[CoroHttpServer._Header] = [
            *self._make_default_headers(),
            self._Header('Connection', 'close'),
        ]

        # Message body is omitted for cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        data: ta.Optional[bytes] = None
        if (
                err.code >= http.HTTPStatus.OK and
                err.code not in (
                    http.HTTPStatus.NO_CONTENT,
                    http.HTTPStatus.RESET_CONTENT,
                    http.HTTPStatus.NOT_MODIFIED,
                )
        ):
            # HTML encode to prevent Cross Site Scripting attacks (see bug #1100201)
            content = self._error_message_format.format(
                code=err.code,
                message=html.escape(err.message, quote=False),
                explain=html.escape(err.explain, quote=False),
            )
            body = content.encode('UTF-8', 'replace')

            headers.extend([
                self._Header('Content-Type', self._error_content_type),
                self._Header('Content-Length', str(len(body))),
            ])

            if err.method != 'HEAD' and body:
                data = body

        return self._Response(
            version=err.version,
            code=err.code,
            message=err.message,
            headers=headers,
            data=data,
            close_connection=True,
        )

    #

    @dc.dataclass(frozen=True)
    class ParsedRequestLogIo(CoroHttpIo.AnyLogIo):
        request: ParsedHttpMessage

    @dc.dataclass(frozen=True)
    class ErrorLogIo(CoroHttpIo.AnyLogIo):
        error: 'CoroHttpServer.Error'

    #

    @dc.dataclass(frozen=True)
    class CoroHandleResult:
        close_reason: ta.Literal['response', 'internal', None] = None

    def coro_handle(self) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], CoroHandleResult]:
        return self._coro_run_handler(self._coro_handle_one())

    class Close(Exception):  # noqa
        pass

    def _coro_run_handler(
            self,
            gen: ta.Generator[
                ta.Union[CoroHttpIo.AnyLogIo, CoroHttpIo.AnyReadIo, _Response],
                ta.Optional[bytes],
                None,
            ],
    ) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], CoroHandleResult]:
        i: ta.Optional[bytes]
        o: ta.Any = next(gen)
        while True:
            try:
                if isinstance(o, CoroHttpIo.AnyLogIo):
                    i = None
                    yield o

                elif isinstance(o, CoroHttpIo.AnyReadIo):
                    i = check.isinstance((yield o), bytes)

                elif isinstance(o, self._Response):
                    i = None

                    r = self._preprocess_response(o)
                    hb = self._build_response_head_bytes(r)
                    check.none((yield CoroHttpIo.WriteIo(hb)))

                    for b in self._yield_response_data(r):
                        yield CoroHttpIo.WriteIo(b)

                    o.close()
                    if o.close_connection:
                        return self.CoroHandleResult(
                            close_reason='response',
                        )
                    o = None

                else:
                    raise TypeError(o)  # noqa

                try:
                    o = gen.send(i)
                except self.Close:
                    return self.CoroHandleResult(
                        close_reason='internal',
                    )
                except StopIteration:
                    return self.CoroHandleResult()

            except Exception:  # noqa
                if hasattr(o, 'close'):
                    o.close()

                raise

    def _coro_handle_one(self) -> ta.Generator[
        ta.Union[CoroHttpIo.AnyLogIo, CoroHttpIo.AnyReadIo, _Response],
        ta.Optional[bytes],
        None,
    ]:
        # Parse request

        head = check.not_none((yield CoroHttpIo.ReadUntilIo(b'\r\n\r\n')))

        try:
            o: ta.Any = self._parser.parse_message(head)
        except HttpParseError as e:
            o = e

        # FIXME:
        # if isinstance(parsed, EmptyParsedHttpResult):
        #     raise self.Close

        if isinstance(o, HttpParseError):
            err = self._build_error(
                400,  # FIXME: parsed.code,
                # FIXME: *([parsed.message] if isinstance(parsed.message, str) else parsed.message),
                f'Bad request ({o!r})',
                version=HttpVersions.HTTP_1_1,  # FIXME: version=parsed.version,
            )
            yield self.ErrorLogIo(err)
            yield self._build_error_response(err)
            return

        parsed = check.isinstance(o, ParsedHttpMessage)

        # Log

        check.none((yield self.ParsedRequestLogIo(parsed)))

        # Handle CONTINUE

        if parsed.prepared.expect_100_continue:
            # https://bugs.python.org/issue1491
            # https://github.com/python/cpython/commit/0f476d49f8d4aa84210392bf13b59afc67b32b31
            yield self._Response(
                version=parsed.request_line.http_version if parsed.request_line else HttpVersions.HTTP_1_1,
                code=http.HTTPStatus.CONTINUE,
            )

        # Read data

        request_data: ta.Optional[bytes]
        if (cl := parsed.headers.get('Content-Length')) is not None:
            request_data = check.isinstance((yield CoroHttpIo.ReadIo(int(cl))), bytes)
        else:
            request_data = None

        # Build request

        handler_request = HttpHandlerRequest(
            client_address=self._client_address,
            method=check.not_none(parsed.request_line).method,
            path=check.not_none(parsed.request_line).request_target.decode('ascii'),  # FIXME: lol
            headers=parsed.headers,
            data=request_data,
        )

        # Build handler response

        try:
            handler_response = self._handler(handler_request)

        except UnsupportedMethodHttpHandlerError:
            err = self._build_error(
                http.HTTPStatus.NOT_IMPLEMENTED,
                f'Unsupported method ({(parsed.request_line.method if parsed.request_line else "?")!r})',
                version=parsed.request_line.http_version if parsed.request_line else HttpVersions.HTTP_1_1,
                method=parsed.request_line.method if parsed.request_line else None,
            )
            yield self.ErrorLogIo(err)
            yield self._build_error_response(err)
            return

        try:
            # Build internal response

            response_headers = handler_response.headers or {}
            response_data = handler_response.data

            headers: ta.List[CoroHttpServer._Header] = [
                *self._make_default_headers(),
            ]

            for k, v in response_headers.items():
                headers.append(self._Header(k, v))

            if handler_response.close_connection and 'Connection' not in headers:
                headers.append(self._Header('Connection', 'close'))

            yield self._Response(
                version=parsed.request_line.http_version if parsed.request_line else HttpVersions.HTTP_1_1,
                code=http.HTTPStatus(handler_response.status),
                headers=headers,
                data=response_data,
                close_connection=handler_response.close_connection,
            )

        except Exception:  # noqa
            handler_response.close()

            raise


########################################
# ../../../omlish/logs/base.py


##


class AnyLogger(AnyLoggerMetricCollector[T], Abstract, ta.Generic[T]):
    def is_enabled_for(self, level: LogLevel) -> bool:
        return level >= self.get_effective_level()

    @abc.abstractmethod
    def get_effective_level(self) -> LogLevel:
        raise NotImplementedError

    #

    @ta.final
    def isEnabledFor(self, level: LogLevel) -> bool:  # noqa
        return self.is_enabled_for(level)

    @ta.final
    def getEffectiveLevel(self) -> LogLevel:  # noqa
        return self.get_effective_level()

    ##

    # This will be 1 for [Sync]Logger and 0 for AsyncLogger - in sync loggers these methods remain present on the stack,
    # in async loggers they return a coroutine to be awaited and thus aren't actually present when said coroutine is
    # awaited.
    _level_proxy_method_stack_offset: int

    @ta.overload
    def log(self, level: LogLevel, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def log(self, level: LogLevel, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def log(self, level: LogLevel, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def log(self, level: LogLevel, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                level,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def debug(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def debug(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def debug(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def debug(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.DEBUG,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def info(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def info(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def info(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def info(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.INFO,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def warning(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def warning(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def warning(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def warning(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.WARNING,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def error(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def error(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def error(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def error(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.ERROR,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def exception(self, exc: BaseException, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, *, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, msg: str, *args: ta.Any, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, msg: ta.Tuple[ta.Any, ...], *, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def exception(self, msg_fn: LoggingMsgFn, *, exc_info: LoggingExcInfoArg = True, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def exception(self, *args, exc_info=True, **kwargs):
        if not args:
            if not exc_info:
                raise TypeError('exc_info=False is not allowed when no args are passed')
            args = ((),)
        elif len(args) == 1:
            if isinstance(arg0 := args[0], BaseException):
                if exc_info is not True:  # noqa
                    raise TypeError(f'exc_info={exc_info!r} is not allowed when exc={arg0!r} is passed')
            args, exc_info = ((),), arg0

        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.ERROR,
                exc_info=exc_info,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @ta.overload
    def critical(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def critical(self, msg: ta.Tuple[ta.Any, ...], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def critical(self, msg_fn: LoggingMsgFn, **kwargs: ta.Any) -> T:
        ...

    @ta.final
    def critical(self, *args, **kwargs):
        return self._log(
            CaptureLoggingContextImpl(
                NamedLogLevel.CRITICAL,
                stack_offset=self._level_proxy_method_stack_offset,
            ),
            *args,
            **kwargs,
        )

    #

    @abc.abstractmethod
    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> T:
        raise NotImplementedError


class Logger(LoggerMetricCollector, AnyLogger[None], Abstract):
    _level_proxy_method_stack_offset: int = 1

    @abc.abstractmethod
    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> None:
        raise NotImplementedError


class AsyncLogger(AsyncLoggerMetricCollector, AnyLogger[ta.Awaitable[None]], Abstract):
    _level_proxy_method_stack_offset: int = 0

    @abc.abstractmethod
    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> ta.Awaitable[None]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def _metric(self, m: LoggerMetric) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class AnyNopLogger(AnyNopLoggerMetricCollector[T], AnyLogger[T], Abstract):
    @ta.final
    def get_effective_level(self) -> LogLevel:
        return -999


class NopLogger(NopLoggerMetricCollector, AnyNopLogger[None], Logger):
    @ta.final
    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        pass


class AsyncNopLogger(AsyncNopLoggerMetricCollector, AnyNopLogger[ta.Awaitable[None]], AsyncLogger):
    @ta.final
    async def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        pass


########################################
# ../../../omlish/logs/std/records.py
"""
TODO:
 - TypedDict?
"""


##


class LoggingContextInfoRecordAdapters:
    # Ref:
    #  - https://docs.python.org/3/library/logging.html#logrecord-attributes
    #
    # LogRecord:
    #  - https://github.com/python/cpython/blob/39b2f82717a69dde7212bc39b673b0f55c99e6a3/Lib/logging/__init__.py#L276 (3.8)  # noqa
    #  - https://github.com/python/cpython/blob/f070f54c5f4a42c7c61d1d5d3b8f3b7203b4a0fb/Lib/logging/__init__.py#L286 (~3.14)  # noqa
    #

    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    class Adapter(Abstract, ta.Generic[T]):
        @property
        @abc.abstractmethod
        def info_cls(self) -> ta.Type[LoggingContextInfo]:
            raise NotImplementedError

        #

        @ta.final
        class NOT_SET:  # noqa
            def __new__(cls, *args, **kwargs):  # noqa
                raise TypeError

        class RecordAttr(ta.NamedTuple):
            name: str
            type: ta.Any
            default: ta.Any

        # @abc.abstractmethod
        record_attrs: ta.ClassVar[ta.Mapping[str, RecordAttr]]

        @property
        @abc.abstractmethod
        def _record_attrs(self) -> ta.Union[
            ta.Mapping[str, ta.Any],
            ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]],
        ]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[T]:
            raise NotImplementedError

        #

        def __init_subclass__(cls, **kwargs: ta.Any) -> None:
            super().__init_subclass__(**kwargs)

            if Abstract in cls.__bases__:
                return

            if 'record_attrs' in cls.__dict__:
                raise TypeError(cls)
            if not isinstance(ra := cls.__dict__['_record_attrs'], collections.abc.Mapping):
                raise TypeError(ra)

            rd: ta.Dict[str, LoggingContextInfoRecordAdapters.Adapter.RecordAttr] = {}
            for n, v in ra.items():
                if not n or not isinstance(n, str) or n in rd:
                    raise AttributeError(n)
                if isinstance(v, tuple):
                    t, d = v
                else:
                    t, d = v, cls.NOT_SET
                rd[n] = cls.RecordAttr(
                    name=n,
                    type=t,
                    default=d,
                )
            cls.record_attrs = rd

    class RequiredAdapter(Adapter[T], Abstract):
        @property
        @abc.abstractmethod
        def _record_attrs(self) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        @ta.final
        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            if (info := ctx.get_info(self.info_cls)) is not None:
                return self._info_to_record(info)
            else:
                raise TypeError  # FIXME: fallback?

        @abc.abstractmethod
        def _info_to_record(self, info: T) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def record_to_info(self, rec: logging.LogRecord) -> T:
            raise NotImplementedError

        #

        def __init_subclass__(cls, **kwargs: ta.Any) -> None:
            super().__init_subclass__(**kwargs)

            if any(a.default is not cls.NOT_SET for a in cls.record_attrs.values()):
                raise TypeError(cls.record_attrs)

    class OptionalAdapter(Adapter[T], Abstract, ta.Generic[T]):
        @property
        @abc.abstractmethod
        def _record_attrs(self) -> ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]:
            raise NotImplementedError

        record_defaults: ta.ClassVar[ta.Mapping[str, ta.Any]]

        #

        @ta.final
        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            if (info := ctx.get_info(self.info_cls)) is not None:
                return self._info_to_record(info)
            else:
                return self.record_defaults

        @abc.abstractmethod
        def _info_to_record(self, info: T) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        #

        def __init_subclass__(cls, **kwargs: ta.Any) -> None:
            super().__init_subclass__(**kwargs)

            dd: ta.Dict[str, ta.Any] = {a.name: a.default for a in cls.record_attrs.values()}
            if any(d is cls.NOT_SET for d in dd.values()):
                raise TypeError(cls.record_attrs)
            cls.record_defaults = dd

    #

    class Name(RequiredAdapter[LoggingContextInfos.Name]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Name]] = LoggingContextInfos.Name

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Name of the logger used to log the call. Unmodified by ctor.
            name=str,
        )

        def _info_to_record(self, info: LoggingContextInfos.Name) -> ta.Mapping[str, ta.Any]:
            return dict(
                name=info.name,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Name:
            return LoggingContextInfos.Name(
                name=rec.name,
            )

    class Level(RequiredAdapter[LoggingContextInfos.Level]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Level]] = LoggingContextInfos.Level

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). Set to
            # `getLevelName(level)`.
            levelname=str,

            # Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL). Unmodified by ctor.
            levelno=int,
        )

        def _info_to_record(self, info: LoggingContextInfos.Level) -> ta.Mapping[str, ta.Any]:
            return dict(
                levelname=info.name,
                levelno=int(info.level),
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Level:
            return LoggingContextInfos.Level.build(rec.levelno)

    class Msg(RequiredAdapter[LoggingContextInfos.Msg]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Msg]] = LoggingContextInfos.Msg

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # The format string passed in the original logging call. Merged with args to produce message, or an
            # arbitrary object (see Using arbitrary objects as messages). Unmodified by ctor.
            msg=str,

            # The tuple of arguments merged into msg to produce message, or a dict whose values are used for the merge
            # (when there is only one argument, and it is a dictionary). Ctor will transform a 1-tuple containing a
            # Mapping into just the mapping, but is otherwise unmodified.
            args=ta.Union[tuple, dict, None],
        )

        def _info_to_record(self, info: LoggingContextInfos.Msg) -> ta.Mapping[str, ta.Any]:
            return dict(
                msg=info.msg,
                args=info.args,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Msg:
            return LoggingContextInfos.Msg(
                msg=rec.msg,
                args=rec.args,
            )

    class Time(RequiredAdapter[LoggingContextInfos.Time]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Time]] = LoggingContextInfos.Time

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Time when the LogRecord was created. Set to `time.time_ns() / 1e9` for >=3.13.0b1, otherwise simply
            # `time.time()`.
            #
            # See:
            #  - https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
            #  - https://github.com/python/cpython/commit/1500a23f33f5a6d052ff1ef6383d9839928b8ff1
            #
            created=float,

            # Millisecond portion of the time when the LogRecord was created.
            msecs=float,

            # Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.
            relativeCreated=float,
        )

        def _info_to_record(self, info: LoggingContextInfos.Time) -> ta.Mapping[str, ta.Any]:
            return dict(
                created=info.secs,
                msecs=info.msecs,
                relativeCreated=info.relative_secs,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Time:
            return LoggingContextInfos.Time.build(
                int(rec.created * 1e9),
            )

    class Exc(OptionalAdapter[LoggingContextInfos.Exc]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Exc]] = LoggingContextInfos.Exc

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Exception tuple (à la sys.exc_info) or, if no exception has occurred, None. Unmodified by ctor.
            exc_info=(ta.Optional[LoggingExcInfoTuple], None),

            # Used to cache the traceback text. Simply set to None by ctor, later set by Formatter.format.
            exc_text=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Exc) -> ta.Mapping[str, ta.Any]:
            return dict(
                exc_info=info.info_tuple,
                exc_text=None,
            )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Exc]:
            # FIXME:
            # error: Argument 1 to "build" of "Exc" has incompatible type
            # "tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None] | None"; expected  # noqa
            # "BaseException | tuple[type[BaseException], BaseException, TracebackType | None] | bool | None"  [arg-type]  # noqa
            return LoggingContextInfos.Exc.build(rec.exc_info)  # type: ignore[arg-type]

    class Caller(OptionalAdapter[LoggingContextInfos.Caller]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Caller]] = LoggingContextInfos.Caller

        _UNKNOWN_PATH_NAME: ta.ClassVar[str] = '(unknown file)'
        _UNKNOWN_FUNC_NAME: ta.ClassVar[str] = '(unknown function)'

        _STACK_INFO_PREFIX: ta.ClassVar[str] = 'Stack (most recent call last):\n'

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Full pathname of the source file where the logging call was issued (if available). Unmodified by ctor. May
            # default to "(unknown file)" by Logger.findCaller / Logger._log.
            pathname=(str, _UNKNOWN_PATH_NAME),

            # Source line number where the logging call was issued (if available). Unmodified by ctor. May default to 0
            # by Logger.findCaller / Logger._log.
            lineno=(int, 0),

            # Name of function containing the logging call. Set by ctor to `func` arg, unmodified. May default to
            # "(unknown function)" by Logger.findCaller / Logger._log.
            funcName=(str, _UNKNOWN_FUNC_NAME),

            # Stack frame information (where available) from the bottom of the stack in the current thread, up to and
            # including the stack frame of the logging call which resulted in the creation of this record. Set by ctor
            # to `sinfo` arg, unmodified. Mostly set, if requested, by `Logger.findCaller`, to
            # `traceback.print_stack(f)`, but prepended with the literal "Stack (most recent call last):\n", and
            # stripped of exactly one trailing `\n` if present.
            stack_info=(ta.Optional[str], None),
        )

        def _info_to_record(self, caller: LoggingContextInfos.Caller) -> ta.Mapping[str, ta.Any]:
            if (sinfo := caller.stack_info) is not None:
                stack_info: ta.Optional[str] = '\n'.join([
                    self._STACK_INFO_PREFIX,
                    sinfo[1:] if sinfo.endswith('\n') else sinfo,
                ])
            else:
                stack_info = None

            return dict(
                pathname=caller.file_path,

                lineno=caller.line_no,
                funcName=caller.func_name,

                stack_info=stack_info,
            )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Caller]:
            # FIXME: piecemeal?
            if (
                    rec.pathname != self._UNKNOWN_PATH_NAME and
                    rec.lineno != 0 and
                    rec.funcName != self._UNKNOWN_FUNC_NAME
            ):
                if (sinfo := rec.stack_info) is not None and sinfo.startswith(self._STACK_INFO_PREFIX):
                    sinfo = sinfo[len(self._STACK_INFO_PREFIX):]
                return LoggingContextInfos.Caller(
                    file_path=rec.pathname,

                    line_no=rec.lineno,
                    func_name=rec.funcName,

                    stack_info=sinfo,
                )

            return None

    class SourceFile(Adapter[LoggingContextInfos.SourceFile]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.SourceFile]] = LoggingContextInfos.SourceFile

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Any]] = dict(
            # Filename portion of pathname. Set to `os.path.basename(pathname)` if successful, otherwise defaults to
            # pathname.
            filename=str,

            # Module (name portion of filename). Set to `os.path.splitext(filename)[0]`, otherwise defaults to
            # "Unknown module".
            module=str,
        )

        _UNKNOWN_MODULE: ta.ClassVar[str] = 'Unknown module'

        def context_to_record(self, ctx: LoggingContext) -> ta.Mapping[str, ta.Any]:
            if (info := ctx.get_info(LoggingContextInfos.SourceFile)) is not None:
                return dict(
                    filename=info.file_name,
                    module=info.module,
                )

            if (caller := ctx.get_info(LoggingContextInfos.Caller)) is not None:
                return dict(
                    filename=caller.file_path,
                    module=self._UNKNOWN_MODULE,
                )

            return dict(
                filename=LoggingContextInfoRecordAdapters.Caller._UNKNOWN_PATH_NAME,  # noqa
                module=self._UNKNOWN_MODULE,
            )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.SourceFile]:
            if (
                    rec.module is not None and
                    rec.module != self._UNKNOWN_MODULE
            ):
                return LoggingContextInfos.SourceFile(
                    file_name=rec.filename,
                    module=rec.module,  # FIXME: piecemeal?
                )

            return None

    class Thread(OptionalAdapter[LoggingContextInfos.Thread]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Thread]] = LoggingContextInfos.Thread

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Thread ID if available, and `logging.logThreads` is truthy.
            thread=(ta.Optional[int], None),

            # Thread name if available, and `logging.logThreads` is truthy.
            threadName=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Thread) -> ta.Mapping[str, ta.Any]:
            if logging.logThreads:
                return dict(
                    thread=info.ident,
                    threadName=info.name,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Thread]:
            if (
                    (ident := rec.thread) is not None and
                    (name := rec.threadName) is not None
            ):
                return LoggingContextInfos.Thread(
                    ident=ident,
                    native_id=None,
                    name=name,
                )

            return None

    class Process(OptionalAdapter[LoggingContextInfos.Process]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Process]] = LoggingContextInfos.Process

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Process ID if available - that is, if `hasattr(os, 'getpid')` - and `logging.logProcesses` is truthy,
            # otherwise None.
            process=(ta.Optional[int], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Process) -> ta.Mapping[str, ta.Any]:
            if logging.logProcesses:
                return dict(
                    process=info.pid,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Process]:
            if (
                    (pid := rec.process) is not None
            ):
                return LoggingContextInfos.Process(
                    pid=pid,
                )

            return None

    class Multiprocessing(OptionalAdapter[LoggingContextInfos.Multiprocessing]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.Multiprocessing]] = LoggingContextInfos.Multiprocessing

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Tuple[ta.Any, ta.Any]]] = dict(
            # Process name if available. Set to None if `logging.logMultiprocessing` is not truthy. Otherwise, set to
            # 'MainProcess', then `sys.modules.get('multiprocessing').current_process().name` if that works, otherwise
            # remains as 'MainProcess'.
            #
            # As noted by stdlib:
            #
            #   Errors may occur if multiprocessing has not finished loading yet - e.g. if a custom import hook causes
            #   third-party code to run when multiprocessing calls import. See issue 8200 for an example
            #
            processName=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.Multiprocessing) -> ta.Mapping[str, ta.Any]:
            if logging.logMultiprocessing:
                return dict(
                    processName=info.process_name,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Multiprocessing]:
            if (
                    (process_name := rec.processName) is not None
            ):
                return LoggingContextInfos.Multiprocessing(
                    process_name=process_name,
                )

            return None

    class AsyncioTask(OptionalAdapter[LoggingContextInfos.AsyncioTask]):
        info_cls: ta.ClassVar[ta.Type[LoggingContextInfos.AsyncioTask]] = LoggingContextInfos.AsyncioTask

        _record_attrs: ta.ClassVar[ta.Mapping[str, ta.Union[ta.Any, ta.Tuple[ta.Any, ta.Any]]]] = dict(
            # Absent <3.12, otherwise asyncio.Task name if available, and `logging.logAsyncioTasks` is truthy. Set to
            # `sys.modules.get('asyncio').current_task().get_name()`, otherwise None.
            taskName=(ta.Optional[str], None),
        )

        def _info_to_record(self, info: LoggingContextInfos.AsyncioTask) -> ta.Mapping[str, ta.Any]:
            if getattr(logging, 'logAsyncioTasks', None):  # Absent <3.12
                return dict(
                    taskName=info.name,
                )

            return self.record_defaults

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.AsyncioTask]:
            if (
                    (name := getattr(rec, 'taskName', None)) is not None
            ):
                return LoggingContextInfos.AsyncioTask(
                    name=name,
                )

            return None


_LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_: ta.Sequence[LoggingContextInfoRecordAdapters.Adapter] = [  # noqa
    LoggingContextInfoRecordAdapters.Name(),
    LoggingContextInfoRecordAdapters.Level(),
    LoggingContextInfoRecordAdapters.Msg(),
    LoggingContextInfoRecordAdapters.Time(),
    LoggingContextInfoRecordAdapters.Exc(),
    LoggingContextInfoRecordAdapters.Caller(),
    LoggingContextInfoRecordAdapters.SourceFile(),
    LoggingContextInfoRecordAdapters.Thread(),
    LoggingContextInfoRecordAdapters.Process(),
    LoggingContextInfoRecordAdapters.Multiprocessing(),
    LoggingContextInfoRecordAdapters.AsyncioTask(),
]

_LOGGING_CONTEXT_INFO_RECORD_ADAPTERS: ta.Mapping[ta.Type[LoggingContextInfo], LoggingContextInfoRecordAdapters.Adapter] = {  # noqa
    ad.info_cls: ad for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_
}


##


# Formatter:
#  - https://github.com/python/cpython/blob/39b2f82717a69dde7212bc39b673b0f55c99e6a3/Lib/logging/__init__.py#L514 (3.8)
#  - https://github.com/python/cpython/blob/f070f54c5f4a42c7c61d1d5d3b8f3b7203b4a0fb/Lib/logging/__init__.py#L554 (~3.14)  # noqa
#
_KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTRS: ta.Dict[str, ta.Any] = dict(
    # The logged message, computed as msg % args. Set to `record.getMessage()`.
    message=str,

    # Human-readable time when the LogRecord was created. By default this is of the form '2003-07-08 16:49:45,896' (the
    # numbers after the comma are millisecond portion of the time). Set to `self.formatTime(record, self.datefmt)` if
    # `self.usesTime()`, otherwise unset.
    asctime=str,

    # Used to cache the traceback text. If unset (falsey) on the record and `exc_info` is truthy, set to
    # `self.formatException(record.exc_info)` - otherwise unmodified.
    exc_text=ta.Optional[str],
)


##


_KNOWN_STD_LOGGING_RECORD_ATTR_SET: ta.FrozenSet[str] = frozenset(
    a for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS.values() for a in ad.record_attrs
)

_KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTR_SET: ta.FrozenSet[str] = frozenset(_KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTRS)


class UnknownStdLoggingRecordAttrsWarning(LoggingSetupWarning):
    pass


def _check_std_logging_record_attrs() -> None:
    if (
            len([a for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS.values() for a in ad.record_attrs]) !=
            len(_KNOWN_STD_LOGGING_RECORD_ATTR_SET)
    ):
        raise RuntimeError('Duplicate LoggingContextInfoRecordAdapter record attrs')

    rec_dct = dict(logging.makeLogRecord({}).__dict__)

    if (unk_rec_fields := frozenset(rec_dct) - _KNOWN_STD_LOGGING_RECORD_ATTR_SET):
        import warnings  # noqa

        warnings.warn(
            f'Unknown log record attrs detected: {sorted(unk_rec_fields)!r}',
            UnknownStdLoggingRecordAttrsWarning,
        )


_check_std_logging_record_attrs()


##


class LoggingContextLogRecord(logging.LogRecord):
    # LogRecord.__init__ args:
    #  - name: str
    #  - level: int
    #  - pathname: str - Confusingly referred to as `fn` before the LogRecord ctor. May be empty or "(unknown file)".
    #  - lineno: int - May be 0.
    #  - msg: str
    #  - args: tuple | dict | 1-tuple[dict]
    #  - exc_info: LoggingExcInfoTuple | None
    #  - func: str | None = None -> funcName
    #  - sinfo: str | None = None -> stack_info
    #

    def __init__(self, *, _logging_context: LoggingContext) -> None:  # noqa
        self.__dict__.update(_logging_context=_logging_context)

        for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_:
            self.__dict__.update(ad.context_to_record(_logging_context))

    _logging_context: LoggingContext

    # FIXME: track extra
    # def __setattr__(self, key, value):
    #     super().__setattr__(key, value)


##


@ta.final
class LogRecordLoggingContext(LoggingContext):
    def __init__(self, rec: logging.LogRecord) -> None:
        if isinstance(rec, LoggingContextLogRecord):
            raise TypeError(rec)

        self._rec = rec

        infos: ta.List[LoggingContextInfo] = [
            info
            for ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS_
            if (info := ad.record_to_info(rec)) is not None
        ]

        # FIXME:
        # if extra is not None:
        #     for key in extra:
        #         if (key in ["message", "asctime"]) or (key in rv.__dict__):
        #             raise KeyError("Attempt to overwrite %r in LogRecord" % key)
        #         rv.__dict__[key] = extra[key]

        if (extra := {
            a: v
            for a, v in rec.__dict__.items()
            if a not in _KNOWN_STD_LOGGING_RECORD_ATTR_SET
        }):
            infos.append(LoggingContextInfos.Extra(extra))

        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {
            type(info): info
            for info in infos
        }

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)


########################################
# ../../../omlish/secrets/tempssl.py


##


class TempSslCert(ta.NamedTuple):
    cert: SslCert
    temp_dir: str


@dc.dataclass(frozen=True)
class TempSslCertGenerator(SubprocessRunnable[TempSslCert]):
    @cached_nullary
    def temp_dir(self) -> str:
        return tempfile.mkdtemp()

    @cached_nullary
    def make_run(self) -> SubprocessRun:
        return SubprocessRun.of(
            'openssl',
            'req',
            '-x509',
            '-newkey', 'rsa:2048',

            '-keyout', 'key.pem',
            '-out', 'cert.pem',

            '-days', '365',

            '-nodes',

            '-subj', '/CN=localhost',
            '-addext', 'subjectAltName = DNS:localhost,IP:127.0.0.1',

            cwd=self.temp_dir(),
            capture_output=True,
            check=False,
        )

    def handle_run_output(self, proc: SubprocessRunOutput) -> TempSslCert:
        if proc.returncode:
            raise RuntimeError(f'Failed to generate temp ssl cert: {proc.stderr=}')

        key_file = os.path.join(self.temp_dir(), 'key.pem')
        cert_file = os.path.join(self.temp_dir(), 'cert.pem')
        for file in [key_file, cert_file]:
            if not os.path.isfile(file):
                raise RuntimeError(f'Failed to generate temp ssl cert (file not found): {file}')

        return TempSslCert(
            SslCert(
                key_file=key_file,
                cert_file=cert_file,
            ),
            temp_dir=self.temp_dir(),
        )


def generate_temp_localhost_ssl_cert() -> TempSslCert:
    return TempSslCertGenerator().run()


########################################
# ../../../omlish/sockets/server/server.py


##


class SocketServer:
    _DEFAULT_LOGGER: LoggerLike = logging.getLogger('.'.join([__name__, 'SocketServer']))  # FIXME

    def __init__(
            self,
            binder: SocketBinder,
            handler: SocketServerHandler,
            *,
            on_error: ta.Optional[ta.Callable[[BaseException, ta.Optional[SocketAndAddress]], None]] = None,
            error_logger: ta.Optional[LoggerLike] = _DEFAULT_LOGGER,
            poll_interval: float = .5,
            shutdown_timeout: ta.Optional[float] = None,
    ) -> None:
        super().__init__()

        self._binder = binder
        self._handler = handler
        self._on_error = on_error
        self._error_logger = error_logger
        self._poll_interval = poll_interval
        self._shutdown_timeout = shutdown_timeout

        self._lock = threading.RLock()
        self._is_shutdown = threading.Event()
        self._should_shutdown = False

    @property
    def binder(self) -> SocketBinder:
        return self._binder

    @property
    def handler(self) -> SocketServerHandler:
        return self._handler

    #

    def _handle_error(self, exc: BaseException, conn: ta.Optional[SocketAndAddress] = None) -> None:
        if (error_logger := self._error_logger) is not None:
            error_logger.exception('Error in socket server: %r', conn)

        if (on_error := self._on_error) is not None:
            on_error(exc, conn)

    #

    class SelectorProtocol(ta.Protocol):
        def register(self, *args, **kwargs) -> None:
            raise NotImplementedError

        def select(self, *args, **kwargs) -> bool:
            raise NotImplementedError

    Selector: ta.ClassVar[ta.Any]
    if hasattr(selectors, 'PollSelector'):
        Selector = selectors.PollSelector
    else:
        Selector = selectors.SelectSelector

    #

    class PollResult(enum.Enum):
        TIMEOUT = enum.auto()
        CONNECTION = enum.auto()
        ERROR = enum.auto()
        SHUTDOWN = enum.auto()

    class PollContext(ExitStacked, Abstract):
        @abc.abstractmethod
        def poll(self, timeout: ta.Optional[float] = None) -> 'SocketServer.PollResult':
            raise NotImplementedError

    class _PollContext(PollContext):
        def __init__(self, server: 'SocketServer') -> None:
            super().__init__()

            self._server = server

        _selector: ta.Any = None

        def _enter_contexts(self) -> None:
            self._enter_context(self._server._lock)  # noqa: SLF001
            self._enter_context(self._server._binder)  # noqa: SLF001

            self._server._binder.listen()  # noqa: SLF001

            self._server._is_shutdown.clear()  # noqa: SLF001
            self._enter_context(defer(self._server._is_shutdown.set))  # noqa

            # XXX: Consider using another file descriptor or connecting to the socket to wake this up instead of
            # polling. Polling reduces our responsiveness to a shutdown request and wastes cpu at all other times.
            self._selector = self._enter_context(self._server.Selector())
            self._selector.register(self._server._binder.fileno(), selectors.EVENT_READ)  # noqa: SLF001

        def poll(self, timeout: ta.Optional[float] = None) -> 'SocketServer.PollResult':
            if self._server._should_shutdown:  # noqa: SLF001
                return SocketServer.PollResult.SHUTDOWN

            ready = self._selector.select(timeout)

            # bpo-35017: shutdown() called during select(), exit immediately.
            if self._server._should_shutdown:  # noqa: SLF001
                return SocketServer.PollResult.SHUTDOWN  # type: ignore[unreachable]

            if not ready:
                return SocketServer.PollResult.TIMEOUT

            try:
                conn = self._server._binder.accept()  # noqa: SLF001

            except OSError as exc:
                self._server._handle_error(exc)  # noqa: SLF001

                return SocketServer.PollResult.ERROR

            try:
                self._server._handler(conn)  # noqa: SLF001

            except Exception as exc:  # noqa
                self._server._handle_error(exc, conn)  # noqa: SLF001

                close_socket_immediately(conn.socket)

            return SocketServer.PollResult.CONNECTION

    def poll_context(self) -> PollContext:
        return self._PollContext(self)

    #

    @contextlib.contextmanager
    def loop_context(self, poll_interval: ta.Optional[float] = None) -> ta.Iterator[ta.Iterator[bool]]:
        if poll_interval is None:
            poll_interval = self._poll_interval

        with self.poll_context() as pc:
            def loop():
                while True:
                    res = pc.poll(poll_interval)
                    if res in (SocketServer.PollResult.ERROR, SocketServer.PollResult.SHUTDOWN):
                        return
                    else:
                        yield res == SocketServer.PollResult.CONNECTION

            yield loop()

    def run(self, poll_interval: ta.Optional[float] = None) -> None:
        with self.loop_context(poll_interval=poll_interval) as loop:
            for _ in loop:
                pass

    #

    class _NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def shutdown(
            self,
            block: bool = False,
            timeout: ta.Union[float, None, ta.Type[_NOT_SET]] = _NOT_SET,
    ) -> None:
        self._should_shutdown = True

        if block:
            if timeout is self._NOT_SET:
                timeout = self._shutdown_timeout

            if not self._is_shutdown.wait(timeout=timeout):  # type: ignore
                raise TimeoutError

    #

    def __enter__(self) -> 'SocketServer':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


########################################
# ../../../omlish/sockets/server/ssl.py


##


@dc.dataclass(frozen=True)
class SslErrorHandlingSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler

    log: ta.Optional[LoggerLike] = None

    #

    _error_cls: ta.ClassVar[ta.Optional[ta.Type[BaseException]]] = None

    @classmethod
    def _get_error_cls(cls) -> ta.Type[BaseException]:
        if (error_cls := cls._error_cls) is None:
            import ssl
            error_cls = cls._error_cls = ssl.SSLError
        return error_cls

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            self.handler(conn)
        except self._get_error_cls():  # noqa
            if (log := self.log) is not None:
                log.exception('SSL Error in connection %r', conn)
            close_socket_immediately(conn.socket)


########################################
# ../../../omlish/sockets/server/threading.py


##


class ThreadingSocketServerHandler:
    def __init__(
            self,
            handler: SocketServerHandler,
            *,
            shutdown_timeout: ta.Optional[float] = None,
    ) -> None:
        super().__init__()

        self._handler = handler
        self._shutdown_timeout = shutdown_timeout

        self._lock = threading.RLock()
        self._threads: ta.List[threading.Thread] = []
        self._is_shutdown = False

    @property
    def handler(self) -> SocketServerHandler:
        return self._handler

    #

    def __call__(self, conn: SocketAndAddress) -> None:
        self.handle(conn)

    def handle(self, conn: SocketAndAddress) -> None:
        with self._lock:
            check.state(not self._is_shutdown)

            self._reap()

            t = threading.Thread(
                target=self._handler,
                args=(conn,),
            )

            self._threads.append(t)

            t.start()

    #

    def _reap(self) -> None:
        with self._lock:
            self._threads[:] = (thread for thread in self._threads if thread.is_alive())

    def is_alive(self) -> bool:
        with self._lock:
            self._reap()

            return bool(self._threads)

    def join(self, timeout: ta.Optional[float] = None) -> None:
        if timeout is not None:
            deadline: ta.Optional[float] = time.time() + timeout
        else:
            deadline = None

        def calc_timeout() -> ta.Optional[float]:
            if deadline is None:
                return None

            tt = deadline - time.time()
            if tt <= 0:
                raise TimeoutError

            return tt

        if not (self._lock.acquire(timeout=calc_timeout() or -1)):
            raise TimeoutError

        try:
            self._reap()

            for t in self._threads:
                t.join(timeout=calc_timeout())

                if t.is_alive():
                    raise TimeoutError

        finally:
            self._lock.release()

    #

    class _NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def shutdown(
            self,
            block: bool = False,
            timeout: ta.Union[float, None, ta.Type[_NOT_SET]] = _NOT_SET,
    ) -> None:
        self._is_shutdown = True

        if block:
            if timeout is self._NOT_SET:
                timeout = self._shutdown_timeout

            self.join(timeout=timeout)  # type: ignore

    #

    def __enter__(self) -> 'ThreadingSocketServerHandler':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


########################################
# ../../../omlish/subprocesses/base.py


##


# Valid channel type kwarg values:
#  - A special flag negative int
#  - A positive fd int
#  - A file-like object
#  - None

SUBPROCESS_CHANNEL_OPTION_VALUES: ta.Mapping[SubprocessChannelOption, int] = {
    'pipe': subprocess.PIPE,
    'stdout': subprocess.STDOUT,
    'devnull': subprocess.DEVNULL,
}


##


class VerboseCalledProcessError(subprocess.CalledProcessError):
    @classmethod
    def from_std(cls, e: subprocess.CalledProcessError) -> 'VerboseCalledProcessError':
        return cls(
            e.returncode,
            e.cmd,
            output=e.output,
            stderr=e.stderr,
        )

    def __str__(self) -> str:
        msg = super().__str__()
        if self.output is not None:
            msg += f' Output: {self.output!r}'
        if self.stderr is not None:
            msg += f' Stderr: {self.stderr!r}'
        return msg


class BaseSubprocesses(Abstract):
    DEFAULT_LOGGER: ta.ClassVar[ta.Optional[LoggerLike]] = None

    PIPE: ta.ClassVar[int] = subprocess.PIPE
    STDOUT: ta.ClassVar[int] = subprocess.STDOUT
    DEVNULL: ta.ClassVar[int] = subprocess.DEVNULL

    def __init__(
            self,
            *,
            log: ta.Optional[LoggerLike] = None,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
    ) -> None:
        super().__init__()

        self._log = log if log is not None else self.DEFAULT_LOGGER
        self._try_exceptions = try_exceptions if try_exceptions is not None else self.DEFAULT_TRY_EXCEPTIONS

    def set_logger(self, log: ta.Optional[LoggerLike]) -> None:
        self._log = log

    #

    def prepare_args(
            self,
            *cmd: str,
            env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
            extra_env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
            quiet: bool = False,
            shell: bool = False,
            **kwargs: ta.Any,
    ) -> ta.Tuple[ta.Tuple[ta.Any, ...], ta.Dict[str, ta.Any]]:
        if self._log:
            self._log.debug('Subprocesses.prepare_args: cmd=%r', cmd)
            if extra_env:
                self._log.debug('Subprocesses.prepare_args: extra_env=%r', extra_env)

        #

        if extra_env:
            env = {**(env if env is not None else os.environ), **extra_env}

        #

        if quiet and 'stderr' not in kwargs:
            if self._log and not self._log.isEnabledFor(logging.DEBUG):
                kwargs['stderr'] = subprocess.DEVNULL

        for chk in ('stdout', 'stderr'):
            try:
                chv = kwargs[chk]
            except KeyError:
                continue
            kwargs[chk] = SUBPROCESS_CHANNEL_OPTION_VALUES.get(chv, chv)

        #

        if not shell:
            cmd = subprocess_maybe_shell_wrap_exec(*cmd)

        #

        if 'timeout' in kwargs:
            kwargs['timeout'] = Timeout.of(kwargs['timeout']).or_(None)

        #

        return cmd, dict(
            env=env,
            shell=shell,
            **kwargs,
        )

    @contextlib.contextmanager
    def wrap_call(
            self,
            *cmd: ta.Any,
            raise_verbose: bool = False,
            **kwargs: ta.Any,
    ) -> ta.Iterator[None]:
        start_time = time.time()
        try:
            if self._log:
                self._log.debug('Subprocesses.wrap_call.try: cmd=%r', cmd)

            yield

        except Exception as exc:  # noqa
            if self._log:
                self._log.debug('Subprocesses.wrap_call.except: exc=%r', exc)

            if (
                    raise_verbose and
                    isinstance(exc, subprocess.CalledProcessError) and
                    not isinstance(exc, VerboseCalledProcessError) and
                    (exc.output is not None or exc.stderr is not None)
            ):
                raise VerboseCalledProcessError.from_std(exc) from exc

            raise

        finally:
            end_time = time.time()
            elapsed_s = end_time - start_time

            if self._log:
                self._log.debug('Subprocesses.wrap_call.finally: elapsed_s=%f cmd=%r', elapsed_s, cmd)

    @contextlib.contextmanager
    def prepare_and_wrap(
            self,
            *cmd: ta.Any,
            raise_verbose: bool = False,
            **kwargs: ta.Any,
    ) -> ta.Iterator[ta.Tuple[
        ta.Tuple[ta.Any, ...],
        ta.Dict[str, ta.Any],
    ]]:
        cmd, kwargs = self.prepare_args(*cmd, **kwargs)

        with self.wrap_call(
                *cmd,
                raise_verbose=raise_verbose,
                **kwargs,
        ):
            yield cmd, kwargs

    #

    DEFAULT_TRY_EXCEPTIONS: ta.Tuple[ta.Type[Exception], ...] = (
        FileNotFoundError,
        subprocess.CalledProcessError,
    )

    def try_fn(
            self,
            fn: ta.Callable[..., T],
            *cmd: str,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
            **kwargs: ta.Any,
    ) -> ta.Union[T, Exception]:
        if try_exceptions is None:
            try_exceptions = self._try_exceptions

        try:
            return fn(*cmd, **kwargs)

        except try_exceptions as e:  # noqa
            if self._log and self._log.isEnabledFor(logging.DEBUG):
                self._log.exception('command failed')
            return e

    async def async_try_fn(
            self,
            fn: ta.Callable[..., ta.Awaitable[T]],
            *cmd: ta.Any,
            try_exceptions: ta.Optional[ta.Tuple[ta.Type[Exception], ...]] = None,
            **kwargs: ta.Any,
    ) -> ta.Union[T, Exception]:
        if try_exceptions is None:
            try_exceptions = self._try_exceptions

        try:
            return await fn(*cmd, **kwargs)

        except try_exceptions as e:  # noqa
            if self._log and self._log.isEnabledFor(logging.DEBUG):
                self._log.exception('command failed')
            return e


########################################
# ../docker/cacheserved/manifests.py


##


@dc.dataclass(frozen=True)
class CacheServedDockerImageManifest:
    @dc.dataclass(frozen=True)
    class Route:
        paths: ta.Sequence[str]

        content_type: str
        content_length: int

        @dc.dataclass(frozen=True)
        class Target(Abstract):
            pass

        @dc.dataclass(frozen=True)
        class BytesTarget(Target):
            data: bytes

        @dc.dataclass(frozen=True)
        class CacheKeyTarget(Target):
            key: str

        target: Target

        def __post_init__(self) -> None:
            check.not_isinstance(self.paths, str)

    routes: ta.Sequence[Route]


#


async def build_cache_served_docker_image_manifest(
        data_server_routes: ta.Iterable[DataServerRoute],
        make_file_cache_key: ta.Callable[[str], ta.Awaitable[str]],
) -> CacheServedDockerImageManifest:
    routes: ta.List[CacheServedDockerImageManifest.Route] = []

    for data_server_route in data_server_routes:
        content_length: int

        data_server_target = data_server_route.target
        target: CacheServedDockerImageManifest.Route.Target
        if isinstance(data_server_target, BytesDataServerTarget):
            bytes_data = check.isinstance(data_server_target.data, bytes)
            content_length = len(bytes_data)
            target = CacheServedDockerImageManifest.Route.BytesTarget(bytes_data)

        elif isinstance(data_server_target, FileDataServerTarget):
            file_path = check.non_empty_str(data_server_target.file_path)
            content_length = os.path.getsize(file_path)
            cache_key = await make_file_cache_key(file_path)
            target = CacheServedDockerImageManifest.Route.CacheKeyTarget(cache_key)

        else:
            raise TypeError(data_server_target)

        routes.append(CacheServedDockerImageManifest.Route(
            paths=data_server_route.paths,

            content_type=check.non_empty_str(data_server_target.content_type),
            content_length=content_length,

            target=target,
        ))

    return CacheServedDockerImageManifest(
        routes=routes,
    )


#


async def build_cache_served_docker_image_data_server_routes(
        manifest: CacheServedDockerImageManifest,
        make_cache_key_target: ta.Callable[..., ta.Awaitable[DataServerTarget]],
) -> ta.List[DataServerRoute]:
    routes: ta.List[DataServerRoute] = []

    for manifest_route in manifest.routes:
        manifest_target = manifest_route.target

        target_kwargs: dict = dict(
            content_type=manifest_route.content_type,
            content_length=manifest_route.content_length,
        )

        target: DataServerTarget

        if isinstance(manifest_target, CacheServedDockerImageManifest.Route.BytesTarget):
            target = DataServerTarget.of(manifest_target.data, **target_kwargs)

        elif isinstance(manifest_target, CacheServedDockerImageManifest.Route.CacheKeyTarget):
            target = await make_cache_key_target(manifest_target.key, **target_kwargs)

        else:
            raise TypeError(manifest_target)

        routes.append(DataServerRoute(
            paths=manifest_route.paths,
            target=target,
        ))

    return routes


########################################
# ../../dataserver/server.py


##


class DataServer:
    @dc.dataclass(frozen=True)
    class HandlerRoute:
        paths: ta.Sequence[str]
        handler: DataServerHandler

        def __post_init__(self) -> None:
            check.not_isinstance(self.paths, str)
            for p in self.paths:
                check.non_empty_str(p)
            check.isinstance(self.handler, DataServerHandler)

        @classmethod
        def of(cls, obj: ta.Union[
            'DataServer.HandlerRoute',
            DataServerRoute,
        ]) -> 'DataServer.HandlerRoute':
            if isinstance(obj, cls):
                return obj

            elif isinstance(obj, DataServerRoute):
                return cls(
                    paths=obj.paths,
                    handler=DataServerTargetHandler.for_target(obj.target),
                )

            else:
                raise TypeError(obj)

        @classmethod
        def of_(cls, *objs: ta.Any) -> ta.List['DataServer.HandlerRoute']:
            return [cls.of(obj) for obj in objs]

    #

    @dc.dataclass(frozen=True)
    class Config:
        pass

    def __init__(
            self,
            routes: ta.Optional[ta.Iterable[HandlerRoute]] = None,
            config: Config = Config(),
    ) -> None:
        super().__init__()

        self._config = config

        self.set_routes(routes)

    #

    _routes_by_path: ta.Dict[str, HandlerRoute]

    def set_routes(self, routes: ta.Optional[ta.Iterable[HandlerRoute]]) -> None:
        routes_by_path: ta.Dict[str, DataServer.HandlerRoute] = {}

        for r in routes or []:
            for p in r.paths:
                check.not_in(p, routes_by_path)
                routes_by_path[p] = r

        self._routes_by_path = routes_by_path

    #

    def handle(self, req: DataServerRequest) -> DataServerResponse:
        try:
            rt = self._routes_by_path[req.path]
        except KeyError:
            return DataServerResponse(http.HTTPStatus.NOT_FOUND)

        return rt.handler.handle(req)


########################################
# ../../oci/building.py


##


class OciRepositoryBuilder:
    @dc.dataclass(frozen=True)
    class Blob:
        digest: str

        data: OciDataRef
        info: OciDataRefInfo

        media_type: ta.Optional[str] = None

        #

        def read(self) -> bytes:
            with open_oci_data_ref(self.data) as f:
                return f.read()

        def read_json(self) -> ta.Any:
            return json.loads(self.read().decode('utf-8'))

        def read_media(
                self,
                cls: ta.Type[OciMediaDataclassT] = OciMediaDataclass,  # type: ignore[assignment]
        ) -> OciMediaDataclassT:
            mt = check.non_empty_str(self.media_type)
            dct = self.read_json()
            obj = unmarshal_oci_media_dataclass(
                dct,
                media_type=mt,
            )
            return check.isinstance(obj, cls)

    def __init__(self) -> None:
        super().__init__()

        self._blobs: ta.Dict[str, OciRepositoryBuilder.Blob] = {}

    #

    def get_blobs(self) -> ta.Dict[str, Blob]:
        return dict(self._blobs)

    def add_blob(
            self,
            r: OciDataRef,
            ri: ta.Optional[OciDataRefInfo] = None,
            *,
            media_type: ta.Optional[str] = None,
    ) -> Blob:
        if ri is None:
            ri = OciDataRefInfo(r)

        if (dg := ri.digest()) in self._blobs:
            raise KeyError(ri.digest())

        blob = self.Blob(
            digest=dg,

            data=r,
            info=ri,

            media_type=media_type,
        )

        self._blobs[dg] = blob

        return blob

    #

    def marshal_media(self, obj: OciMediaDataclass) -> bytes:
        check.isinstance(obj, OciMediaDataclass)
        m = marshal_obj(obj)
        j = json_dumps_compact(m)
        b = j.encode('utf-8')
        return b

    def add_media(self, obj: OciMediaDataclass) -> OciMediaDescriptor:
        b = self.marshal_media(obj)

        r = BytesOciDataRef(b)
        ri = OciDataRefInfo(r)
        self.add_blob(
            r,
            ri,
            media_type=obj.media_type,
        )

        return OciMediaDescriptor(
            media_type=obj.media_type,
            digest=ri.digest(),
            size=ri.size(),
        )

    #

    def to_media(self, obj: OciDataclass) -> ta.Union[OciMediaDataclass, OciMediaDescriptor]:
        def make_kw(*exclude):
            return {
                a: v
                for f in dc.fields(obj)
                if (a := f.name) not in exclude
                for v in [getattr(obj, a)]
                if v is not None
            }

        if isinstance(obj, OciImageIndex):
            return OciMediaImageIndex(
                **make_kw('manifests'),
                manifests=[
                    self.add_data(m)
                    for m in obj.manifests
                ],
            )

        elif isinstance(obj, OciImageManifest):
            return OciMediaImageManifest(
                **make_kw('config', 'layers'),
                config=self.add_data(obj.config),
                layers=[
                    self.add_data(l)
                    for l in obj.layers
                ],
            )

        elif isinstance(obj, OciImageLayer):
            ri = OciDataRefInfo(obj.data)
            mt = OCI_IMAGE_LAYER_KIND_MEDIA_TYPES[obj.kind]
            self.add_blob(
                obj.data,
                ri,
                media_type=mt,
            )
            return OciMediaDescriptor(
                media_type=mt,
                digest=ri.digest(),
                size=ri.size(),
            )

        elif isinstance(obj, OciImageConfig):
            return OciMediaImageConfig(**make_kw())

        else:
            raise TypeError(obj)

    def add_data(self, obj: OciDataclass) -> OciMediaDescriptor:
        ret = self.to_media(obj)

        if isinstance(ret, OciMediaDataclass):
            return self.add_media(ret)

        elif isinstance(ret, OciMediaDescriptor):
            return ret

        else:
            raise TypeError(ret)


##


@dc.dataclass(frozen=True)
class BuiltOciImageIndexRepository:
    index: OciImageIndex

    media_index_descriptor: OciMediaDescriptor
    media_index: OciMediaImageIndex

    blobs: ta.Mapping[str, OciRepositoryBuilder.Blob]


def build_oci_index_repository(index: OciImageIndex) -> BuiltOciImageIndexRepository:
    builder = OciRepositoryBuilder()

    media_index_descriptor = builder.add_data(index)

    blobs = builder.get_blobs()

    media_index = blobs[media_index_descriptor.digest].read_media(OciMediaImageIndex)

    return BuiltOciImageIndexRepository(
        index=index,

        media_index_descriptor=media_index_descriptor,
        media_index=media_index,

        blobs=blobs,
    )


########################################
# ../../oci/loading.py


##


class OciRepositoryLoader:
    def __init__(
            self,
            repo: OciRepository,
    ) -> None:
        super().__init__()

        self._repo = repo

    #

    def load_object(
            self,
            data: bytes,
            cls: ta.Type[T] = object,  # type: ignore[assignment]
            *,
            media_type: ta.Optional[str] = None,
    ) -> T:
        text = data.decode('utf-8')
        dct = json.loads(text)
        obj = unmarshal_oci_media_dataclass(
            dct,
            media_type=media_type,
        )
        return check.isinstance(obj, cls)

    def read_object(
            self,
            digest: str,
            cls: ta.Type[T] = object,  # type: ignore[assignment]
            *,
            media_type: ta.Optional[str] = None,
    ) -> T:
        data = self._repo.read_blob(digest)
        return self.load_object(
            data,
            cls,
            media_type=media_type,
        )

    def read_descriptor(
            self,
            desc: OciMediaDescriptor,
            cls: ta.Type[T] = object,  # type: ignore[assignment]
    ) -> ta.Any:
        return self.read_object(
            desc.digest,
            cls,
            media_type=desc.media_type,
        )

    #

    def from_media(self, obj: ta.Any) -> ta.Any:
        def make_kw(*exclude):
            return {
                a: getattr(obj, a)
                for f in dc.fields(obj)
                if (a := f.name) not in OCI_MEDIA_FIELDS
                and a not in exclude
            }

        if isinstance(obj, OciMediaImageConfig):
            return OciImageConfig(**make_kw())

        elif isinstance(obj, OciMediaImageManifest):
            return OciImageManifest(
                **make_kw('config', 'layers'),
                config=self.from_media(self.read_descriptor(obj.config)),
                layers=[
                    OciImageLayer(
                        kind=lk,
                        data=self._repo.ref_blob(l.digest),
                    )
                    for l in obj.layers
                    if (lk := OCI_IMAGE_LAYER_KIND_MEDIA_TYPES_.get(l.media_type)) is not None
                ],
            )

        elif isinstance(obj, OciMediaImageIndex):
            return OciImageIndex(
                **make_kw('manifests'),
                manifests=[
                    fm
                    for m in obj.manifests
                    if self._repo.contains_blob(m.digest)
                    for fm in [self.from_media(self.read_descriptor(m))]
                    if not is_empty_oci_dataclass(fm)
                ],
            )

        else:
            raise TypeError(obj)


##


def read_oci_repository_root_index(
        obj: ta.Any,
        *,
        file_name: str = 'index.json',
) -> OciImageIndex:
    file_repo = check.isinstance(OciRepository.of(obj), FileOciRepository)

    repo_ldr = OciRepositoryLoader(file_repo)

    media_image_idx = repo_ldr.load_object(file_repo.read_file(file_name), OciMediaImageIndex)

    image_idx = repo_ldr.from_media(media_image_idx)

    return check.isinstance(image_idx, OciImageIndex)


########################################
# ../../../omlish/formats/yaml/goyaml/parsing.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


# context context at parsing
@dc.dataclass()
class YamlParsingContext:
    token_ref: ta.Optional['YamlParseTokenRef'] = None
    path: str = dc.field(default_factory=dataclass_field_required('path'))
    is_flow: bool = False

    def current_token(self) -> ta.Optional['YamlParseToken']:
        ref = check.not_none(self.token_ref)

        if ref.idx >= ref.size:
            return None

        return ref.tokens[ref.idx]

    def is_comment(self) -> bool:
        return YamlParseToken.type(self.current_token()) == YamlTokenType.COMMENT

    def next_token(self) -> ta.Optional['YamlParseToken']:
        ref = check.not_none(self.token_ref)

        if ref.idx + 1 >= ref.size:
            return None

        return ref.tokens[ref.idx + 1]

    def next_not_comment_token(self) -> ta.Optional['YamlParseToken']:
        ref = check.not_none(self.token_ref)

        for i in range(ref.idx + 1, ref.size):
            tk = ref.tokens[i]
            if tk.type() == YamlTokenType.COMMENT:
                continue
            return tk

        return None

    def is_token_not_found(self) -> bool:
        return self.current_token() is None

    def with_group(self, g: 'YamlParseTokenGroup') -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.token_ref = YamlParseTokenRef(
            tokens=g.tokens,
            size=len(g.tokens),
        )
        return ctx

    def with_child(self, path: str) -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.path = self.path + '.' + yaml_normalize_path(path)
        return ctx

    def with_index(self, idx: int) -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.path = self.path + '[' + str(idx) + ']'
        return ctx

    def with_flow(self, is_flow: bool) -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.is_flow = is_flow
        return ctx

    @staticmethod
    def new() -> 'YamlParsingContext':
        return YamlParsingContext(
            path='$',
        )

    def go_next(self) -> None:
        ref = check.not_none(self.token_ref)
        if ref.size <= ref.idx + 1:
            ref.idx = ref.size
        else:
            ref.idx += 1

    def next(self) -> bool:
        return check.not_none(self.token_ref).idx < check.not_none(self.token_ref).size

    def insert_null_token(self, tk: 'YamlParseToken') -> 'YamlParseToken':
        null_token = self.create_implicit_null_token(tk)
        self.insert_token(null_token)
        self.go_next()

        return null_token

    def add_null_value_token(self, tk: 'YamlParseToken') -> 'YamlParseToken':
        null_token = self.create_implicit_null_token(tk)
        raw_tk = null_token.raw_token()

        # add space for map or sequence value.
        check.not_none(raw_tk).position.column += 1

        self.add_token(null_token)
        self.go_next()

        return null_token

    def create_implicit_null_token(self, base: 'YamlParseToken') -> 'YamlParseToken':
        pos = copy.copy(check.not_none(base.raw_token()).position)
        pos.column += 1
        tk = yaml_new_token('null', ' null', pos)
        tk.type = YamlTokenType.IMPLICIT_NULL
        return YamlParseToken(token=tk)

    def insert_token(self, tk: 'YamlParseToken') -> None:
        ref = check.not_none(self.token_ref)
        idx = ref.idx
        if ref.size < idx:
            return

        if ref.size == idx:
            cur_token = ref.tokens[ref.size - 1]
            check.not_none(tk.raw_token()).next = cur_token.raw_token()
            check.not_none(cur_token.raw_token()).prev = tk.raw_token()

            ref.tokens.append(tk)
            ref.size = len(ref.tokens)
            return

        cur_token = ref.tokens[idx]
        check.not_none(tk.raw_token()).next = cur_token.raw_token()
        check.not_none(cur_token.raw_token()).prev = tk.raw_token()

        ref.tokens = [*ref.tokens[:idx + 1], *ref.tokens[idx:]]
        ref.tokens[idx] = tk
        ref.size = len(ref.tokens)

    def add_token(self, tk: 'YamlParseToken') -> None:
        ref = check.not_none(self.token_ref)
        last_tk = check.not_none(ref.tokens[ref.size - 1])
        if last_tk.group is not None:
            last_tk = check.not_none(last_tk.group.last())

        check.not_none(last_tk.raw_token()).next = tk.raw_token()
        check.not_none(tk.raw_token()).prev = last_tk.raw_token()

        ref.tokens.append(tk)
        ref.size = len(ref.tokens)


@dc.dataclass()
class YamlParseTokenRef:
    tokens: ta.List['YamlParseToken']
    size: int
    idx: int = 0


##


YAML_PATH_SPECIAL_CHARS = (
    '$',
    '*',
    '.',
    '[',
    ']',
)


def yaml_contains_path_special_char(path: str) -> bool:
    return any(char in path for char in YAML_PATH_SPECIAL_CHARS)


def yaml_normalize_path(path: str) -> str:
    if yaml_contains_path_special_char(path):
        return f"'{path}'"

    return path


##


# Option represents parser's option.
YamlOption = ta.Callable[['YamlParser'], None]  # ta.TypeAlias  # omlish-amalg-typing-no-move


# AllowDuplicateMapKey allow the use of keys with the same name in the same map, but by default, this is not permitted.
def yaml_allow_duplicate_map_key() -> YamlOption:
    def fn(p: 'YamlParser') -> None:
        p.allow_duplicate_map_key = True

    return fn


##


class YamlParseTokenGroupType(enum.Enum):
    NONE = enum.auto()
    DIRECTIVE = enum.auto()
    DIRECTIVE_NAME = enum.auto()
    DOCUMENT = enum.auto()
    DOCUMENT_BODY = enum.auto()
    ANCHOR = enum.auto()
    ANCHOR_NAME = enum.auto()
    ALIAS = enum.auto()
    LITERAL = enum.auto()
    FOLDED = enum.auto()
    SCALAR_TAG = enum.auto()
    MAP_KEY = enum.auto()
    MAP_KEY_VALUE = enum.auto()


@dc.dataclass()
class YamlParseToken:
    token: ta.Optional[YamlToken] = None
    group: ta.Optional['YamlParseTokenGroup'] = None
    line_comment: ta.Optional[YamlToken] = None

    def raw_token(self: ta.Optional['YamlParseToken']) -> ta.Optional[YamlToken]:
        if self is None:
            return None
        if self.token is not None:
            return self.token
        return check.not_none(self.group).raw_token()

    def type(self: ta.Optional['YamlParseToken']) -> YamlTokenType:
        if self is None:
            return YamlTokenType.UNKNOWN
        if self.token is not None:
            return self.token.type
        return check.not_none(self.group).token_type()

    def group_type(self: ta.Optional['YamlParseToken']) -> YamlParseTokenGroupType:
        if self is None:
            return YamlParseTokenGroupType.NONE
        if self.token is not None:
            return YamlParseTokenGroupType.NONE
        return check.not_none(self.group).type

    def line(self: ta.Optional['YamlParseToken']) -> int:
        if self is None:
            return 0
        if self.token is not None:
            return self.token.position.line
        return check.not_none(self.group).line()

    def column(self: ta.Optional['YamlParseToken']) -> int:
        if self is None:
            return 0
        if self.token is not None:
            return self.token.position.column
        return check.not_none(self.group).column()

    def set_group_type(self, typ: YamlParseTokenGroupType) -> None:
        if self.group is None:
            return
        self.group.type = typ


##


@dc.dataclass()
class YamlParseTokenGroup:
    type: YamlParseTokenGroupType = YamlParseTokenGroupType.NONE
    tokens: ta.List[YamlParseToken] = dc.field(default_factory=dataclass_field_required('tokens'))

    def first(self) -> ta.Optional[YamlParseToken]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0]

    def last(self) -> ta.Optional[YamlParseToken]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[len(self.tokens) - 1]

    def raw_token(self) -> ta.Optional[YamlToken]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0].raw_token()

    def line(self) -> int:
        if len(self.tokens) == 0:
            return 0
        return self.tokens[0].line()

    def column(self) -> int:
        if len(self.tokens) == 0:
            return 0
        return self.tokens[0].column()

    def token_type(self) -> YamlTokenType:
        if len(self.tokens) == 0:
            return YamlTokenType.UNKNOWN
        return self.tokens[0].type()


def yaml_create_grouped_tokens(tokens: YamlTokens) -> YamlErrorOr[ta.List[YamlParseToken]]:
    tks = yaml_new_tokens(tokens)

    tks = yaml_create_line_comment_token_groups(tks)

    tks_ = yaml_create_literal_and_folded_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_anchor_and_alias_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_scalar_tag_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_anchor_with_scalar_tag_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_map_key_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks = yaml_create_map_key_value_token_groups(tks)

    tks_ = yaml_create_directive_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = yaml_create_document_tokens(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    return tks


def yaml_new_tokens(tks: YamlTokens) -> ta.List[YamlParseToken]:
    ret: ta.List[YamlParseToken] = []
    for tk in tks:
        ret.append(YamlParseToken(token=tk))
    return ret


def yaml_create_line_comment_token_groups(tokens: ta.List[YamlParseToken]) -> ta.List[YamlParseToken]:
    ret: ta.List[YamlParseToken] = []
    for i in range(len(tokens)):
        tk = tokens[i]
        if tk.type() == YamlTokenType.COMMENT:
            if i > 0 and tokens[i - 1].line() == tk.line():
                tokens[i - 1].line_comment = tk.raw_token()
            else:
                ret.append(tk)
        else:
            ret.append(tk)
    return ret


def yaml_create_literal_and_folded_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:  # noqa
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.LITERAL:
            tks: ta.List[YamlParseToken] = [tk]
            if i + 1 < len(tokens):
                tks.append(tokens[i + 1])
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.LITERAL,
                    tokens=tks,
                ),
            ))
            i += 1
        elif tk.type() == YamlTokenType.FOLDED:
            tks = [tk]
            if i + 1 < len(tokens):
                tks.append(tokens[i + 1])
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.FOLDED,
                    tokens=tks,
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def yaml_create_anchor_and_alias_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.ANCHOR:
            if i + 1 >= len(tokens):
                return YamlSyntaxError('undefined anchor name', tk.raw_token())
            if i + 2 >= len(tokens):
                return YamlSyntaxError('undefined anchor value', tk.raw_token())
            anchor_name = YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.ANCHOR_NAME,
                    tokens=[tk, tokens[i + 1]],
                ),
            )
            value_tk = tokens[i + 2]
            if tk.line() == value_tk.line() and value_tk.type() == YamlTokenType.SEQUENCE_ENTRY:
                return YamlSyntaxError(
                    'sequence entries are not allowed after anchor on the same line',
                    value_tk.raw_token(),
                )
            if tk.line() == value_tk.line() and yaml_is_scalar_type(value_tk):
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.ANCHOR,
                        tokens=[anchor_name, value_tk],
                    ),
                ))
                i += 1
            else:
                ret.append(anchor_name)
            i += 1
        elif tk.type() == YamlTokenType.ALIAS:
            if i + 1 == len(tokens):
                return YamlSyntaxError('undefined alias name', tk.raw_token())
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.ALIAS,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def yaml_create_scalar_tag_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() != YamlTokenType.TAG:
            ret.append(tk)
            continue
        tag = check.not_none(tk.raw_token())
        if tag.value.startswith('!!'):
            # secondary tag.
            if tag.value in (
                    YamlReservedTagKeywords.INTEGER,
                    YamlReservedTagKeywords.FLOAT,
                    YamlReservedTagKeywords.STRING,
                    YamlReservedTagKeywords.BINARY,
                    YamlReservedTagKeywords.TIMESTAMP,
                    YamlReservedTagKeywords.BOOLEAN,
                    YamlReservedTagKeywords.NULL,
            ):
                if len(tokens) <= i + 1:
                    ret.append(tk)
                    continue
                if tk.line() != tokens[i + 1].line():
                    ret.append(tk)
                    continue
                if tokens[i + 1].group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                    ret.append(tk)
                    continue
                if yaml_is_scalar_type(tokens[i + 1]):
                    ret.append(YamlParseToken(
                        group=YamlParseTokenGroup(
                            type=YamlParseTokenGroupType.SCALAR_TAG,
                            tokens=[tk, tokens[i + 1]],
                        ),
                    ))
                    i += 1
                else:
                    ret.append(tk)
            elif tag.value == YamlReservedTagKeywords.MERGE:
                if len(tokens) <= i + 1:
                    ret.append(tk)
                    continue
                if tk.line() != tokens[i + 1].line():
                    ret.append(tk)
                    continue
                if tokens[i + 1].group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                    ret.append(tk)
                    continue
                if tokens[i + 1].type() != YamlTokenType.MERGE_KEY:
                    return YamlSyntaxError('could not find merge key', tokens[i + 1].raw_token())
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.SCALAR_TAG,
                        tokens=[tk, tokens[i + 1]],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
        else:
            if len(tokens) <= i + 1:
                ret.append(tk)
                continue
            if tk.line() != tokens[i + 1].line():
                ret.append(tk)
                continue
            if tokens[i + 1].group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                ret.append(tk)
                continue
            if yaml_is_flow_type(tokens[i + 1]):
                ret.append(tk)
                continue
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.SCALAR_TAG,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
    return ret


def yaml_create_anchor_with_scalar_tag_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:  # noqa
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
            if i + 1 >= len(tokens):
                return YamlSyntaxError('undefined anchor value', tk.raw_token())
            value_tk = tokens[i + 1]
            if tk.line() == value_tk.line() and value_tk.group_type() == YamlParseTokenGroupType.SCALAR_TAG:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.ANCHOR,
                        tokens=[tk, tokens[i + 1]],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
        else:
            ret.append(tk)
    return ret


def yaml_create_map_key_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    tks = yaml_create_map_key_by_mapping_key(tokens)
    if isinstance(tks, YamlError):
        return tks
    return yaml_create_map_key_by_mapping_value(tks)


def yaml_create_map_key_by_mapping_key(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.MAPPING_KEY:
            if i + 1 >= len(tokens):
                return YamlSyntaxError('undefined map key', tk.raw_token())
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.MAP_KEY,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def yaml_create_map_key_by_mapping_value(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.MAPPING_VALUE:
            if i == 0:
                return YamlSyntaxError('unexpected key name', tk.raw_token())
            map_key_tk = tokens[i - 1]
            if yaml_is_not_map_key_type(map_key_tk):
                return YamlSyntaxError('found an invalid key for this map', tokens[i].raw_token())
            new_tk = YamlParseToken(
                token=map_key_tk.token,
                group=map_key_tk.group,
            )
            map_key_tk.token = None
            map_key_tk.group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.MAP_KEY,
                tokens=[new_tk, tk],
            )
        else:
            ret.append(tk)
    return ret


def yaml_create_map_key_value_token_groups(tokens: ta.List[YamlParseToken]) -> ta.List[YamlParseToken]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.group_type() == YamlParseTokenGroupType.MAP_KEY:
            if len(tokens) <= i + 1:
                ret.append(tk)
                continue
            value_tk = tokens[i + 1]
            if tk.line() != value_tk.line():
                ret.append(tk)
                continue
            if value_tk.group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                ret.append(tk)
                continue
            if (
                    value_tk.type() == YamlTokenType.TAG and
                    value_tk.group_type() != YamlParseTokenGroupType.SCALAR_TAG
            ):
                ret.append(tk)
                continue

            if yaml_is_scalar_type(value_tk) or value_tk.type() == YamlTokenType.TAG:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.MAP_KEY_VALUE,
                        tokens=[tk, value_tk],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
                continue
        else:
            ret.append(tk)
    return ret


def yaml_create_directive_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.DIRECTIVE:
            if i + 1 >= len(tokens):
                return YamlSyntaxError('undefined directive value', tk.raw_token())
            directive_name = YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.DIRECTIVE_NAME,
                    tokens=[tk, tokens[i + 1]],
                ),
            )
            i += 1
            value_tks: ta.List[YamlParseToken] = []
            for j in range(i + 1, len(tokens)):
                if tokens[j].line() != tk.line():
                    break
                value_tks.append(tokens[j])
                i += 1
            if i + 1 >= len(tokens) or tokens[i + 1].type() != YamlTokenType.DOCUMENT_HEADER:
                return YamlSyntaxError('unexpected directive value. document not started', tk.raw_token())
            if len(value_tks) != 0:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DIRECTIVE,
                        tokens=[directive_name, *value_tks],
                    ),
                ))
            else:
                ret.append(directive_name)
        else:
            ret.append(tk)
    return ret


def yaml_create_document_tokens(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.DOCUMENT_HEADER:
            if i != 0:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(tokens=tokens[:i]),
                ))
            if i + 1 == len(tokens):
                # if current token is last token, add DocumentHeader only tokens to ret.
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DOCUMENT,
                        tokens=[tk],
                    ),
                ))
                return ret
            if tokens[i + 1].type() == YamlTokenType.DOCUMENT_HEADER:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DOCUMENT,
                        tokens=[tk],
                    ),
                ))
                return ret
            if tokens[i].line() == tokens[i + 1].line():
                if tokens[i + 1].group_type() in (
                        YamlParseTokenGroupType.MAP_KEY,
                        YamlParseTokenGroupType.MAP_KEY_VALUE,
                ):
                    return YamlSyntaxError(
                        'value cannot be placed after document separator',
                        tokens[i + 1].raw_token(),
                    )
                if tokens[i + 1].type() == YamlTokenType.SEQUENCE_ENTRY:
                    return YamlSyntaxError(
                        'value cannot be placed after document separator',
                        tokens[i + 1].raw_token(),
                    )
            tks = yaml_create_document_tokens(tokens[i + 1:])
            if isinstance(tks, YamlError):
                return tks
            if len(tks) != 0:
                tks[0].set_group_type(YamlParseTokenGroupType.DOCUMENT)
                check.not_none(tks[0].group).tokens = list(check.not_none(tks[0].group).tokens)
                ret.extend(tks)
                return ret
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.DOCUMENT,
                    tokens=[tk],
                ),
            ))
            return ret
        elif tk.type() == YamlTokenType.DOCUMENT_END:
            if i != 0:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DOCUMENT,
                        tokens=tokens[0: i + 1],
                    ),
                ))
            if i + 1 == len(tokens):
                return ret
            if yaml_is_scalar_type(tokens[i + 1]):
                return YamlSyntaxError('unexpected end content', tokens[i + 1].raw_token())

            tks = yaml_create_document_tokens(tokens[i + 1:])
            if isinstance(tks, YamlError):
                return tks
            ret.extend(tks)
            return ret
    ret.append(YamlParseToken(
        group=YamlParseTokenGroup(
            type=YamlParseTokenGroupType.DOCUMENT,
            tokens=tokens,
        ),
    ))
    return ret


def yaml_is_scalar_type(tk: YamlParseToken) -> bool:
    if tk.group_type() in (YamlParseTokenGroupType.MAP_KEY, YamlParseTokenGroupType.MAP_KEY_VALUE):
        return False
    typ = tk.type()
    return typ in (
        YamlTokenType.ANCHOR,
        YamlTokenType.ALIAS,
        YamlTokenType.LITERAL,
        YamlTokenType.FOLDED,
        YamlTokenType.NULL,
        YamlTokenType.IMPLICIT_NULL,
        YamlTokenType.BOOL,
        YamlTokenType.INTEGER,
        YamlTokenType.BINARY_INTEGER,
        YamlTokenType.OCTET_INTEGER,
        YamlTokenType.HEX_INTEGER,
        YamlTokenType.FLOAT,
        YamlTokenType.INFINITY,
        YamlTokenType.NAN,
        YamlTokenType.STRING,
        YamlTokenType.SINGLE_QUOTE,
        YamlTokenType.DOUBLE_QUOTE,
    )


def yaml_is_not_map_key_type(tk: YamlParseToken) -> bool:
    typ = tk.type()
    return typ in (
        YamlTokenType.DIRECTIVE,
        YamlTokenType.DOCUMENT_HEADER,
        YamlTokenType.DOCUMENT_END,
        YamlTokenType.COLLECT_ENTRY,
        YamlTokenType.MAPPING_START,
        YamlTokenType.MAPPING_VALUE,
        YamlTokenType.MAPPING_END,
        YamlTokenType.SEQUENCE_START,
        YamlTokenType.SEQUENCE_ENTRY,
        YamlTokenType.SEQUENCE_END,
    )


def yaml_is_flow_type(tk: YamlParseToken) -> bool:
    typ = tk.type()
    return typ in (
        YamlTokenType.MAPPING_START,
        YamlTokenType.MAPPING_END,
        YamlTokenType.SEQUENCE_START,
        YamlTokenType.SEQUENCE_ENTRY,
    )


##


class YamlNodeMakers:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    @staticmethod
    def new_mapping_node(
            ctx: YamlParsingContext,
            tk: YamlParseToken,
            is_flow: bool,
            *values: MappingValueYamlNode,
    ) -> YamlErrorOr[MappingYamlNode]:
        node = YamlAsts.mapping(check.not_none(tk.raw_token()), is_flow, *values)
        node.set_path(ctx.path)
        return node

    @staticmethod
    def new_mapping_value_node(
            ctx: YamlParsingContext,
            colon_tk: YamlParseToken,
            entry_tk: ta.Optional[YamlParseToken],
            key: MapKeyYamlNode,
            value: YamlNode,
    ) -> YamlErrorOr[MappingValueYamlNode]:
        node = YamlAsts.mapping_value(check.not_none(colon_tk.raw_token()), key, value)
        node.set_path(ctx.path)
        node.collect_entry = YamlParseToken.raw_token(entry_tk)
        if check.not_none(key.get_token()).position.line == check.not_none(value.get_token()).position.line:
            # originally key was commented, but now that null value has been added, value must be commented.
            if (err := yaml_set_line_comment(ctx, value, colon_tk)) is not None:
                return err
            # set line comment by colon_tk or entry_tk.
            if (err := yaml_set_line_comment(ctx, value, entry_tk)) is not None:
                return err
        else:
            if (err := yaml_set_line_comment(ctx, key, colon_tk)) is not None:
                return err
            # set line comment by colon_tk or entry_tk.
            if (err := yaml_set_line_comment(ctx, key, entry_tk)) is not None:
                return err
        return node

    @staticmethod
    def new_mapping_key_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[MappingKeyYamlNode]:  # noqa
        node = YamlAsts.mapping_key(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_anchor_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[AnchorYamlNode]:
        node = YamlAsts.anchor(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_alias_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[AliasYamlNode]:
        node = YamlAsts.alias(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_directive_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[DirectiveYamlNode]:  # noqa
        node = YamlAsts.directive(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_merge_key_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[MergeKeyYamlNode]:  # noqa
        node = YamlAsts.merge_key(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_null_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[NullYamlNode]:
        node = YamlAsts.null(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_bool_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[BoolYamlNode]:
        node = YamlAsts.bool_(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_integer_node(ctx: YamlParsingContext, tk: YamlParseToken) -> YamlErrorOr[IntegerYamlNode]:
        node = YamlAsts.integer(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_float_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[FloatYamlNode]:
        node = YamlAsts.float_(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_infinity_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[InfinityYamlNode]:  # noqa
        node = YamlAsts.infinity(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_nan_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[NanYamlNode]:
        node = YamlAsts.nan(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_string_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[StringYamlNode]:
        node = YamlAsts.string(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_literal_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[LiteralYamlNode]:
        node = YamlAsts.literal(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_tag_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[TagYamlNode]:
        node = YamlAsts.tag(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_sequence_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken], is_flow: bool) -> YamlErrorOr[SequenceYamlNode]:  # noqa
        node = YamlAsts.sequence(check.not_none(YamlParseToken.raw_token(tk)), is_flow)
        node.set_path(ctx.path)
        if (err := yaml_set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_tag_default_scalar_value_node(ctx: YamlParsingContext, tag: YamlToken) -> YamlErrorOr[ScalarYamlNode]:
        pos = copy.copy(tag.position)
        pos.column += 1

        tk: YamlErrorOr[YamlParseToken]
        node: YamlErrorOr[ScalarYamlNode]

        if tag.value == YamlReservedTagKeywords.INTEGER:
            tk = YamlParseToken(token=yaml_new_token('0', '0', pos))
            n0 = YamlNodeMakers.new_integer_node(ctx, tk)
            if isinstance(n0, YamlError):
                return n0
            node = n0
        elif tag.value == YamlReservedTagKeywords.FLOAT:
            tk = YamlParseToken(token=yaml_new_token('0', '0', pos))
            n1 = YamlNodeMakers.new_float_node(ctx, tk)
            if isinstance(n1, YamlError):
                return n1
            node = n1
        elif tag.value in (
                YamlReservedTagKeywords.STRING,
                YamlReservedTagKeywords.BINARY,
                YamlReservedTagKeywords.TIMESTAMP,
        ):
            tk = YamlParseToken(token=yaml_new_token('', '', pos))
            n2 = YamlNodeMakers.new_string_node(ctx, tk)
            if isinstance(n2, YamlError):
                return n2
            node = n2
        elif tag.value == YamlReservedTagKeywords.BOOLEAN:
            tk = YamlParseToken(token=yaml_new_token('false', 'false', pos))
            n3 = YamlNodeMakers.new_bool_node(ctx, tk)
            if isinstance(n3, YamlError):
                return n3
            node = n3
        elif tag.value == YamlReservedTagKeywords.NULL:
            tk = YamlParseToken(token=yaml_new_token('null', 'null', pos))
            n4 = YamlNodeMakers.new_null_node(ctx, tk)
            if isinstance(n4, YamlError):
                return n4
            node = n4
        else:
            return YamlSyntaxError(f'cannot assign default value for {tag.value!r} tag', tag)
        ctx.insert_token(tk)
        ctx.go_next()
        return node


def yaml_set_line_comment(ctx: YamlParsingContext, node: YamlNode, tk: ta.Optional[YamlParseToken]) -> ta.Optional[YamlError]:  # noqa
    if tk is None or tk.line_comment is None:
        return None
    comment = YamlAsts.comment_group([tk.line_comment])
    comment.set_path(ctx.path)
    if (err := node.set_comment(comment)) is not None:
        return err
    return None


def yaml_set_head_comment(cm: ta.Optional[CommentGroupYamlNode], value: YamlNode) -> ta.Optional[YamlError]:
    if cm is None:
        return None
    n = value
    if isinstance(n, MappingYamlNode):
        if len(n.values) != 0 and value.get_comment() is None:
            cm.set_path(n.values[0].get_path())
            return n.values[0].set_comment(cm)
    elif isinstance(n, MappingValueYamlNode):
        cm.set_path(n.get_path())
        return n.set_comment(cm)
    cm.set_path(value.get_path())
    return value.set_comment(cm)


##


YamlParseMode = int  # ta.TypeAlias  # omlish-amalg-typing-no-move

YAML_PARSE_COMMENTS = YamlParseMode(1)  # parse comments and add them to AST


# ParseBytes parse from byte slice, and returns YamlFile
def yaml_parse_str(
        s: str,
        mode: YamlParseMode = YamlParseMode(0),
        *opts: YamlOption,
) -> YamlErrorOr[YamlFile]:
    tokens = yaml_tokenize(s)
    f = yaml_parse(tokens, mode, *opts)
    if isinstance(f, YamlError):
        return f
    return f


# Parse parse from token instances, and returns YamlFile
def yaml_parse(
        tokens: YamlTokens,
        mode: YamlParseMode = YamlParseMode(0),
        *opts: YamlOption,
) -> YamlErrorOr[YamlFile]:
    if (tk := tokens.invalid_token()) is not None:
        return YamlSyntaxError(check.not_none(tk.error).message, tk)
    p = YamlParser.new_parser(tokens, mode, opts)
    if isinstance(p, YamlError):
        return p
    f = p.parse(YamlParsingContext.new())
    if isinstance(f, YamlError):
        return f
    return f


#


YamlVersion = str  # ta.TypeAlias  # omlish-amalg-typing-no-move

YAML10 = YamlVersion('1.0')
YAML11 = YamlVersion('1.1')
YAML12 = YamlVersion('1.2')
YAML13 = YamlVersion('1.3')

YAML_VERSION_MAP: ta.Mapping[str, YamlVersion] = {
    '1.0': YAML10,
    '1.1': YAML11,
    '1.2': YAML12,
    '1.3': YAML13,
}


#

@dc.dataclass()
class YamlParser:
    tokens: ta.List[YamlParseToken]
    path_map: ta.Dict[str, YamlNode]
    yaml_version: YamlVersion = YamlVersion('')
    allow_duplicate_map_key: bool = False
    secondary_tag_directive: ta.Optional[DirectiveYamlNode] = None

    @staticmethod
    def new_parser(
            tokens: YamlTokens,
            mode: YamlParseMode,
            opts: ta.Iterable[YamlOption],
    ) -> YamlErrorOr['YamlParser']:
        filtered_tokens: ta.List[YamlToken] = []
        if mode & YAML_PARSE_COMMENTS != 0:
            filtered_tokens = tokens
        else:
            for tk in tokens:
                if tk.type == YamlTokenType.COMMENT:
                    continue
                # keep prev/next reference between tokens containing comments
                # https://github.com/goccy/go-yaml/issues/254
                filtered_tokens.append(tk)
        tks = yaml_create_grouped_tokens(YamlTokens(filtered_tokens))
        if isinstance(tks, YamlError):
            return tks
        p = YamlParser(
            tokens=tks,
            path_map={},
        )
        for opt in opts:
            opt(p)
        return p

    def parse(self, ctx: YamlParsingContext) -> YamlErrorOr[YamlFile]:
        file = YamlFile(docs=[])
        for token in self.tokens:
            doc = self.parse_document(ctx, check.not_none(token.group))
            if isinstance(doc, YamlError):
                return doc
            file.docs.append(doc)
        return file

    def parse_document(
            self,
            ctx: YamlParsingContext,
            doc_group: YamlParseTokenGroup,
    ) -> YamlErrorOr[DocumentYamlNode]:
        if len(doc_group.tokens) == 0:
            return YamlAsts.document(doc_group.raw_token(), None)

        self.path_map: ta.Dict[str, YamlNode] = {}

        tokens = doc_group.tokens
        start: ta.Optional[YamlToken] = None
        end: ta.Optional[YamlToken] = None
        if YamlParseToken.type(doc_group.first()) == YamlTokenType.DOCUMENT_HEADER:
            start = YamlParseToken.raw_token(doc_group.first())
            tokens = tokens[1:]

        clear_yaml_version = False
        try:
            if YamlParseToken.type(doc_group.last()) == YamlTokenType.DOCUMENT_END:
                end = YamlParseToken.raw_token(doc_group.last())
                tokens = tokens[:len(tokens) - 1]
                # clear yaml version value if DocumentEnd token (...) is specified.
                clear_yaml_version = True

            if len(tokens) == 0:
                return YamlAsts.document(doc_group.raw_token(), None)

            body = self.parse_document_body(ctx.with_group(YamlParseTokenGroup(
                type=YamlParseTokenGroupType.DOCUMENT_BODY,
                tokens=tokens,
            )))
            if isinstance(body, YamlError):
                return body
            node = YamlAsts.document(start, body)
            node.end = end
            return node

        finally:
            if clear_yaml_version:
                self.yaml_version = ''

    def parse_document_body(self, ctx: YamlParsingContext) -> YamlErrorOr[YamlNode]:
        node = self.parse_token(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        if ctx.next():
            return YamlSyntaxError('value is not allowed in this context', YamlParseToken.raw_token(ctx.current_token()))  # noqa
        return node

    def parse_token(self, ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[YamlNode]:
        if YamlParseToken.group_type(tk) in (
                YamlParseTokenGroupType.MAP_KEY,
                YamlParseTokenGroupType.MAP_KEY_VALUE,
        ):
            return self.parse_map(ctx)

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.DIRECTIVE:
            node0 = self.parse_directive(
                ctx.with_group(check.not_none(check.not_none(tk).group)),
                check.not_none(check.not_none(tk).group),
            )
            if isinstance(node0, YamlError):
                return node0
            ctx.go_next()
            return node0

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.DIRECTIVE_NAME:
            node1 = self.parse_directive_name(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node1, YamlError):
                return node1
            ctx.go_next()
            return node1

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR:
            node2 = self.parse_anchor(
                ctx.with_group(check.not_none(check.not_none(tk).group)),
                check.not_none(check.not_none(tk).group),
            )
            if isinstance(node2, YamlError):
                return node2
            ctx.go_next()
            return node2

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME:
            anchor = self.parse_anchor_name(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            if ctx.is_token_not_found():
                return YamlSyntaxError('could not find anchor value', YamlParseToken.raw_token(tk))
            value = self.parse_token(ctx, ctx.current_token())
            if isinstance(value, YamlError):
                return value
            if isinstance(value, AnchorYamlNode):
                return YamlSyntaxError('anchors cannot be used consecutively', value.get_token())
            anchor.value = value
            return anchor

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ALIAS:
            node3 = self.parse_alias(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node3, YamlError):
                return node3
            ctx.go_next()
            return node3

        elif YamlParseToken.group_type(tk) in (
                YamlParseTokenGroupType.LITERAL,
                YamlParseTokenGroupType.FOLDED,
        ):
            node4 = self.parse_literal(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node4, YamlError):
                return node4
            ctx.go_next()
            return node4

        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.SCALAR_TAG:
            node5 = self.parse_tag(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node5, YamlError):
                return node5
            ctx.go_next()
            return node5

        if YamlParseToken.type(tk) == YamlTokenType.COMMENT:
            return ta.cast('YamlErrorOr[YamlNode]', check.not_none(self.parse_comment(ctx)))

        elif YamlParseToken.type(tk) == YamlTokenType.TAG:
            return self.parse_tag(ctx)

        elif YamlParseToken.type(tk) == YamlTokenType.MAPPING_START:
            return self.parse_flow_map(ctx.with_flow(True))

        elif YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_START:
            return self.parse_flow_sequence(ctx.with_flow(True))

        elif YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_ENTRY:
            return self.parse_sequence(ctx)

        elif YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_END:
            # SequenceEndType is always validated in parse_flow_sequence.
            # Therefore, if this is found in other cases, it is treated as a syntax error.
            return YamlSyntaxError("could not find '[' character corresponding to ']'", YamlParseToken.raw_token(tk))

        elif YamlParseToken.type(tk) == YamlTokenType.MAPPING_END:
            # MappingEndType is always validated in parse_flow_map.
            # Therefore, if this is found in other cases, it is treated as a syntax error.
            return YamlSyntaxError("could not find '{' character corresponding to '}'", YamlParseToken.raw_token(tk))

        elif YamlParseToken.type(tk) == YamlTokenType.MAPPING_VALUE:
            return YamlSyntaxError('found an invalid key for this map', YamlParseToken.raw_token(tk))

        node6 = self.parse_scalar_value(ctx, tk)
        if isinstance(node6, YamlError):
            return node6

        ctx.go_next()
        return check.not_none(node6)

    def parse_scalar_value(self, ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ta.Optional[ScalarYamlNode]]:  # noqa
        tk = check.not_none(tk)
        if tk.group is not None:
            if tk.group_type() == YamlParseTokenGroupType.ANCHOR:
                return self.parse_anchor(ctx.with_group(tk.group), tk.group)

            elif tk.group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                anchor = self.parse_anchor_name(ctx.with_group(tk.group))
                if isinstance(anchor, YamlError):
                    return anchor
                ctx.go_next()
                if ctx.is_token_not_found():
                    return YamlSyntaxError('could not find anchor value', tk.raw_token())
                value = self.parse_token(ctx, ctx.current_token())
                if isinstance(value, YamlError):
                    return value
                if isinstance(value, AnchorYamlNode):
                    return YamlSyntaxError('anchors cannot be used consecutively', value.get_token())
                anchor.value = value
                return anchor

            elif tk.group_type() == YamlParseTokenGroupType.ALIAS:
                return self.parse_alias(ctx.with_group(tk.group))

            elif tk.group_type() in (
                    YamlParseTokenGroupType.LITERAL,
                    YamlParseTokenGroupType.FOLDED,
            ):
                return self.parse_literal(ctx.with_group(tk.group))

            elif tk.group_type() == YamlParseTokenGroupType.SCALAR_TAG:
                return self.parse_tag(ctx.with_group(tk.group))

            else:
                return YamlSyntaxError('unexpected scalar value', tk.raw_token())

        if tk.type() == YamlTokenType.MERGE_KEY:
            return YamlNodeMakers.new_merge_key_node(ctx, tk)

        if tk.type() in (YamlTokenType.NULL, YamlTokenType.IMPLICIT_NULL):
            return YamlNodeMakers.new_null_node(ctx, tk)

        if tk.type() == YamlTokenType.BOOL:
            return YamlNodeMakers.new_bool_node(ctx, tk)

        if tk.type() in (
                YamlTokenType.INTEGER,
                YamlTokenType.BINARY_INTEGER,
                YamlTokenType.OCTET_INTEGER,
                YamlTokenType.HEX_INTEGER,
        ):
            return YamlNodeMakers.new_integer_node(ctx, tk)

        if tk.type() == YamlTokenType.FLOAT:
            return YamlNodeMakers.new_float_node(ctx, tk)

        if tk.type() == YamlTokenType.INFINITY:
            return YamlNodeMakers.new_infinity_node(ctx, tk)

        if tk.type() == YamlTokenType.NAN:
            return YamlNodeMakers.new_nan_node(ctx, tk)

        if tk.type() in (
                YamlTokenType.STRING,
                YamlTokenType.SINGLE_QUOTE,
                YamlTokenType.DOUBLE_QUOTE,
        ):
            return YamlNodeMakers.new_string_node(ctx, tk)

        if tk.type() == YamlTokenType.TAG:
            # this case applies when it is a scalar tag and its value does not exist.
            # Examples of cases where the value does not exist include cases like `key: !!str,` or `!!str : value`.
            return self.parse_scalar_tag(ctx)

        return YamlSyntaxError('unexpected scalar value type', tk.raw_token())

    def parse_flow_map(self, ctx: YamlParsingContext) -> YamlErrorOr[MappingYamlNode]:
        node = YamlNodeMakers.new_mapping_node(ctx, check.not_none(ctx.current_token()), True)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip MappingStart token

        is_first = True
        while ctx.next():
            tk = ctx.current_token()
            if YamlParseToken.type(tk) == YamlTokenType.MAPPING_END:
                node.end = YamlParseToken.raw_token(tk)
                break

            entry_tk: ta.Optional[YamlParseToken] = None
            if YamlParseToken.type(tk) == YamlTokenType.COLLECT_ENTRY:
                entry_tk = tk
                ctx.go_next()
            elif not is_first:
                return YamlSyntaxError("',' or '}' must be specified", YamlParseToken.raw_token(tk))

            if YamlParseToken.type(tk := ctx.current_token()) == YamlTokenType.MAPPING_END:
                # this case is here: "{ elem, }".
                # In this case, ignore the last element and break mapping parsing.
                node.end = YamlParseToken.raw_token(tk)
                break

            map_key_tk = ctx.current_token()
            if YamlParseToken.group_type(map_key_tk) == YamlParseTokenGroupType.MAP_KEY_VALUE:
                value0 = self.parse_map_key_value(
                    ctx.with_group(check.not_none(check.not_none(map_key_tk).group)),
                    check.not_none(check.not_none(map_key_tk).group),
                    entry_tk,
                )
                if isinstance(value0, YamlError):
                    return value0
                node.values.append(value0)
                ctx.go_next()

            elif YamlParseToken.group_type(map_key_tk) == YamlParseTokenGroupType.MAP_KEY:
                key0 = self.parse_map_key(
                    ctx.with_group(check.not_none(check.not_none(map_key_tk).group)),
                    check.not_none(check.not_none(map_key_tk).group),
                )
                if isinstance(key0, YamlError):
                    return key0
                ctx = ctx.with_child(self.map_key_text(key0))
                colon_tk = check.not_none(check.not_none(map_key_tk).group).last()

                if self.is_flow_map_delim(check.not_none(ctx.next_token())):
                    value1 = YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(check.not_none(colon_tk)))
                    if isinstance(value1, YamlError):
                        return value1
                    map_value = YamlNodeMakers.new_mapping_value_node(
                        ctx,
                        check.not_none(colon_tk),
                        entry_tk,
                        key0,
                        value1,
                    )
                    if isinstance(map_value, YamlError):
                        return map_value
                    node.values.append(map_value)
                    ctx.go_next()

                else:
                    ctx.go_next()
                    if ctx.is_token_not_found():
                        return YamlSyntaxError('could not find map value', YamlParseToken.raw_token(colon_tk))
                    value2 = self.parse_token(ctx, ctx.current_token())
                    if isinstance(value2, YamlError):
                        return value2
                    map_value = YamlNodeMakers.new_mapping_value_node(
                        ctx,
                        check.not_none(colon_tk),
                        entry_tk,
                        key0,
                        value2,
                    )
                    if isinstance(map_value, YamlError):
                        return map_value
                    node.values.append(map_value)

            else:
                if not self.is_flow_map_delim(check.not_none(ctx.next_token())):
                    err_tk = map_key_tk
                    if err_tk is None:
                        err_tk = tk
                    return YamlSyntaxError('could not find flow map content', YamlParseToken.raw_token(err_tk))

                key1 = self.parse_scalar_value(ctx, map_key_tk)
                if isinstance(key1, YamlError):
                    return key1

                value3 = YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(check.not_none(map_key_tk)))
                if isinstance(value3, YamlError):
                    return value3

                map_value = YamlNodeMakers.new_mapping_value_node(
                    ctx,
                    check.not_none(map_key_tk),
                    entry_tk,
                    check.not_none(key1),
                    value3,
                )
                if isinstance(map_value, YamlError):
                    return map_value

                node.values.append(map_value)
                ctx.go_next()

            is_first = False

        if node.end is None:
            return YamlSyntaxError("could not find flow mapping end token '}'", node.start)

        # set line comment if exists. e.g.) } # comment
        if (err := yaml_set_line_comment(ctx, node, ctx.current_token())) is not None:
            return err

        ctx.go_next()  # skip mapping end token.
        return node

    def is_flow_map_delim(self, tk: YamlParseToken) -> bool:
        return tk.type() == YamlTokenType.MAPPING_END or tk.type() == YamlTokenType.COLLECT_ENTRY

    def parse_map(self, ctx: YamlParsingContext) -> YamlErrorOr[MappingYamlNode]:
        key_tk = check.not_none(ctx.current_token())
        if key_tk.group is None:
            return YamlSyntaxError('unexpected map key', YamlParseToken.raw_token(key_tk))

        key_value_node: MappingValueYamlNode
        if YamlParseToken.group_type(key_tk) == YamlParseTokenGroupType.MAP_KEY_VALUE:
            node0 = self.parse_map_key_value(
                ctx.with_group(check.not_none(key_tk.group)),
                check.not_none(key_tk.group),
                None,
            )
            if isinstance(node0, YamlError):
                return node0

            key_value_node = node0
            ctx.go_next()
            if (err := self.validate_map_key_value_next_token(ctx, key_tk, ctx.current_token())) is not None:
                return err

        else:
            key = self.parse_map_key(ctx.with_group(check.not_none(key_tk.group)), check.not_none(key_tk.group))
            if isinstance(key, YamlError):
                return key
            ctx.go_next()

            value_tk = ctx.current_token()
            if (
                    YamlParseToken.line(key_tk) == YamlParseToken.line(value_tk) and
                    YamlParseToken.type(value_tk) == YamlTokenType.SEQUENCE_ENTRY
            ):
                return YamlSyntaxError(
                    'block sequence entries are not allowed in this context',
                    YamlParseToken.raw_token(value_tk),
                )

            ctx = ctx.with_child(self.map_key_text(key))
            value = self.parse_map_value(ctx, key, check.not_none(check.not_none(key_tk.group).last()))
            if isinstance(value, YamlError):
                return value

            node1 = YamlNodeMakers.new_mapping_value_node(
                ctx,
                check.not_none(check.not_none(key_tk.group).last()),
                None,
                key,
                value,
            )
            if isinstance(node1, YamlError):
                return node1

            key_value_node = node1

        map_node = YamlNodeMakers.new_mapping_node(
            ctx,
            YamlParseToken(token=key_value_node.get_token()),
            False,
            key_value_node,
        )
        if isinstance(map_node, YamlError):
            return map_node

        tk: ta.Optional[YamlParseToken]
        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        else:
            tk = ctx.current_token()

        while YamlParseToken.column(tk) == YamlParseToken.column(key_tk):
            typ = YamlParseToken.type(tk)
            if ctx.is_flow and typ == YamlTokenType.SEQUENCE_END:
                # [
                # key: value
                # ] <=
                break
            if not self.is_map_token(check.not_none(tk)):
                return YamlSyntaxError('non-map value is specified', YamlParseToken.raw_token(tk))
            cm = self.parse_head_comment(ctx)
            if typ == YamlTokenType.MAPPING_END:
                # a: {
                #  b: c
                # } <=
                ctx.go_next()
                break
            node2 = self.parse_map(ctx)
            if isinstance(node2, YamlError):
                return node2
            if len(node2.values) != 0:
                if (err := yaml_set_head_comment(cm, node2.values[0])) is not None:
                    return err
            map_node.values.extend(node2.values)
            if node2.foot_comment is not None:
                map_node.values[len(map_node.values) - 1].foot_comment = node2.foot_comment
            tk = ctx.current_token()

        if ctx.is_comment():
            if YamlParseToken.column(key_tk) <= YamlParseToken.column(ctx.current_token()):
                # If the comment is in the same or deeper column as the last element column in map value,
                # treat it as a footer comment for the last element.
                if len(map_node.values) == 1:
                    map_node.values[0].foot_comment = self.parse_foot_comment(ctx, YamlParseToken.column(key_tk))
                    BaseYamlNode.set_path(map_node.values[0].foot_comment, map_node.values[0].key.get_path())
                else:
                    map_node.foot_comment = self.parse_foot_comment(ctx, YamlParseToken.column(key_tk))
                    BaseYamlNode.set_path(map_node.foot_comment, map_node.get_path())

        return map_node

    def validate_map_key_value_next_token(self, ctx: YamlParsingContext, key_tk, tk: ta.Optional[YamlParseToken]) -> ta.Optional[YamlError]:  # noqa
        if tk is None:
            return None
        if tk.column() <= key_tk.column():
            return None
        if ctx.is_comment():
            return None
        if (
                ctx.is_flow and
                (tk.type() == YamlTokenType.COLLECT_ENTRY or tk.type() == YamlTokenType.SEQUENCE_END)
        ):
            return None
        # a: b
        #  c <= this token is invalid.
        return YamlSyntaxError('value is not allowed in this context. map key-value is pre-defined', tk.raw_token())

    def is_map_token(self, tk: YamlParseToken) -> bool:
        if tk.group is None:
            return tk.type() == YamlTokenType.MAPPING_START or tk.type() == YamlTokenType.MAPPING_END
        g = tk.group
        return g.type == YamlParseTokenGroupType.MAP_KEY or g.type == YamlParseTokenGroupType.MAP_KEY_VALUE

    def parse_map_key_value(
            self,
            ctx: YamlParsingContext,
            g: YamlParseTokenGroup,
            entry_tk: ta.Optional[YamlParseToken],
    ) -> YamlErrorOr[MappingValueYamlNode]:
        if g.type != YamlParseTokenGroupType.MAP_KEY_VALUE:
            return YamlSyntaxError('unexpected map key-value pair', g.raw_token())
        if check.not_none(g.first()).group is None:
            return YamlSyntaxError('unexpected map key', g.raw_token())
        key_group = check.not_none(check.not_none(g.first()).group)
        key = self.parse_map_key(ctx.with_group(key_group), key_group)
        if isinstance(key, YamlError):
            return key

        c = ctx.with_child(self.map_key_text(key))
        value = self.parse_token(c, g.last())
        if isinstance(value, YamlError):
            return value
        return YamlNodeMakers.new_mapping_value_node(c, check.not_none(key_group.last()), entry_tk, key, value)

    def parse_map_key(self, ctx: YamlParsingContext, g: YamlParseTokenGroup) -> YamlErrorOr[MapKeyYamlNode]:
        if g.type != YamlParseTokenGroupType.MAP_KEY:
            return YamlSyntaxError('unexpected map key', g.raw_token())

        if YamlParseToken.type(g.first()) == YamlTokenType.MAPPING_KEY:
            map_key_tk = check.not_none(g.first())
            if map_key_tk.group is not None:
                ctx = ctx.with_group(map_key_tk.group)
            key0 = YamlNodeMakers.new_mapping_key_node(ctx, map_key_tk)
            if isinstance(key0, YamlError):
                return key0
            ctx.go_next()  # skip mapping key token
            if ctx.is_token_not_found():
                return YamlSyntaxError('could not find value for mapping key', YamlParseToken.raw_token(map_key_tk))

            scalar0 = self.parse_scalar_value(ctx, ctx.current_token())
            if isinstance(scalar0, YamlError):
                return scalar0
            key0.value = scalar0
            key_text = self.map_key_text(scalar0)
            key_path = ctx.with_child(key_text).path
            key0.set_path(key_path)
            if (err := self.validate_map_key(
                    ctx,
                    check.not_none(key0.get_token()),
                    key_path,
                    check.not_none(g.last()),
            )) is not None:
                return err
            self.path_map[key_path] = key0
            return key0
        if YamlParseToken.type(g.last()) != YamlTokenType.MAPPING_VALUE:
            return YamlSyntaxError("expected map key-value delimiter ':'", YamlParseToken.raw_token(g.last()))

        scalar1 = self.parse_scalar_value(ctx, g.first())
        if isinstance(scalar1, YamlError):
            return scalar1
        if not isinstance(scalar1, MapKeyYamlNode):
            # FIXME: not possible
            return YamlSyntaxError(
                'cannot take map-key node',
                check.not_none(scalar1).get_token(),
            )
        key1: MapKeyYamlNode = ta.cast(MapKeyYamlNode, scalar1)
        key_text = self.map_key_text(key1)
        key_path = ctx.with_child(key_text).path
        key1.set_path(key_path)
        if (err := self.validate_map_key(
                ctx,
                check.not_none(key1.get_token()),
                key_path,
                check.not_none(g.last()),
        )) is not None:
            return err
        self.path_map[key_path] = key1
        return key1

    def validate_map_key(
            self,
            ctx: YamlParsingContext,
            tk: YamlToken,
            key_path: str,
            colon_tk: YamlParseToken,
    ) -> ta.Optional[YamlError]:
        if not self.allow_duplicate_map_key:
            if (n := self.path_map.get(key_path)) is not None:
                pos = check.not_none(n.get_token()).position
                return YamlSyntaxError(
                    f'mapping key {tk.value!r} already defined at [{pos.line:d}:{pos.column:d}]',
                    tk,
                )
        origin = self.remove_left_white_space(tk.origin)
        if ctx.is_flow:
            if tk.type == YamlTokenType.STRING:
                origin = self.remove_right_white_space(origin)
                if tk.position.line + self.new_line_character_num(origin) != colon_tk.line():
                    return YamlSyntaxError('map key definition includes an implicit line break', tk)
            return None
        if (
                tk.type != YamlTokenType.STRING and
                tk.type != YamlTokenType.SINGLE_QUOTE and
                tk.type != YamlTokenType.DOUBLE_QUOTE
        ):
            return None
        if self.exists_new_line_character(origin):
            return YamlSyntaxError('unexpected key name', tk)
        return None

    def remove_left_white_space(self, src: str) -> str:
        # CR or LF or CRLF
        return src.lstrip(' \r\n')

    def remove_right_white_space(self, src: str) -> str:
        # CR or LF or CRLF
        return src.rstrip(' \r\n')

    def exists_new_line_character(self, src: str) -> bool:
        return self.new_line_character_num(src) > 0

    def new_line_character_num(self, src: str) -> int:
        num = 0
        i = -1
        while True:
            i += 1
            if not (i < len(src)):
                break
            if src[i] == '\r':
                if len(src) > i + 1 and src[i + 1] == '\n':
                    i += 1
                num += 1
            elif src[i] == '\n':
                num += 1
        return num

    def map_key_text(self, n: ta.Optional[YamlNode]) -> str:
        if n is None:
            return ''
        nn = n
        if isinstance(nn, MappingKeyYamlNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, TagYamlNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, AnchorYamlNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, AliasYamlNode):
            return ''
        return check.not_none(n.get_token()).value

    def parse_map_value(
            self,
            ctx: YamlParsingContext,
            key: MapKeyYamlNode,
            colon_tk: YamlParseToken,
    ) -> YamlErrorOr[YamlNode]:
        tk = ctx.current_token()
        if tk is None:
            return YamlNodeMakers.new_null_node(ctx, ctx.add_null_value_token(colon_tk))

        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        key_col = check.not_none(key.get_token()).position.column
        key_line = check.not_none(key.get_token()).position.line

        if (
            YamlParseToken.column(tk) != key_col and
            YamlParseToken.line(tk) == key_line and
            (
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.MAP_KEY or
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.MAP_KEY_VALUE
            )
        ):
            # a: b:
            #    ^
            #
            # a: b: c
            #    ^
            return YamlSyntaxError('mapping value is not allowed in this context', YamlParseToken.raw_token(tk))

        if YamlParseToken.column(tk) == key_col and self.is_map_token(check.not_none(tk)):
            # in this case,
            # ----
            # key: <value does not defined>
            # next
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(colon_tk))

        if (
                YamlParseToken.line(tk) == key_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) == key_col and
                self.is_map_token(check.not_none(ctx.next_token()))
        ):
            # in this case,
            # ----
            # key: &anchor
            # next
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        if (
                YamlParseToken.column(tk) <= key_col and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME
        ):
            # key: <value does not defined>
            # &anchor
            return YamlSyntaxError('anchor is not allowed in this context', YamlParseToken.raw_token(tk))
        if YamlParseToken.column(tk) <= key_col and YamlParseToken.type(tk) == YamlTokenType.TAG:
            # key: <value does not defined>
            # !!tag
            return YamlSyntaxError('tag is not allowed in this context', YamlParseToken.raw_token(tk))

        if YamlParseToken.column(tk) < key_col:
            # in this case,
            # ----
            #   key: <value does not defined>
            # next
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(colon_tk))

        if (
                YamlParseToken.line(tk) == key_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) < key_col
        ):
            # in this case,
            # ----
            #   key: &anchor
            # next
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        value = self.parse_token(ctx, ctx.current_token())
        if isinstance(value, YamlError):
            return value
        if (err := self.validate_anchor_value_in_map_or_seq(value, key_col)) is not None:
            return err
        return value

    def validate_anchor_value_in_map_or_seq(self, value: YamlNode, col: int) -> ta.Optional[YamlError]:
        if not isinstance(value, AnchorYamlNode):
            return None
        anchor: AnchorYamlNode = value
        if not isinstance(anchor.value, TagYamlNode):
            return None
        tag: TagYamlNode = anchor.value
        anchor_tk = anchor.get_token()
        tag_tk = tag.get_token()

        if anchor_tk.position.line == tag_tk.position.line:
            # key:
            #   &anchor !!tag
            #
            # - &anchor !!tag
            return None

        if tag_tk.position.column <= col:
            # key: &anchor
            # !!tag
            #
            # - &anchor
            # !!tag
            return YamlSyntaxError('tag is not allowed in this context', tag_tk)
        return None

    def parse_anchor(self, ctx: YamlParsingContext, g: YamlParseTokenGroup) -> YamlErrorOr[AnchorYamlNode]:
        anchor_name_group = check.not_none(check.not_none(g.first()).group)
        anchor = self.parse_anchor_name(ctx.with_group(anchor_name_group))
        if isinstance(anchor, YamlError):
            return anchor
        ctx.go_next()
        if ctx.is_token_not_found():
            return YamlSyntaxError('could not find anchor value', anchor.get_token())

        value = self.parse_token(ctx, ctx.current_token())
        if isinstance(value, YamlError):
            return value
        if isinstance(value, AnchorYamlNode):
            return YamlSyntaxError('anchors cannot be used consecutively', value.get_token())
        anchor.value = value
        return anchor

    def parse_anchor_name(self, ctx: YamlParsingContext) -> YamlErrorOr[AnchorYamlNode]:
        anchor = YamlNodeMakers.new_anchor_node(ctx, ctx.current_token())
        if isinstance(anchor, YamlError):
            return anchor
        ctx.go_next()
        if ctx.is_token_not_found():
            return YamlSyntaxError('could not find anchor value', anchor.get_token())

        anchor_name = self.parse_scalar_value(ctx, ctx.current_token())
        if isinstance(anchor_name, YamlError):
            return anchor_name
        if anchor_name is None:
            return YamlSyntaxError(
                'unexpected anchor. anchor name is not scalar value',
                YamlParseToken.raw_token(ctx.current_token()),
            )
        anchor.name = anchor_name
        return anchor

    def parse_alias(self, ctx: YamlParsingContext) -> YamlErrorOr[AliasYamlNode]:
        alias = YamlNodeMakers.new_alias_node(ctx, ctx.current_token())
        if isinstance(alias, YamlError):
            return alias
        ctx.go_next()
        if ctx.is_token_not_found():
            return YamlSyntaxError('could not find alias value', alias.get_token())

        alias_name = self.parse_scalar_value(ctx, ctx.current_token())
        if isinstance(alias_name, YamlError):
            return alias_name
        if alias_name is None:
            return YamlSyntaxError(
                'unexpected alias. alias name is not scalar value',
                YamlParseToken.raw_token(ctx.current_token()),
            )
        alias.value = alias_name
        return alias

    def parse_literal(self, ctx: YamlParsingContext) -> YamlErrorOr[LiteralYamlNode]:
        node = YamlNodeMakers.new_literal_node(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip literal/folded token

        tk = ctx.current_token()
        if tk is None:
            value0 = YamlNodeMakers.new_string_node(
                ctx,
                YamlParseToken(token=yaml_new_token('', '', node.start.position)),
            )
            if isinstance(value0, YamlError):
                return value0
            node.value = value0
            return node
        value1 = self.parse_token(ctx, tk)
        if isinstance(value1, YamlError):
            return value1
        if not isinstance(s := value1, StringYamlNode):
            return YamlSyntaxError('unexpected token. required string token', value1.get_token())
        node.value = s
        return node

    def parse_scalar_tag(self, ctx: YamlParsingContext) -> YamlErrorOr[TagYamlNode]:
        tag = self.parse_tag(ctx)
        if isinstance(tag, YamlError):
            return tag
        if tag.value is None:
            return YamlSyntaxError('specified not scalar tag', tag.get_token())
        if not isinstance(tag.value, ScalarYamlNode):
            return YamlSyntaxError('specified not scalar tag', tag.get_token())
        return tag

    def parse_tag(self, ctx: YamlParsingContext) -> YamlErrorOr[TagYamlNode]:
        tag_tk = ctx.current_token()
        tag_raw_tk = YamlParseToken.raw_token(tag_tk)
        node = YamlNodeMakers.new_tag_node(ctx, tag_tk)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()

        comment = self.parse_head_comment(ctx)

        tag_value: YamlNode
        if self.secondary_tag_directive is not None:
            value0 = YamlNodeMakers.new_string_node(ctx, ctx.current_token())
            if isinstance(value0, YamlError):
                return value0
            tag_value = value0
            node.directive = self.secondary_tag_directive
        else:
            value1 = self.parse_tag_value(ctx, check.not_none(tag_raw_tk), ctx.current_token())
            if isinstance(value1, YamlError):
                return value1
            tag_value = check.not_none(value1)
        if (err := yaml_set_head_comment(comment, tag_value)) is not None:
            return err
        node.value = tag_value
        return node

    def parse_tag_value(
            self,
            ctx: YamlParsingContext,
            tag_raw_tk: YamlToken,
            tk: ta.Optional[YamlParseToken],
    ) -> YamlErrorOr[ta.Optional[YamlNode]]:
        if tk is None:
            return YamlNodeMakers.new_null_node(ctx, ctx.create_implicit_null_token(YamlParseToken(token=tag_raw_tk)))
        if tag_raw_tk.value in (
                YamlReservedTagKeywords.MAPPING,
                YamlReservedTagKeywords.SET,
        ):
            if not self.is_map_token(tk):
                return YamlSyntaxError('could not find map', tk.raw_token())
            if tk.type() == YamlTokenType.MAPPING_START:
                return self.parse_flow_map(ctx.with_flow(True))
            return self.parse_map(ctx)
        elif tag_raw_tk.value in (
                YamlReservedTagKeywords.INTEGER,
                YamlReservedTagKeywords.FLOAT,
                YamlReservedTagKeywords.STRING,
                YamlReservedTagKeywords.BINARY,
                YamlReservedTagKeywords.TIMESTAMP,
                YamlReservedTagKeywords.BOOLEAN,
                YamlReservedTagKeywords.NULL,
        ):
            if tk.group_type() == YamlParseTokenGroupType.LITERAL or tk.group_type() == YamlParseTokenGroupType.FOLDED:
                return self.parse_literal(ctx.with_group(check.not_none(tk.group)))
            elif tk.type() == YamlTokenType.COLLECT_ENTRY or tk.type() == YamlTokenType.MAPPING_VALUE:
                return YamlNodeMakers.new_tag_default_scalar_value_node(ctx, tag_raw_tk)
            scalar = self.parse_scalar_value(ctx, tk)
            if isinstance(scalar, YamlError):
                return scalar
            ctx.go_next()
            return scalar
        elif tag_raw_tk.value in (
                YamlReservedTagKeywords.SEQUENCE,
                YamlReservedTagKeywords.ORDERED_MAP,
        ):
            if tk.type() == YamlTokenType.SEQUENCE_START:
                return self.parse_flow_sequence(ctx.with_flow(True))
            return self.parse_sequence(ctx)
        return self.parse_token(ctx, tk)

    def parse_flow_sequence(self, ctx: YamlParsingContext) -> YamlErrorOr[SequenceYamlNode]:
        node = YamlNodeMakers.new_sequence_node(ctx, ctx.current_token(), True)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip SequenceStart token

        is_first = True
        while ctx.next():
            tk = ctx.current_token()
            if YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_END:
                node.end = YamlParseToken.raw_token(tk)
                break

            entry_tk: ta.Optional[YamlParseToken] = None
            if YamlParseToken.type(tk) == YamlTokenType.COLLECT_ENTRY:
                if is_first:
                    return YamlSyntaxError("expected sequence element, but found ','", YamlParseToken.raw_token(tk))
                entry_tk = tk
                ctx.go_next()
            elif not is_first:
                return YamlSyntaxError("',' or ']' must be specified", YamlParseToken.raw_token(tk))

            if YamlParseToken.type(tk := ctx.current_token()) == YamlTokenType.SEQUENCE_END:
                # this case is here: "[ elem, ]".
                # In this case, ignore the last element and break sequence parsing.
                node.end = YamlParseToken.raw_token(tk)
                break

            if ctx.is_token_not_found():
                break

            ctx = ctx.with_index(len(node.values))
            value = self.parse_token(ctx, ctx.current_token())
            if isinstance(value, YamlError):
                return value
            node.values.append(value)
            seq_entry = yaml_sequence_entry(
                entry_tk.raw_token() if entry_tk is not None else None,
                value,
                None,
            )
            if (err := yaml_set_line_comment(ctx, seq_entry, entry_tk)) is not None:
                return err
            seq_entry.set_path(ctx.path)
            node.entries.append(seq_entry)

            is_first = False
        if node.end is None:
            return YamlSyntaxError("sequence end token ']' not found", node.start)

        # set ine comment if exists. e.g.) ] # comment
        if (err := yaml_set_line_comment(ctx, node, ctx.current_token())) is not None:
            return err
        ctx.go_next()  # skip sequence end token.
        return node

    def parse_sequence(self, ctx: YamlParsingContext) -> YamlErrorOr[SequenceYamlNode]:
        seq_tk = ctx.current_token()
        seq_node = YamlNodeMakers.new_sequence_node(ctx, seq_tk, False)
        if isinstance(seq_node, YamlError):
            return seq_node

        tk = seq_tk
        while (
                YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_ENTRY and
                YamlParseToken.column(tk) == YamlParseToken.column(seq_tk)
        ):
            head_comment = self.parse_head_comment(ctx)
            ctx.go_next()  # skip sequence entry token

            ctx = ctx.with_index(len(seq_node.values))
            value = self.parse_sequence_value(ctx, check.not_none(seq_tk))
            if isinstance(value, YamlError):
                return value
            seq_entry = yaml_sequence_entry(YamlParseToken.raw_token(seq_tk), value, head_comment)
            if (err := yaml_set_line_comment(ctx, seq_entry, seq_tk)) is not None:
                return err
            seq_entry.set_path(ctx.path)
            seq_node.value_head_comments.append(head_comment)
            seq_node.values.append(value)
            seq_node.entries.append(seq_entry)

            if ctx.is_comment():
                tk = ctx.next_not_comment_token()
            else:
                tk = ctx.current_token()
        if ctx.is_comment():
            if YamlParseToken.column(seq_tk) <= YamlParseToken.column(ctx.current_token()):
                # If the comment is in the same or deeper column as the last element column in sequence value,
                # treat it as a footer comment for the last element.
                seq_node.foot_comment = self.parse_foot_comment(ctx, YamlParseToken.column(seq_tk))
                if len(seq_node.values) != 0:
                    check.not_none(seq_node.foot_comment).set_path(
                        check.not_none(seq_node.values[len(seq_node.values) - 1]).get_path(),
                    )
        return seq_node

    def parse_sequence_value(self, ctx: YamlParsingContext, seq_tk: YamlParseToken) -> YamlErrorOr[YamlNode]:
        tk = ctx.current_token()
        if tk is None:
            return YamlNodeMakers.new_null_node(ctx, ctx.add_null_value_token(seq_tk))

        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        seq_col = seq_tk.column()
        seq_line = seq_tk.line()

        if YamlParseToken.column(tk) == seq_col and YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_ENTRY:
            # in this case,
            # ----
            # - <value does not defined>
            # -
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(seq_tk))

        if (
                YamlParseToken.line(tk) == seq_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) == seq_col and
                YamlParseToken.type(ctx.next_token()) == YamlTokenType.SEQUENCE_ENTRY
        ):
            # in this case,
            # ----
            # - &anchor
            # -
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        if (
                YamlParseToken.column(tk) <= seq_col and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME
        ):
            # - <value does not defined>
            # &anchor
            return YamlSyntaxError('anchor is not allowed in this sequence context', YamlParseToken.raw_token(tk))
        if YamlParseToken.column(tk) <= seq_col and YamlParseToken.type(tk) == YamlTokenType.TAG:
            # - <value does not defined>
            # !!tag
            return YamlSyntaxError('tag is not allowed in this sequence context', YamlParseToken.raw_token(tk))

        if (
                YamlParseToken.column(tk) < seq_col or
                (YamlParseToken.column(tk) == seq_col and YamlParseToken.line(tk) != seq_line)
        ):
            # in this case,
            # ----
            #   - <value does not defined>
            # next
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(seq_tk))

        if (
                YamlParseToken.line(tk) == seq_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) < seq_col
        ):
            # in this case,
            # ----
            #   - &anchor
            # next
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        value = self.parse_token(ctx, ctx.current_token())
        if isinstance(value, YamlError):
            return value
        if (err := self.validate_anchor_value_in_map_or_seq(value, seq_col)) is not None:
            return err
        return value

    def parse_directive(self, ctx: YamlParsingContext, g: YamlParseTokenGroup) -> YamlErrorOr[DirectiveYamlNode]:
        directive_name_group = check.not_none(check.not_none(g.first()).group)
        directive = self.parse_directive_name(ctx.with_group(directive_name_group))
        if isinstance(directive, YamlError):
            return directive

        if directive.name == 'YAML':
            if len(g.tokens) != 2:
                return YamlSyntaxError('unexpected format YAML directive', YamlParseToken.raw_token(g.first()))
            value_tk = g.tokens[1]
            value_raw_tk = check.not_none(value_tk.raw_token())
            value0 = value_raw_tk.value
            ver = YAML_VERSION_MAP.get(value0)
            if ver is None:
                return YamlSyntaxError(f'unknown YAML version {value0!r}', value_raw_tk)
            if self.yaml_version != '':
                return YamlSyntaxError('YAML version has already been specified', value_raw_tk)
            self.yaml_version = ver
            version_node = YamlNodeMakers.new_string_node(ctx, value_tk)
            if isinstance(version_node, YamlError):
                return version_node
            directive.values.append(version_node)

        elif directive.name == 'TAG':
            if len(g.tokens) != 3:
                return YamlSyntaxError('unexpected format TAG directive', YamlParseToken.raw_token(g.first()))
            tag_key = YamlNodeMakers.new_string_node(ctx, g.tokens[1])
            if isinstance(tag_key, YamlError):
                return tag_key
            if tag_key.value == '!!':
                self.secondary_tag_directive = directive
            tag_value = YamlNodeMakers.new_string_node(ctx, g.tokens[2])
            if isinstance(tag_value, YamlError):
                return tag_value
            directive.values.extend([tag_key, tag_value])

        elif len(g.tokens) > 1:
            for tk in g.tokens[1:]:
                value1 = YamlNodeMakers.new_string_node(ctx, tk)
                if isinstance(value1, YamlError):
                    return value1
                directive.values.append(value1)

        return directive

    def parse_directive_name(self, ctx: YamlParsingContext) -> YamlErrorOr[DirectiveYamlNode]:
        directive = YamlNodeMakers.new_directive_node(ctx, ctx.current_token())
        if isinstance(directive, YamlError):
            return directive
        ctx.go_next()
        if ctx.is_token_not_found():
            return YamlSyntaxError('could not find directive value', directive.get_token())

        directive_name = self.parse_scalar_value(ctx, ctx.current_token())
        if isinstance(directive_name, YamlError):
            return directive_name
        if directive_name is None:
            return YamlSyntaxError(
                'unexpected directive. directive name is not scalar value',
                YamlParseToken.raw_token(ctx.current_token()),
            )
        directive.name = directive_name
        return directive

    def parse_comment(self, ctx: YamlParsingContext) -> YamlErrorOr[ta.Optional[YamlNode]]:
        cm = self.parse_head_comment(ctx)
        if ctx.is_token_not_found():
            return cm
        node = self.parse_token(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        if (err := yaml_set_head_comment(cm, node)) is not None:
            return err
        return node

    def parse_head_comment(self, ctx: YamlParsingContext) -> ta.Optional[CommentGroupYamlNode]:
        tks: ta.List[ta.Optional[YamlToken]] = []
        while ctx.is_comment():
            tks.append(YamlParseToken.raw_token(ctx.current_token()))
            ctx.go_next()
        if len(tks) == 0:
            return None
        return YamlAsts.comment_group(tks)

    def parse_foot_comment(self, ctx: YamlParsingContext, col: int) -> ta.Optional[CommentGroupYamlNode]:
        tks: ta.List[ta.Optional[YamlToken]] = []
        while ctx.is_comment() and col <= YamlParseToken.column(ctx.current_token()):
            tks.append(YamlParseToken.raw_token(ctx.current_token()))
            ctx.go_next()
        if len(tks) == 0:
            return None
        return YamlAsts.comment_group(tks)


########################################
# ../../../omlish/http/coro/server/sockets.py


##


class CoroHttpServerSocketHandler(SocketHandler_):
    def __init__(
            self,
            server_factory: CoroHttpServerFactory,
            *,
            keep_alive: bool = False,
            log_handler: ta.Optional[ta.Callable[[CoroHttpServer, CoroHttpIo.AnyLogIo], None]] = None,
    ) -> None:
        super().__init__()

        self._server_factory = server_factory
        self._keep_alive = keep_alive
        self._log_handler = log_handler

    def __call__(self, client_address: SocketAddress, fp: SocketIoPair) -> None:
        server = self._server_factory(client_address)

        pbr = PushbackReader(fp.r)

        if self._keep_alive:
            for i in itertools.count():  # noqa
                res = self._handle_one(server, fp, pbr)
                if res.close_reason is not None:
                    break

        else:
            self._handle_one(server, fp, pbr)

    def _handle_one(
            self,
            server: CoroHttpServer,
            fp: SocketIoPair,
            pbr: PushbackReader,
    ) -> CoroHttpServer.CoroHandleResult:
        gen = server.coro_handle()

        o = next(gen)
        while True:
            if isinstance(o, CoroHttpIo.AnyLogIo):
                i = None
                if self._log_handler is not None:
                    self._log_handler(server, o)

            elif isinstance(o, CoroHttpIo.ReadIo):
                i = pbr.read(check.not_none(o.sz))

            elif isinstance(o, CoroHttpIo.ReadLineIo):
                i = pbr.readline(o.sz)

            elif isinstance(o, CoroHttpIo.ReadUntilIo):
                i = pbr.readuntil(o.b, max_bytes=o.sz)

            elif isinstance(o, CoroHttpIo.WriteIo):
                i = None
                fp.w.write(o.data)
                fp.w.flush()

            else:
                raise TypeError(o)

            try:
                if i is not None:
                    o = gen.send(i)
                else:
                    o = next(gen)
            except StopIteration as e:
                return check.isinstance(e.value, CoroHttpServer.CoroHandleResult)


########################################
# ../../../omlish/logs/asyncs.py


##


class AsyncLoggerToLogger(Logger):
    def __init__(self, u: AsyncLogger) -> None:
        super().__init__()

        self._u = u

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        # Nope out early to avoid sync_await if possible - don't bother in the LoggerToAsyncLogger.
        if not self.is_enabled_for(ctx.must_get_info(LoggingContextInfos.Level).level):
            return

        # Note: we hardcode the stack offset of sync_await (which is 2 - sync_await + sync_await.thunk). In non-lite
        # code, lang.sync_await uses a cext if present to avoid being on the py stack, which would obviously complicate
        # this, but this is lite code so we will always have the non-c version.
        sync_await(
            self._u._log(  # noqa
                check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(3),
                msg,
                *args,
                **kwargs,
            ),
        )

    def _metric(self, m: LoggerMetric) -> None:
        sync_await(self._u._metric(m))  # noqa


class LoggerToAsyncLogger(AsyncLogger):
    def __init__(self, u: Logger) -> None:
        super().__init__()

        self._u = u

    def get_effective_level(self) -> LogLevel:
        return self._u.get_effective_level()

    async def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        self._u._log(  # noqa
            check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
            msg,
            *args,
            **kwargs,
        )

    async def _metric(self, m: LoggerMetric) -> None:
        self._u._metric(m)  # noqa


########################################
# ../../../omlish/logs/std/loggers.py


##


class StdLogger(Logger):
    def __init__(self, std: logging.Logger) -> None:
        super().__init__()

        self._std = std

    @property
    def std(self) -> logging.Logger:
        return self._std

    def is_enabled_for(self, level: LogLevel) -> bool:
        return self._std.isEnabledFor(level)

    def get_effective_level(self) -> LogLevel:
        return self._std.getEffectiveLevel()

    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
    ) -> None:
        if not self.is_enabled_for(ctx.must_get_info(LoggingContextInfos.Level).level):
            return

        ctx.set_basic(
            name=self._std.name,

            msg=msg,
            args=args,
        )

        ctx.capture()

        rec = LoggingContextLogRecord(_logging_context=ctx)

        self._std.handle(rec)

    def _metric(self, m: LoggerMetric) -> None:
        pass


########################################
# ../../../omlish/subprocesses/asyncs.py


##


class AbstractAsyncSubprocesses(BaseSubprocesses, Abstract):
    @abc.abstractmethod
    def run_(self, run: SubprocessRun) -> ta.Awaitable[SubprocessRunOutput]:
        raise NotImplementedError

    def run(
            self,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
            check: bool = False,
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> ta.Awaitable[SubprocessRunOutput]:
        return self.run_(SubprocessRun(
            cmd=cmd,
            input=input,
            timeout=timeout,
            check=check,
            capture_output=capture_output,
            kwargs=kwargs,
        ))

    #

    async def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        await self.run(
            *cmd,
            stdout=stdout,
            check=True,
            **kwargs,
        )

    async def check_output(
            self,
            *cmd: str,
            stdout: ta.Any = subprocess.PIPE,
            **kwargs: ta.Any,
    ) -> bytes:
        return check.not_none((await self.run(
            *cmd,
            stdout=stdout,
            check=True,
            **kwargs,
        )).stdout)

    async def check_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> str:
        return (await self.check_output(
            *cmd,
            **kwargs,
        )).decode().strip()

    #

    async def try_call(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bool:
        if isinstance(await self.async_try_fn(self.check_call, *cmd, **kwargs), Exception):
            return False
        else:
            return True

    async def try_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[bytes]:
        if isinstance(ret := await self.async_try_fn(self.check_output, *cmd, **kwargs), Exception):
            return None
        else:
            return ret

    async def try_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[str]:
        if (ret := await self.try_output(*cmd, **kwargs)) is None:
            return None
        else:
            return ret.decode().strip()


########################################
# ../../../omlish/subprocesses/sync.py
"""
TODO:
 - popen
 - route check_calls through run_?
"""


##


class AbstractSubprocesses(BaseSubprocesses, Abstract):
    @abc.abstractmethod
    def run_(self, run: SubprocessRun) -> SubprocessRunOutput:
        raise NotImplementedError

    def run(
            self,
            *cmd: str,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
            check: bool = False,
            capture_output: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> SubprocessRunOutput:
        return self.run_(SubprocessRun(
            cmd=cmd,
            input=input,
            timeout=timeout,
            check=check,
            capture_output=capture_output,
            kwargs=kwargs,
        ))

    #

    @abc.abstractmethod
    def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bytes:
        raise NotImplementedError

    #

    def check_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> str:
        return self.check_output(*cmd, **kwargs).decode().strip()

    #

    def try_call(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bool:
        if isinstance(self.try_fn(self.check_call, *cmd, **kwargs), Exception):
            return False
        else:
            return True

    def try_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[bytes]:
        if isinstance(ret := self.try_fn(self.check_output, *cmd, **kwargs), Exception):
            return None
        else:
            return ret

    def try_output_str(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> ta.Optional[str]:
        if (ret := self.try_output(*cmd, **kwargs)) is None:
            return None
        else:
            return ret.decode().strip()


##


class Subprocesses(AbstractSubprocesses):
    def run_(self, run: SubprocessRun) -> SubprocessRunOutput[subprocess.CompletedProcess]:
        with self.prepare_and_wrap(
                *run.cmd,
                input=run.input,
                timeout=run.timeout,
                check=run.check,
                capture_output=run.capture_output or False,
                **(run.kwargs or {}),
        ) as (cmd, kwargs):
            proc = subprocess.run(cmd, **kwargs)  # noqa

        return SubprocessRunOutput(
            proc=proc,

            returncode=proc.returncode,

            stdout=proc.stdout,  # noqa
            stderr=proc.stderr,  # noqa
        )

    #

    def check_call(
            self,
            *cmd: str,
            stdout: ta.Any = sys.stderr,
            **kwargs: ta.Any,
    ) -> None:
        with self.prepare_and_wrap(*cmd, stdout=stdout, **kwargs) as (cmd, kwargs):  # noqa
            subprocess.check_call(cmd, **kwargs)

    def check_output(
            self,
            *cmd: str,
            **kwargs: ta.Any,
    ) -> bytes:
        with self.prepare_and_wrap(*cmd, **kwargs) as (cmd, kwargs):  # noqa
            return subprocess.check_output(cmd, **kwargs)


##


subprocesses = Subprocesses()

SubprocessRun._DEFAULT_SUBPROCESSES = subprocesses  # noqa


########################################
# ../../dataserver/http.py
"""
TODO:
 - asyncio
 - chunked transfer - both output and urllib input
 - range headers
"""


##


class DataServerHttpHandler(HttpHandler_):
    DEFAULT_READ_CHUNK_SIZE = 0x10000

    def __init__(
            self,
            ps: DataServer,
            *,
            read_chunk_size: int = DEFAULT_READ_CHUNK_SIZE,
    ) -> None:
        super().__init__()

        self._ps = ps
        self._read_chunk_size = read_chunk_size

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        p_req = DataServerRequest(
            req.method,
            req.path,
        )

        p_resp = self._ps.handle(p_req)
        try:
            data: ta.Any
            if (p_body := p_resp.body) is not None:
                def stream_data():
                    try:
                        while (b := p_body.read(self._read_chunk_size)):
                            yield b
                    finally:
                        p_body.close()

                data = HttpHandlerResponseStreamedData(stream_data())

            else:
                data = None

            resp = HttpHandlerResponse(
                status=p_resp.status,
                headers=p_resp.headers,
                data=data,
                close_connection=True,
            )

            return resp

        except Exception:  # noqa
            p_resp.close()

            raise


########################################
# ../../oci/dataserver.py


##


def build_oci_repository_data_server_routes(
        repo_name: str,
        built_repo: BuiltOciImageIndexRepository,
) -> ta.List[DataServerRoute]:
    base_url_path = f'/v2/{repo_name}'

    repo_contents: ta.Dict[str, OciRepositoryBuilder.Blob] = {}

    repo_contents[f'{base_url_path}/manifests/latest'] = built_repo.blobs[built_repo.media_index_descriptor.digest]

    for blob in built_repo.blobs.values():
        repo_contents['/'.join([
            base_url_path,
            'manifests' if blob.media_type in OCI_MANIFEST_MEDIA_TYPES else 'blobs',
            blob.digest,
        ])] = blob

    #

    def build_blob_target(blob: OciRepositoryBuilder.Blob) -> ta.Optional[DataServerTarget]:  # noqa
        kw: dict = dict(
            content_type=check.non_empty_str(blob.media_type),
        )

        if isinstance(blob.data, BytesOciDataRef):
            return DataServerTarget.of(blob.data.data, **kw)

        elif isinstance(blob.data, FileOciDataRef):
            return DataServerTarget.of(file_path=blob.data.path, **kw)

        else:
            with open_oci_data_ref(blob.data) as f:
                data = f.read()

            return DataServerTarget.of(data, **kw)

    #

    return [
        DataServerRoute(
            paths=[path],
            target=target,
        )
        for path, blob in repo_contents.items()
        if (target := build_blob_target(blob)) is not None
    ]


########################################
# ../../../omlish/asyncs/asyncio/subprocesses.py


##


class AsyncioProcessCommunicator:
    def __init__(
            self,
            proc: asyncio.subprocess.Process,
            loop: ta.Optional[ta.Any] = None,
            *,
            log: ta.Optional[LoggerLike] = None,
    ) -> None:
        super().__init__()

        if loop is None:
            loop = asyncio.get_running_loop()

        self._proc = proc
        self._loop = loop
        self._log = log

        self._transport: asyncio.base_subprocess.BaseSubprocessTransport = check.isinstance(
            proc._transport,  # type: ignore  # noqa
            asyncio.base_subprocess.BaseSubprocessTransport,
        )

    @property
    def _debug(self) -> bool:
        return self._loop.get_debug()

    async def _feed_stdin(self, input: bytes) -> None:  # noqa
        stdin = check.not_none(self._proc.stdin)
        try:
            if input is not None:
                stdin.write(input)
                if self._debug and self._log is not None:
                    self._log.debug('%r communicate: feed stdin (%s bytes)', self, len(input))

            await stdin.drain()

        except (BrokenPipeError, ConnectionResetError) as exc:
            # communicate() ignores BrokenPipeError and ConnectionResetError. write() and drain() can raise these
            # exceptions.
            if self._debug and self._log is not None:
                self._log.debug('%r communicate: stdin got %r', self, exc)

        if self._debug and self._log is not None:
            self._log.debug('%r communicate: close stdin', self)

        stdin.close()

    async def _noop(self) -> None:
        return None

    async def _read_stream(self, fd: int) -> bytes:
        transport: ta.Any = check.not_none(self._transport.get_pipe_transport(fd))

        if fd == 2:
            stream = check.not_none(self._proc.stderr)
        else:
            check.equal(fd, 1)
            stream = check.not_none(self._proc.stdout)

        if self._debug and self._log is not None:
            name = 'stdout' if fd == 1 else 'stderr'
            self._log.debug('%r communicate: read %s', self, name)

        output = await stream.read()

        if self._debug and self._log is not None:
            name = 'stdout' if fd == 1 else 'stderr'
            self._log.debug('%r communicate: close %s', self, name)

        transport.close()

        return output

    class Communication(ta.NamedTuple):
        stdout: ta.Optional[bytes]
        stderr: ta.Optional[bytes]

    async def _communicate(
            self,
            input: ta.Any = None,  # noqa
    ) -> Communication:
        stdin_fut: ta.Any
        if self._proc.stdin is not None:
            stdin_fut = self._feed_stdin(input)
        else:
            stdin_fut = self._noop()

        stdout_fut: ta.Any
        if self._proc.stdout is not None:
            stdout_fut = self._read_stream(1)
        else:
            stdout_fut = self._noop()

        stderr_fut: ta.Any
        if self._proc.stderr is not None:
            stderr_fut = self._read_stream(2)
        else:
            stderr_fut = self._noop()

        stdin_res, stdout_res, stderr_res = await asyncio.gather(stdin_fut, stdout_fut, stderr_fut)

        await self._proc.wait()

        return AsyncioProcessCommunicator.Communication(stdout_res, stderr_res)

    async def communicate(
            self,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
    ) -> Communication:
        return await asyncio_maybe_timeout(self._communicate(input), timeout)


##


class AsyncioSubprocesses(AbstractAsyncSubprocesses):
    async def communicate(
            self,
            proc: asyncio.subprocess.Process,
            input: ta.Any = None,  # noqa
            timeout: TimeoutLike = None,
    ) -> ta.Tuple[ta.Optional[bytes], ta.Optional[bytes]]:
        return await AsyncioProcessCommunicator(proc).communicate(input, timeout)  # noqa

    #

    @contextlib.asynccontextmanager
    async def popen(
            self,
            *cmd: str,
            shell: bool = False,
            timeout: TimeoutLike = None,
            **kwargs: ta.Any,
    ) -> ta.AsyncGenerator[asyncio.subprocess.Process, None]:
        with self.prepare_and_wrap( *cmd, shell=shell, **kwargs) as (cmd, kwargs):  # noqa
            fac: ta.Any
            if shell:
                fac = functools.partial(
                    asyncio.create_subprocess_shell,
                    check.single(cmd),
                )
            else:
                fac = functools.partial(
                    asyncio.create_subprocess_exec,
                    *cmd,
                )

            proc: asyncio.subprocess.Process = await fac(**kwargs)
            try:
                yield proc

            finally:
                await asyncio_maybe_timeout(proc.wait(), timeout)

    #

    async def run_(self, run: SubprocessRun) -> SubprocessRunOutput[asyncio.subprocess.Process]:
        kwargs = dict(run.kwargs or {})

        if run.capture_output:
            kwargs.setdefault('stdout', subprocess.PIPE)
            kwargs.setdefault('stderr', subprocess.PIPE)

        proc: asyncio.subprocess.Process
        async with self.popen(*run.cmd, **kwargs) as proc:
            stdout, stderr = await self.communicate(proc, run.input, run.timeout)

        if run.check and proc.returncode:
            raise subprocess.CalledProcessError(
                proc.returncode,
                run.cmd,
                output=stdout,
                stderr=stderr,
            )

        return SubprocessRunOutput(
            proc=proc,

            returncode=check.isinstance(proc.returncode, int),

            stdout=stdout,
            stderr=stderr,
        )


asyncio_subprocesses = AsyncioSubprocesses()


########################################
# ../../../omlish/formats/yaml/goyaml/decoding.py
##
# MIT License
#
# Copyright (c) 2019 Masaaki Goshima
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##


##


class YamlDecodeContext:
    def __init__(self, values: ta.Optional[ta.Dict[ta.Any, ta.Any]] = None) -> None:
        super().__init__()

        self._values: ta.Dict[ta.Any, ta.Any] = values if values is not None else {}

    def with_value(self, key: ta.Any, value: ta.Any) -> 'YamlDecodeContext':
        return YamlDecodeContext({**self._values, key: value})

    def value(self, key: ta.Any) -> ta.Any:
        return self._values.get(key)

    #

    class _MergeKey:  # noqa
        pass

    def with_merge(self) -> 'YamlDecodeContext':
        return self.with_value(self._MergeKey, True)

    def is_merge(self) -> bool:
        if not isinstance(v := self.value(self._MergeKey), bool):
            return False

        return v

    #

    class _AnchorKey:  # noqa
        pass

    def with_anchor(self, name: str) -> 'YamlDecodeContext':
        anchor_map = self.get_anchor_map()
        new_map: ta.Dict[str, None] = {}
        new_map.update(anchor_map)
        new_map[name] = None
        return self.with_value(self._AnchorKey, new_map)

    def get_anchor_map(self) -> ta.Dict[str, None]:
        if not isinstance(v := self.value(self._AnchorKey), dict):
            return {}

        return v


##


# CommentPosition type of the position for comment.
class YamlCommentPosition(enum.IntEnum):
    HEAD = 0
    LINE = 1
    FOOT = 2


# Comment raw data for comment.
@dc.dataclass()
class YamlComment:
    texts: ta.List[str]
    position: YamlCommentPosition


# LineComment create a one-line comment for CommentMap.
def yaml_line_comment(text: str) -> YamlComment:
    return YamlComment(
        texts=[text],
        position=YamlCommentPosition.LINE,
    )


# HeadComment create a multiline comment for CommentMap.
def yaml_head_comment(*texts: str) -> YamlComment:
    return YamlComment(
        texts=list(texts),
        position=YamlCommentPosition.HEAD,
    )


# FootComment create a multiline comment for CommentMap.
def yaml_foot_comment(*texts: str) -> YamlComment:
    return YamlComment(
        texts=list(texts),
        position=YamlCommentPosition.FOOT,
    )


# CommentMap map of the position of the comment and the comment information.
class YamlCommentMap(ta.Dict[str, ta.List[YamlComment]]):
    pass


##


# MapItem is an item in a MapSlice.
@dc.dataclass()
class YamlMapItem:
    key: ta.Any
    value: ta.Any


# MapSlice encodes and decodes as a YAML map.
# The order of keys is preserved when encoding and decoding.
class YamlMapSlice(ta.List[YamlMapItem]):
    # ToMap convert to map[interface{}]interface{}.
    def to_map(self) -> ta.Dict[ta.Any, ta.Any]:
        return {item.key: item.value for item in self}


##


class YamlBytesReader(ta.Protocol):
    def read(self) -> bytes: ...


class ImmediateYamlBytesReader:
    def __init__(self, bs: bytes) -> None:
        self._bs = bs

    def read(self) -> bytes:
        bs = self._bs
        self._bs = b''
        return bs


##


class YamlDecodeOption(ta.Protocol):
    def __call__(self, d: 'YamlDecoder') -> ta.Optional[YamlError]: ...


##


class YamlDecodeErrors:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    EXCEEDED_MAX_DEPTH = yaml_error('exceeded max depth')


@dc.dataclass()
class DuplicateKeyYamlError(YamlError):
    msg: str
    token: YamlToken

    @property
    def message(self) -> str:
        return self.msg


##


# Decoder reads and decodes YAML values from an input stream.
class YamlDecoder:
    reader: YamlBytesReader
    reference_readers: ta.List[YamlBytesReader]
    anchor_node_map: ta.Dict[str, ta.Optional[YamlNode]]
    anchor_value_map: ta.Dict[str, ta.Any]
    comment_maps: ta.List[YamlCommentMap]
    to_comment_map: ta.Optional[YamlCommentMap] = None
    opts: ta.List[YamlDecodeOption]
    reference_files: ta.List[str]
    reference_dirs: ta.List[str]
    is_recursive_dir: bool = False
    is_resolved_reference: bool = False
    allow_duplicate_map_key: bool = False
    use_ordered_map: bool = False
    parsed_file: ta.Optional[YamlFile] = None
    stream_index: int = 0
    decode_depth: int = 0

    # NewDecoder returns a new decoder that reads from r.
    def __init__(self, r: YamlBytesReader, *opts: YamlDecodeOption) -> None:
        super().__init__()

        self.reader = r
        self.anchor_node_map = {}
        self.anchor_value_map = {}
        self.opts = list(opts)
        self.reference_readers = []
        self.reference_files = []
        self.reference_dirs = []
        self.is_recursive_dir = False
        self.is_resolved_reference = False
        self.allow_duplicate_map_key = False
        self.use_ordered_map = False

        self.comment_maps = []

    MAX_DECODE_DEPTH: ta.ClassVar[int] = 10000

    def step_in(self) -> None:
        self.decode_depth += 1

    def step_out(self) -> None:
        self.decode_depth -= 1

    def is_exceeded_max_depth(self) -> bool:
        return self.decode_depth > self.MAX_DECODE_DEPTH

    def cast_to_float(self, v: ta.Any) -> ta.Any:
        if isinstance(v, float):
            return v
        elif isinstance(v, int):
            return float(v)
        elif isinstance(v, str):
            # if error occurred, return zero value
            try:
                return float(v)
            except ValueError:
                return 0
        return 0

    def map_key_node_to_string(self, ctx: YamlDecodeContext, node: MapKeyYamlNode) -> YamlErrorOr[str]:
        key = self.node_to_value(ctx, node)
        if isinstance(key, YamlError):
            return key
        if key is None:
            return 'null'
        if isinstance(key, str):
            return key
        return str(key)

    def set_to_map_value(
            self,
            ctx: YamlDecodeContext,
            node: YamlNode,
            m: ta.Dict[str, ta.Any],
    ) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            self.set_path_comment_map(node)
            if isinstance(n := node, MappingValueYamlNode):
                if n.key.is_merge_key():
                    value = self.get_map_node(n.value, True)
                    if isinstance(value, YamlError):
                        return value

                    it = value.map_range()
                    while it.next():
                        if (err := self.set_to_map_value(ctx, it.key_value(), m)) is not None:
                            return err

                else:
                    key = self.map_key_node_to_string(ctx, n.key)
                    if isinstance(key, YamlError):
                        return key

                    v = self.node_to_value(ctx, n.value)
                    if isinstance(v, YamlError):
                        return v

                    m[key] = v

            elif isinstance(n, MappingYamlNode):
                for value2 in n.values:
                    if (err := self.set_to_map_value(ctx, value2, m)) is not None:
                        return err

            elif isinstance(n, AnchorYamlNode):
                anchor_name = check.not_none(check.not_none(n.name).get_token()).value
                self.anchor_node_map[anchor_name] = n.value

            return None

        finally:
            self.step_out()

    def set_to_ordered_map_value(
            self,
            ctx: YamlDecodeContext,
            node: YamlNode,
            m: YamlMapSlice,
    ) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            self.set_path_comment_map(node)
            if isinstance(n := node, MappingValueYamlNode):
                if n.key.is_merge_key():
                    value = self.get_map_node(n.value, True)
                    if isinstance(value, YamlError):
                        return value

                    it = value.map_range()
                    while it.next():
                        if (err := self.set_to_ordered_map_value(ctx, it.key_value(), m)) is not None:
                            return err

                else:
                    key = self.map_key_node_to_string(ctx, n.key)
                    if isinstance(key, YamlError):
                        return key

                    value = self.node_to_value(ctx, n.value)
                    if isinstance(value, YamlError):
                        return value

                    m.append(YamlMapItem(key, value))

            elif isinstance(n, MappingYamlNode):
                for value2 in n.values:
                    if (err := self.set_to_ordered_map_value(ctx, value2, m)) is not None:
                        return err

            return None

        finally:
            self.step_out()

    def set_path_comment_map(self, node: ta.Optional[YamlNode]) -> None:
        if node is None:
            return

        if self.to_comment_map is None:
            return

        self.add_head_or_line_comment_to_map(node)
        self.add_foot_comment_to_map(node)

    def add_head_or_line_comment_to_map(self, node: YamlNode) -> None:
        if isinstance(node, SequenceYamlNode):
            self.add_sequence_node_comment_to_map(node)
            return

        comment_group = node.get_comment()
        if comment_group is None:
            return

        texts: ta.List[str] = []
        target_line = check.not_none(node.get_token()).position.line
        min_comment_line = 1_000_000_000  # FIXME lol
        for comment in comment_group.comments:
            if min_comment_line > check.not_none(comment.token).position.line:
                min_comment_line = check.not_none(comment.token).position.line

            texts.append(check.not_none(comment.token).value)

        if len(texts) == 0:
            return

        comment_path = node.get_path()
        if min_comment_line < target_line:
            if isinstance(n := node, MappingYamlNode):
                if len(n.values) != 0:
                    comment_path = n.values[0].key.get_path()

            elif isinstance(n, MappingValueYamlNode):
                comment_path = n.key.get_path()

            self.add_comment_to_map(comment_path, yaml_head_comment(*texts))
        else:
            self.add_comment_to_map(comment_path, yaml_line_comment(texts[0]))

    def add_sequence_node_comment_to_map(self, node: SequenceYamlNode) -> None:
        if len(node.value_head_comments) != 0:
            for idx, hc in enumerate(node.value_head_comments):
                if hc is None:
                    continue

                texts: ta.List[str] = []
                for comment in hc.comments:
                    texts.append(check.not_none(comment.token).value)

                if len(texts) != 0:
                    self.add_comment_to_map(check.not_none(node.values[idx]).get_path(), yaml_head_comment(*texts))

        first_elem_head_comment = node.get_comment()
        if first_elem_head_comment is not None:
            texts = []
            for comment in first_elem_head_comment.comments:
                texts.append(check.not_none(comment.token).value)

            if len(texts) != 0:
                if len(node.values) != 0:
                    self.add_comment_to_map(check.not_none(node.values[0]).get_path(), yaml_head_comment(*texts))

    def add_foot_comment_to_map(self, node: YamlNode) -> None:
        fc: ta.Optional[CommentGroupYamlNode] = None
        foot_comment_path = node.get_path()

        if isinstance(n := node, SequenceYamlNode):
            fc = n.foot_comment
            if n.foot_comment is not None:
                foot_comment_path = n.foot_comment.get_path()

        elif isinstance(n, MappingYamlNode):
            fc = n.foot_comment
            if n.foot_comment is not None:
                foot_comment_path = n.foot_comment.get_path()

        elif isinstance(n, MappingValueYamlNode):
            fc = n.foot_comment
            if n.foot_comment is not None:
                foot_comment_path = n.foot_comment.get_path()

        if fc is None:
            return

        texts: ta.List[str] = []
        for comment in fc.comments:
            texts.append(check.not_none(comment.token).value)

        if len(texts) != 0:
            self.add_comment_to_map(foot_comment_path, yaml_foot_comment(*texts))

    def add_comment_to_map(self, path: str, comment: YamlComment) -> None:
        tcm = check.not_none(self.to_comment_map)[path]
        for c in tcm:
            if c.position == comment.position:
                # already added same comment
                return

        tcm.append(comment)
        tcm.sort(key=lambda c: c.position)

    def node_to_value(self, ctx: YamlDecodeContext, node: YamlNode) -> YamlErrorOr[ta.Any]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            self.set_path_comment_map(node)

            if isinstance(n := node, NullYamlNode):
                return None

            elif isinstance(n, StringYamlNode):
                return n.get_value()

            elif isinstance(n, IntegerYamlNode):
                return n.get_value()

            elif isinstance(n, FloatYamlNode):
                return n.get_value()

            elif isinstance(n, BoolYamlNode):
                return n.get_value()

            elif isinstance(n, InfinityYamlNode):
                return n.get_value()

            elif isinstance(n, NanYamlNode):
                return n.get_value()

            elif isinstance(n, TagYamlNode):
                if n.directive is not None:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    if v is None:
                        return ''

                    return str(v)

                rtk = n.start.value
                if rtk == YamlReservedTagKeywords.TIMESTAMP:
                    t = self.cast_to_time(ctx, check.not_none(n.value))
                    if isinstance(t, YamlError):
                        return None
                    return t

                elif rtk == YamlReservedTagKeywords.INTEGER:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    try:
                        return int(str(v))
                    except ValueError:
                        return 0

                elif rtk == YamlReservedTagKeywords.FLOAT:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    return self.cast_to_float(v)

                elif rtk == YamlReservedTagKeywords.NULL:
                    return None

                elif rtk == YamlReservedTagKeywords.BINARY:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    if not isinstance(v, str):
                        return YamlSyntaxError(
                            f'cannot convert {str(v)!r} to string',
                            check.not_none(check.not_none(n.value).get_token()),
                        )
                    try:
                        return base64.b64decode(v)
                    except ValueError:
                        return None

                elif rtk == YamlReservedTagKeywords.BOOLEAN:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    l = str(v).lower()
                    if l in ('true', 't', '1', 'yes'):
                        return True
                    if l in ('false', 'f', '0', 'no'):
                        return False
                    return YamlSyntaxError(
                        f'cannot convert {v!r} to boolean',
                        check.not_none(check.not_none(n.value).get_token()),
                    )

                elif rtk == YamlReservedTagKeywords.STRING:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    if v is None:
                        return ''
                    return str(v)

                elif rtk == YamlReservedTagKeywords.MAPPING:
                    return self.node_to_value(ctx, check.not_none(n.value))

                else:
                    return self.node_to_value(ctx, check.not_none(n.value))

            elif isinstance(n, AnchorYamlNode):
                anchor_name = check.not_none(check.not_none(n.name).get_token()).value

                # To handle the case where alias is processed recursively, the result of alias can be set to nil in
                # advance.
                self.anchor_node_map[anchor_name] = None
                anchor_value = self.node_to_value(ctx.with_anchor(anchor_name), check.not_none(n.value))
                if isinstance(anchor_value, YamlError):
                    del self.anchor_node_map[anchor_name]
                    return anchor_value
                self.anchor_node_map[anchor_name] = n.value
                self.anchor_value_map[anchor_name] = anchor_value
                return anchor_value

            elif isinstance(n, AliasYamlNode):
                text = check.not_none(n.value).string()
                if text in ctx.get_anchor_map():
                    # self recursion.
                    return None
                try:
                    v = self.anchor_value_map[text]
                except KeyError:
                    pass
                else:
                    return v
                try:
                    node2 = self.anchor_node_map[text]
                except KeyError:
                    pass
                else:
                    return self.node_to_value(ctx, check.not_none(node2))
                return YamlSyntaxError(
                    f'could not find alias {text!r}',
                    check.not_none(check.not_none(n.value).get_token()),
                )

            elif isinstance(n, LiteralYamlNode):
                return check.not_none(n.value).get_value()

            elif isinstance(n, MappingKeyYamlNode):
                return self.node_to_value(ctx, check.not_none(n.value))

            elif isinstance(n, MappingValueYamlNode):
                if n.key.is_merge_key():
                    value = self.get_map_node(check.not_none(n.value), True)
                    if isinstance(value, YamlError):
                        return value
                    it = value.map_range()
                    if self.use_ordered_map:
                        m = YamlMapSlice()
                        while it.next():
                            if (err := self.set_to_ordered_map_value(ctx, it.key_value(), m)) is not None:
                                return err
                        return m
                    m2: ta.Dict[str, ta.Any] = {}
                    while it.next():
                        if (err := self.set_to_map_value(ctx, it.key_value(), m2)) is not None:
                            return err
                    return m2

                key = self.map_key_node_to_string(ctx, n.key)
                if isinstance(key, YamlError):
                    return key

                if self.use_ordered_map:
                    v = self.node_to_value(ctx, n.value)
                    if isinstance(v, YamlError):
                        return v
                    return YamlMapSlice([YamlMapItem(key, v)])

                v = self.node_to_value(ctx, n.value)
                if isinstance(v, YamlError):
                    return v

                return {key: v}

            elif isinstance(n, MappingYamlNode):
                if self.use_ordered_map:
                    m3 = YamlMapSlice()
                    for value2 in n.values:
                        if (err := self.set_to_ordered_map_value(ctx, value2, m3)) is not None:
                            return err
                    return m3

                m4: ta.Dict[str, ta.Any] = {}
                for value3 in n.values:
                    if (err := self.set_to_map_value(ctx, value3, m4)) is not None:
                        return err
                return m4

            elif isinstance(n, SequenceYamlNode):
                v2: ta.List[ta.Any] = []
                for value4 in n.values:
                    vv = self.node_to_value(ctx, check.not_none(value4))
                    if isinstance(vv, YamlError):
                        return vv
                    v2.append(vv)
                return v2

            return None

        finally:
            self.step_out()

    def cast_to_time(self, ctx: YamlDecodeContext, src: YamlNode) -> YamlErrorOr[datetime.datetime]:
        raise NotImplementedError

    def get_map_node(self, node: YamlNode, is_merge: bool) -> YamlErrorOr[MapYamlNode]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            if isinstance(n := node, MapYamlNode):
                return n

            elif isinstance(n, AnchorYamlNode):
                anchor_name = check.not_none(check.not_none(n.name).get_token()).value
                self.anchor_node_map[anchor_name] = n.value
                return self.get_map_node(check.not_none(n.value), is_merge)

            elif isinstance(n, AliasYamlNode):
                alias_name = check.not_none(check.not_none(n.value).get_token()).value
                node2 = self.anchor_node_map[alias_name]
                if node2 is None:
                    return yaml_error(f'cannot find anchor by alias name {alias_name}')
                return self.get_map_node(node2, is_merge)

            elif isinstance(n, SequenceYamlNode):
                if not is_merge:
                    return UnexpectedNodeTypeYamlError(node.type(), YamlNodeType.MAPPING, check.not_none(node.get_token()))  # noqa
                map_nodes: ta.List[MapYamlNode] = []
                for value in n.values:
                    map_node = self.get_map_node(check.not_none(value), False)
                    if isinstance(map_node, YamlError):
                        return map_node
                    map_nodes.append(map_node)
                return yaml_sequence_merge_value(*map_nodes)

            return UnexpectedNodeTypeYamlError(node.type(), YamlNodeType.MAPPING, check.not_none(node.get_token()))

        finally:
            self.step_out()

    def get_array_node(self, node: YamlNode) -> YamlErrorOr[ta.Optional[ArrayYamlNode]]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            if isinstance(node, NullYamlNode):
                return None

            if isinstance(anchor := node, AnchorYamlNode):
                if isinstance(array_node := anchor.value, ArrayYamlNode):
                    return array_node

                return UnexpectedNodeTypeYamlError(check.not_none(anchor.value).type(), YamlNodeType.SEQUENCE, check.not_none(node.get_token()))  # noqa

            if isinstance(alias := node, AliasYamlNode):
                alias_name = check.not_none(check.not_none(alias.value).get_token()).value
                node2 = self.anchor_node_map[alias_name]
                if node2 is None:
                    return yaml_error(f'cannot find anchor by alias name {alias_name}')
                if isinstance(array_node := node2, ArrayYamlNode):
                    return array_node
                return UnexpectedNodeTypeYamlError(node2.type(), YamlNodeType.SEQUENCE, check.not_none(node2.get_token()))  # noqa

            if not isinstance(array_node := node, ArrayYamlNode):
                return UnexpectedNodeTypeYamlError(node.type(), YamlNodeType.SEQUENCE, check.not_none(node.get_token()))  # noqa

            return array_node

        finally:
            self.step_out()

    def decode_value(self, ctx: YamlDecodeContext, src: YamlNode) -> YamlErrorOr[ta.Any]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            if src.type() == YamlNodeType.ANCHOR:
                anchor = check.isinstance(src, AnchorYamlNode)
                anchor_name = check.not_none(check.not_none(anchor.name).get_token()).value
                if isinstance(av := self.decode_value(ctx.with_anchor(anchor_name), check.not_none(anchor.value)), YamlError):  # noqa
                    return av
                self.anchor_value_map[anchor_name] = av
                return None

            src_val = self.node_to_value(ctx, src)
            if isinstance(src_val, YamlError):
                return src_val

            return src_val

        finally:
            self.step_out()

    def key_to_node_map(
        self,
        ctx: YamlDecodeContext,
        node: YamlNode,
        ignore_merge_key: bool,
        get_key_or_value_node: ta.Callable[[MapYamlNodeIter], YamlNode],
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            map_node = self.get_map_node(node, False)
            if isinstance(map_node, YamlError):
                return map_node
            key_map: ta.Dict[str, None] = {}
            key_to_node_map: ta.Dict[str, YamlNode] = {}
            map_iter = map_node.map_range()
            while map_iter.next():
                key_node = map_iter.key()
                if key_node.is_merge_key():
                    if ignore_merge_key:
                        continue
                    merge_map = self.key_to_node_map(ctx, map_iter.value(), ignore_merge_key, get_key_or_value_node)
                    if isinstance(merge_map, YamlError):
                        return merge_map
                    for k, v in merge_map.items():
                        if (err := self.validate_duplicate_key(key_map, k, v)) is not None:
                            return err
                        key_to_node_map[k] = v
                else:
                    key_val = self.node_to_value(ctx, key_node)
                    if isinstance(key_val, YamlError):
                        return key_val
                    if not isinstance(key := key_val, str):
                        return yaml_error('???')
                    if (err := self.validate_duplicate_key(key_map, key, key_node)) is not None:
                        return err
                    key_to_node_map[key] = get_key_or_value_node(map_iter)
            return key_to_node_map

        finally:
            self.step_out()

    def key_to_key_node_map(
        self,
        ctx: YamlDecodeContext,
        node: YamlNode,
        ignore_merge_key: bool,
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        m = self.key_to_node_map(ctx, node, ignore_merge_key, lambda node_map: node_map.key())
        if isinstance(m, YamlError):
            return m
        return m

    def key_to_value_node_map(
        self,
        ctx: YamlDecodeContext,
        node: YamlNode,
        ignore_merge_key: bool,
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        m = self.key_to_node_map(ctx, node, ignore_merge_key, lambda node_map: node_map.value())
        if isinstance(m, YamlError):
            return m
        return m

    # getParentMapTokenIfExists if the NodeType is a container type such as MappingType or SequenceType,
    # it is necessary to return the parent MapNode's colon token to represent the entire container.
    def get_parent_map_token_if_exists_for_validation_error(self, typ: YamlNodeType, tk: ta.Optional[YamlToken]) -> ta.Optional[YamlToken]:  # noqa
        if tk is None:
            return None
        if typ == YamlNodeType.MAPPING:
            # map:
            #   key: value
            #      ^ current token ( colon )
            if tk.prev is None:
                return tk
            key = tk.prev
            if key.prev is None:
                return tk
            return key.prev
        if typ == YamlNodeType.SEQUENCE:
            # map:
            #   - value
            #   ^ current token ( sequence entry )
            if tk.prev is None:
                return tk
            return tk.prev
        return tk

    def validate_duplicate_key(self, key_map: ta.Dict[str, None], key: ta.Any, key_node: YamlNode) -> ta.Optional[YamlError]:  # noqa
        if not isinstance(k := key, str):
            return None
        if not self.allow_duplicate_map_key:
            if k in key_map:
                return DuplicateKeyYamlError(f'duplicate key "{k}"', check.not_none(key_node.get_token()))
        key_map[k] = None
        return None

    def file_to_reader(self, file: str) -> YamlErrorOr[YamlBytesReader]:
        with open(file, 'rb') as f:
            bs = f.read()
        return ImmediateYamlBytesReader(bs)

    def is_yaml_file(self, file: str) -> bool:
        ext = file.rsplit('.', maxsplit=1)[-1]
        if ext == '.yml':
            return True
        if ext == '.yaml':
            return True
        return False

    def readers_under_dir(self, d: str) -> YamlErrorOr[ta.List[YamlBytesReader]]:
        pattern = f'{d}/*'
        matches = glob.glob(pattern)
        readers: ta.List[YamlBytesReader] = []
        for match in matches:
            if not self.is_yaml_file(match):
                continue
            if isinstance(reader := self.file_to_reader(match), YamlError):
                return reader
            readers.append(reader)
        return readers

    def readers_under_dir_recursive(self, d: str) -> YamlErrorOr[ta.List[YamlBytesReader]]:
        readers: ta.List[YamlBytesReader] = []
        for dp, _, fns in os.walk(d):
            for fn in fns:
                path = os.path.join(dp, fn)
                if not os.path.isfile(path):
                    continue
                if not self.is_yaml_file(path):
                    continue
                if isinstance(reader := self.file_to_reader(path), YamlError):
                    return reader
                readers.append(reader)
        return readers

    def resolve_reference(self, ctx: YamlDecodeContext) -> ta.Optional[YamlError]:
        for opt in self.opts:
            if (err := opt(self)) is not None:
                return err
        for file in self.reference_files:
            if isinstance(reader := self.file_to_reader(file), YamlError):
                return reader
            self.reference_readers.append(reader)
        for d in self.reference_dirs:
            if not self.is_recursive_dir:
                if isinstance(readers := self.readers_under_dir(d), YamlError):
                    return readers
                self.reference_readers.extend(readers)
            else:
                if isinstance(readers := self.readers_under_dir_recursive(d), YamlError):
                    return readers
                self.reference_readers.extend(readers)
        for reader in self.reference_readers:
            bs = reader.read()
            # assign new anchor definition to anchorMap
            if isinstance(err2 := self.parse(ctx, bs), YamlError):
                return err2
        self.is_resolved_reference = True
        return None

    def parse(self, ctx: YamlDecodeContext, bs: bytes) -> YamlErrorOr[YamlFile]:
        parse_mode: YamlParseMode = 0
        if self.to_comment_map is not None:
            parse_mode |= YAML_PARSE_COMMENTS
        opts: ta.List[YamlOption] = []
        if self.allow_duplicate_map_key:
            opts.append(yaml_allow_duplicate_map_key())
        if isinstance(f := yaml_parse_str(bs.decode(), parse_mode, *opts), YamlError):
            return f
        normalized_file = YamlFile()
        for doc in f.docs:
            # try to decode YamlNode to value and map anchor value to anchorMap
            if isinstance(v := self.node_to_value(ctx, check.not_none(doc.body)), YamlError):
                return v
            if v is not None or (doc.body is not None and doc.body.type() == YamlNodeType.NULL):
                normalized_file.docs.append(doc)
                cm = YamlCommentMap()
                cm.update(self.to_comment_map or {})
                self.comment_maps.append(cm)
            if self.to_comment_map is not None:
                self.to_comment_map.clear()
        return normalized_file

    def is_initialized(self) -> bool:
        return self.parsed_file is not None

    def decode_init(self, ctx: YamlDecodeContext) -> ta.Optional[YamlError]:
        if not self.is_resolved_reference:
            if (err := self.resolve_reference(ctx)) is not None:
                return err
        buf = self.reader.read()
        if isinstance(file := self.parse(ctx, buf), YamlError):
            return file
        self.parsed_file = file
        return None

    def _decode(self, ctx: YamlDecodeContext) -> YamlErrorOr[ta.Any]:
        self.decode_depth = 0
        self.anchor_value_map = {}
        pf = check.not_none(self.parsed_file)
        if len(pf.docs) == 0:
            # empty document.
            return None
        if len(pf.docs) <= self.stream_index:
            return EofYamlError()
        body = pf.docs[self.stream_index].body
        if body is None:
            return None
        if len(self.comment_maps) > self.stream_index:
            if (scm := self.comment_maps[self.stream_index]):
                check.not_none(self.to_comment_map).update(scm)
        if isinstance(v := self.decode_value(ctx, body), YamlError):
            return v
        self.stream_index += 1
        return v

    # Decode reads the next YAML-encoded value from its input
    # and stores it in the value pointed to by v.
    #
    # See the documentation for Unmarshal for details about the
    # conversion of YAML into a Go value.
    def decode(self) -> YamlErrorOr[ta.Any]:
        return self.decode_context(YamlDecodeContext())

    # decode_context reads the next YAML-encoded value from its input
    # and stores it in the value pointed to by v with Context.
    def decode_context(self, ctx: YamlDecodeContext) -> YamlErrorOr[ta.Any]:
        if self.is_initialized():
            if isinstance(v := self._decode(ctx), YamlError):
                return v
            return v
        if (err := self.decode_init(ctx)) is not None:
            return err
        if isinstance(v := self._decode(ctx), YamlError):
            return v
        return v

    # decode_from_node decodes node into the value pointed to by v.
    def decode_from_node(self, node: YamlNode) -> YamlErrorOr[ta.Any]:
        return self.decode_from_node_context(YamlDecodeContext(), node)

    # decode_from_node_context decodes node into the value pointed to by v with Context.
    def decode_from_node_context(self, ctx: YamlDecodeContext, node: YamlNode) -> YamlErrorOr[ta.Any]:
        if not self.is_initialized():
            if (err := self.decode_init(ctx)) is not None:
                return err
        # resolve references to the anchor on the same file
        if (err := self.node_to_value(ctx, node)) is not None:
            return err
        if isinstance(v := self.decode_value(ctx, node), YamlError):
            return v
        return v


##


def yaml_decode(s: str) -> ta.Any:
    d = YamlDecoder(ImmediateYamlBytesReader(s.encode()))
    if isinstance(v := d.decode(), YamlError):
        raise v
    return v


########################################
# ../../../omlish/http/coro/server/simple.py
"""
TODO:
 - logging
"""


@contextlib.contextmanager
def make_simple_http_server(
        bind: CanSocketBinder,
        handler: HttpHandler,
        *,
        keep_alive: bool = False,
        ssl_context: ta.Optional['ssl.SSLContext'] = None,
        ignore_ssl_errors: bool = False,
        executor: ta.Optional[cf.Executor] = None,
        use_threads: bool = False,
        **kwargs: ta.Any,
) -> ta.Iterator[SocketServer]:
    check.arg(not (executor is not None and use_threads))

    #

    with contextlib.ExitStack() as es:
        server_factory = functools.partial(
            CoroHttpServer,
            handler=handler,
        )

        socket_handler = CoroHttpServerSocketHandler(
            server_factory,
            keep_alive=keep_alive,
        )

        #

        server_handler: SocketServerHandler = SocketHandlerSocketServerHandler(
            socket_handler,
        )

        #

        if ssl_context is not None:
            server_handler = SocketWrappingSocketServerHandler(
                server_handler,
                SocketAndAddress.socket_wrapper(functools.partial(
                    ssl_context.wrap_socket,
                    server_side=True,
                )),
            )

        if ignore_ssl_errors:
            server_handler = SslErrorHandlingSocketServerHandler(
                server_handler,
            )

        #

        server_handler = StandardSocketServerHandler(
            server_handler,
        )

        #

        if executor is not None:
            server_handler = ExecutorSocketServerHandler(
                server_handler,
                executor,
            )

        elif use_threads:
            server_handler = es.enter_context(ThreadingSocketServerHandler(
                server_handler,
            ))

        #

        server = es.enter_context(SocketServer(
            SocketBinder.of(bind),
            server_handler,
            **kwargs,
        ))

        yield server


########################################
# ../../../omlish/logs/modules.py


##


def _get_module_std_logger(mod_globals: ta.Mapping[str, ta.Any]) -> logging.Logger:
    return logging.getLogger(mod_globals.get('__name__'))


def get_module_logger(mod_globals: ta.Mapping[str, ta.Any]) -> Logger:
    return StdLogger(_get_module_std_logger(mod_globals))


def get_module_async_logger(mod_globals: ta.Mapping[str, ta.Any]) -> AsyncLogger:
    return LoggerToAsyncLogger(get_module_logger(mod_globals))


def get_module_loggers(mod_globals: ta.Mapping[str, ta.Any]) -> ta.Tuple[Logger, AsyncLogger]:
    return (
        log := get_module_logger(mod_globals),
        LoggerToAsyncLogger(log),
    )


########################################
# ../cache.py
"""
TODO:
 - os.mtime, Config.purge_after_days
  - nice to have: get a total set of might-need keys ahead of time and keep those
  - okay: just purge after running
"""


CacheVersion = ta.NewType('CacheVersion', int)


log = get_module_logger(globals())  # noqa


##


class FileCache(Abstract):
    DEFAULT_CACHE_VERSION: ta.ClassVar[CacheVersion] = CacheVersion(CI_CACHE_VERSION)

    def __init__(
            self,
            *,
            version: ta.Optional[CacheVersion] = None,
    ) -> None:
        super().__init__()

        if version is None:
            version = self.DEFAULT_CACHE_VERSION
        check.isinstance(version, int)
        check.arg(version >= 0)
        self._version: CacheVersion = version

    @property
    def version(self) -> CacheVersion:
        return self._version

    #

    @abc.abstractmethod
    def get_file(self, key: str) -> ta.Awaitable[ta.Optional[str]]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_file(
            self,
            key: str,
            file_path: str,
            *,
            steal: bool = False,
    ) -> ta.Awaitable[str]:
        raise NotImplementedError


#


class DirectoryFileCache(FileCache):
    @dc.dataclass(frozen=True)
    class Config:
        dir: str

        no_create: bool = False
        no_purge: bool = False

        no_update_mtime: bool = False

        purge_max_age_s: ta.Optional[float] = None
        purge_max_size_b: ta.Optional[int] = None

    def __init__(
            self,
            config: Config,
            *,
            version: ta.Optional[CacheVersion] = None,
    ) -> None:  # noqa
        super().__init__(
            version=version,
        )

        self._config = config

    @property
    def dir(self) -> str:
        return self._config.dir

    #

    VERSION_FILE_NAME = '.ci-cache-version'

    def _iter_dir_contents(self) -> ta.Iterator[str]:
        for n in sorted(os.listdir(self.dir)):
            if n.startswith('.'):
                continue
            yield os.path.join(self.dir, n)

    @cached_nullary
    def setup_dir(self) -> None:
        version_file = os.path.join(self.dir, self.VERSION_FILE_NAME)

        if self._config.no_create:
            check.state(os.path.isdir(self.dir))

        elif not os.path.isdir(self.dir):
            os.makedirs(self.dir)
            with open(version_file, 'w') as f:
                f.write(f'{self._version}\n')
            return

        # NOTE: intentionally raises FileNotFoundError to refuse to use an existing non-cache dir as a cache dir.
        with open(version_file) as f:
            dir_version = int(f.read().strip())

        if dir_version == self._version:
            return

        if self._config.no_purge:
            raise RuntimeError(f'{dir_version=} != {self._version=}')

        dirs = [n for n in sorted(os.listdir(self.dir)) if os.path.isdir(os.path.join(self.dir, n))]
        if dirs:
            raise RuntimeError(
                f'Refusing to remove stale cache dir {self.dir!r} '
                f'due to present directories: {", ".join(dirs)}',
            )

        for fp in self._iter_dir_contents():
            check.state(os.path.isfile(fp))
            log.debug('Purging stale cache file: %s', fp)
            os.unlink(fp)

        os.unlink(version_file)

        with open(version_file, 'w') as f:
            f.write(str(self._version))

    #

    def purge(self, *, dry_run: bool = False) -> None:
        purge_max_age_s = self._config.purge_max_age_s
        purge_max_size_b = self._config.purge_max_size_b
        if self._config.no_purge or (purge_max_age_s is None and purge_max_size_b is None):
            return

        self.setup_dir()

        purge_min_mtime: ta.Optional[float] = None
        if purge_max_age_s is not None:
            purge_min_mtime = time.time() - purge_max_age_s

        dct: ta.Dict[str, os.stat_result] = {}
        for fp in self._iter_dir_contents():
            check.state(os.path.isfile(fp))
            dct[fp] = os.stat(fp)

        total_size_b = 0
        for fp, st in sorted(dct.items(), key=lambda t: -t[1].st_mtime):
            total_size_b += st.st_size

            purge = False
            if purge_min_mtime is not None and st.st_mtime < purge_min_mtime:
                purge = True
            if purge_max_size_b is not None and total_size_b >= purge_max_size_b:
                purge = True

            if not purge:
                continue

            log.debug('Purging cache file: %s', fp)
            if not dry_run:
                os.unlink(fp)

    #

    def get_cache_file_path(
            self,
            key: str,
    ) -> str:
        self.setup_dir()
        return os.path.join(self.dir, key)

    def format_incomplete_file(self, f: str) -> str:
        return os.path.join(os.path.dirname(f), f'_{os.path.basename(f)}.incomplete')

    #

    async def get_file(self, key: str) -> ta.Optional[str]:
        cache_file_path = self.get_cache_file_path(key)
        if not os.path.exists(cache_file_path):
            return None

        if not self._config.no_update_mtime:
            stat_info = os.stat(cache_file_path)
            os.utime(cache_file_path, (stat_info.st_atime, time.time()))

        return cache_file_path

    async def put_file(
            self,
            key: str,
            file_path: str,
            *,
            steal: bool = False,
    ) -> str:
        cache_file_path = self.get_cache_file_path(key)
        if steal:
            shutil.move(file_path, cache_file_path)
        else:
            shutil.copyfile(file_path, cache_file_path)
        return cache_file_path


##


class DataCache:
    @dc.dataclass(frozen=True)
    class Data(Abstract):
        pass

    @dc.dataclass(frozen=True)
    class BytesData(Data):
        data: bytes

    @dc.dataclass(frozen=True)
    class FileData(Data):
        file_path: str

    @dc.dataclass(frozen=True)
    class UrlData(Data):
        url: str

    #

    @abc.abstractmethod
    def get_data(self, key: str) -> ta.Awaitable[ta.Optional[Data]]:
        raise NotImplementedError

    @abc.abstractmethod
    def put_data(self, key: str, data: Data) -> ta.Awaitable[None]:
        raise NotImplementedError


#


@functools.singledispatch
async def read_data_cache_data(data: DataCache.Data) -> bytes:
    raise TypeError(data)


@read_data_cache_data.register
async def _(data: DataCache.BytesData) -> bytes:
    return data.data


@read_data_cache_data.register
async def _(data: DataCache.FileData) -> bytes:
    with open(data.file_path, 'rb') as f:  # noqa
        return f.read()


@read_data_cache_data.register
async def _(data: DataCache.UrlData) -> bytes:
    def inner() -> bytes:
        with urllib.request.urlopen(urllib.request.Request(  # noqa
            data.url,
        )) as resp:
            return resp.read()

    return await asyncio.get_running_loop().run_in_executor(None, inner)


#


class FileCacheDataCache(DataCache):
    def __init__(
            self,
            file_cache: FileCache,
    ) -> None:
        super().__init__()

        self._file_cache = file_cache

    async def get_data(self, key: str) -> ta.Optional[DataCache.Data]:
        if (file_path := await self._file_cache.get_file(key)) is None:
            return None

        return DataCache.FileData(file_path)

    async def put_data(self, key: str, data: DataCache.Data) -> None:
        steal = False

        if isinstance(data, DataCache.BytesData):
            file_path = make_temp_file()
            with open(file_path, 'wb') as f:  # noqa
                f.write(data.data)
            steal = True

        elif isinstance(data, DataCache.FileData):
            file_path = data.file_path

        elif isinstance(data, DataCache.UrlData):
            raise NotImplementedError

        else:
            raise TypeError(data)

        await self._file_cache.put_file(
            key,
            file_path,
            steal=steal,
        )


########################################
# ../docker/cmds.py


##


async def is_docker_image_present(image: str) -> bool:
    out = await asyncio_subprocesses.check_output(
        'docker',
        'images',
        '--format', 'json',
        image,
    )

    out_s = out.decode('utf-8').strip()
    if not out_s:
        return False

    json.loads(out_s)  # noqa
    return True


async def pull_docker_image(
        image: str,
) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'pull',
        image,
    )


async def build_docker_image(
        docker_file: str,
        *,
        tag: ta.Optional[str] = None,
        cwd: ta.Optional[str] = None,
        run_options: ta.Optional[ta.Sequence[str]] = None,
) -> str:
    with temp_file_context() as id_file:
        await asyncio_subprocesses.check_call(
            'docker',
            'build',
            '-f', os.path.abspath(docker_file),
            '--iidfile', id_file,
            *(['--tag', tag] if tag is not None else []),
            *(run_options or []),
            '.',
            **(dict(cwd=cwd) if cwd is not None else {}),
        )

        with open(id_file) as f:  # noqa
            image_id = check.single(f.read().strip().splitlines()).strip()

    return image_id


async def tag_docker_image(image: str, tag: str) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'tag',
        image,
        tag,
    )


async def delete_docker_tag(tag: str) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'rmi',
        tag,
    )


##


async def save_docker_tar_cmd(
        image: str,
        output_cmd: ShellCmd,
) -> None:
    cmd = dc.replace(output_cmd, s=f'docker save {image} | {output_cmd.s}')
    await cmd.run(asyncio_subprocesses.check_call)


async def save_docker_tar(
        image: str,
        tar_file: str,
) -> None:
    return await save_docker_tar_cmd(
        image,
        ShellCmd(f'cat > {shlex.quote(tar_file)}'),
    )


#


async def load_docker_tar_cmd(
        input_cmd: ShellCmd,
) -> str:
    cmd = dc.replace(input_cmd, s=f'{input_cmd.s} | docker load')

    out = (await cmd.run(asyncio_subprocesses.check_output)).decode()

    line = check.single(out.strip().splitlines())
    loaded = line.partition(':')[2].strip()
    return loaded


async def load_docker_tar(
        tar_file: str,
) -> str:
    return await load_docker_tar_cmd(ShellCmd(f'cat {shlex.quote(tar_file)}'))


##


async def ensure_docker_image_setup(
        image: str,
        *,
        cwd: ta.Optional[str] = None,
) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'run',
        '--rm',
        '--entrypoint', '/bin/true',  # FIXME: lol
        image,
        **(dict(cwd=cwd) if cwd is not None else {}),
    )


########################################
# ../docker/dataserver.py


##


@contextlib.asynccontextmanager
async def start_docker_port_relay(
        docker_port: int,
        host_port: int,
        **kwargs: ta.Any,
) -> ta.AsyncGenerator[None, None]:
    proc = await asyncio.create_subprocess_exec(*DockerPortRelay(
        docker_port,
        host_port,
        **kwargs,
    ).run_cmd())

    try:
        yield

    finally:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        await proc.wait()


##


class AsyncioManagedSimpleHttpServer(AsyncExitStacked):
    def __init__(
            self,
            port: int,
            handler: HttpHandler,
            *,
            temp_ssl: bool = False,
    ) -> None:
        super().__init__()

        self._port = port
        self._handler = handler

        self._temp_ssl = temp_ssl

        self._lock = threading.RLock()

        self._loop: ta.Optional[asyncio.AbstractEventLoop] = None
        self._thread: ta.Optional[threading.Thread] = None
        self._thread_exit_event = asyncio.Event()
        self._server: ta.Optional[SocketServer] = None

    @cached_nullary
    def _ssl_context(self) -> ta.Optional['ssl.SSLContext']:
        if not self._temp_ssl:
            return None

        ssl_cert = generate_temp_localhost_ssl_cert().cert  # FIXME: async blocking

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            keyfile=ssl_cert.key_file,
            certfile=ssl_cert.cert_file,
        )

        return ssl_context

    @contextlib.contextmanager
    def _make_server(self) -> ta.Iterator[SocketServer]:
        with make_simple_http_server(
                self._port,
                self._handler,
                ssl_context=self._ssl_context(),
                ignore_ssl_errors=True,
                use_threads=True,
        ) as server:
            yield server

    def _thread_main(self) -> None:
        try:
            check.none(self._server)
            with self._make_server() as server:
                self._server = server

                server.run()

        finally:
            check.not_none(self._loop).call_soon_threadsafe(self._thread_exit_event.set)

    def is_running(self) -> bool:
        return self._server is not None

    def shutdown(self) -> None:
        if (server := self._server) is not None:
            server.shutdown(block=False)

    async def run(self) -> None:
        with self._lock:
            check.none(self._loop)
            check.none(self._thread)
            check.state(not self._thread_exit_event.is_set())

            if self._temp_ssl:
                # Hit the ExitStack from this thread
                self._ssl_context()

            self._loop = check.not_none(asyncio.get_running_loop())
            self._thread = threading.Thread(
                target=self._thread_main,
                daemon=True,
            )
            self._thread.start()

        await self._thread_exit_event.wait()


##


class DockerDataServer(AsyncExitStacked):
    def __init__(
            self,
            port: int,
            data_server: DataServer,
            *,
            handler_log: ta.Optional[LoggerLike] = None,
            stop_event: ta.Optional[asyncio.Event] = None,
    ) -> None:
        super().__init__()

        self._port = port
        self._data_server = data_server

        self._handler_log = handler_log

        if stop_event is None:
            stop_event = asyncio.Event()
        self._stop_event = stop_event

    @property
    def stop_event(self) -> asyncio.Event:
        return self._stop_event

    async def run(self) -> None:
        # FIXME:
        #  - shared single server with updatable routes
        #  - get docker used ports with ns1
        #  - discover server port with get_available_port
        #  - discover relay port pair with get_available_ports
        # relay_port: ta.Optional[ta.Tuple[int, int]] = None

        relay_port: ta.Optional[int] = None
        if sys.platform == 'darwin':
            relay_port = self._port
            server_port = self._port + 1
        else:
            server_port = self._port

        #

        handler: HttpHandler = DataServerHttpHandler(self._data_server)

        if self._handler_log is not None:
            handler = LoggingHttpHandler(
                handler,
                self._handler_log,
            )

        #

        async with contextlib.AsyncExitStack() as es:
            if relay_port is not None:
                await es.enter_async_context(start_docker_port_relay(  # noqa
                    relay_port,
                    server_port,
                    intermediate_port=server_port + 1,
                ))

            async with AsyncioManagedSimpleHttpServer(
                    server_port,
                    handler,
                    temp_ssl=True,
            ) as server:
                server_run_task = asyncio.create_task(server.run())
                try:
                    await self._stop_event.wait()

                finally:
                    server.shutdown()
                    await server_run_task


########################################
# ../utils.py


##


def read_yaml_file(yaml_file: str) -> ta.Any:
    with open(yaml_file) as f:
        return yaml_decode(f.read())


##


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


########################################
# ../../../omlish/lite/timing.py


log = get_module_logger(globals())  # noqa


LogTimingContext.DEFAULT_LOG = log

log_timing_context = log_timing_context  # noqa


########################################
# ../compose.py
"""
TODO:
 - fix rmi - only when not referenced anymore
"""


##


def get_compose_service_dependencies(
        compose_file: str,
        service: str,
) -> ta.Dict[str, str]:
    compose_dct = read_yaml_file(compose_file)

    services = compose_dct['services']
    service_dct = services[service]

    out = {}
    for dep_service in service_dct.get('depends_on', []):
        dep_service_dct = services[dep_service]
        out[dep_service] = dep_service_dct['image']

    return out


##


class DockerComposeRun(AsyncExitStacked):
    @dc.dataclass(frozen=True)
    class Config:
        compose_file: str
        service: str

        image: str

        cmd: ShellCmd

        #

        run_options: ta.Optional[ta.Sequence[str]] = None

        cwd: ta.Optional[str] = None

        #

        no_dependencies: bool = False
        no_dependency_cleanup: bool = False

        #

        def __post_init__(self) -> None:
            check.not_isinstance(self.run_options, str)

    def __init__(self, cfg: Config) -> None:
        super().__init__()

        self._cfg = cfg

        self._subprocess_kwargs = {
            **(dict(cwd=self._cfg.cwd) if self._cfg.cwd is not None else {}),
        }

    #

    def _rewrite_compose_dct(self, in_dct: ta.Dict[str, ta.Any]) -> ta.Dict[str, ta.Any]:
        out = dict(in_dct)

        #

        in_services = in_dct['services']
        out['services'] = out_services = {}

        #

        in_service: dict = in_services[self._cfg.service]
        out_services[self._cfg.service] = out_service = dict(in_service)

        out_service['image'] = self._cfg.image

        for k in ['build', 'platform']:
            out_service.pop(k, None)

        #

        if not self._cfg.no_dependencies:
            depends_on = in_service.get('depends_on', [])

            for dep_service, in_dep_service_dct in list(in_services.items()):
                if dep_service not in depends_on:
                    continue

                out_dep_service: dict = dict(in_dep_service_dct)
                out_services[dep_service] = out_dep_service

                out_dep_service['ports'] = []

        else:
            out_service['depends_on'] = []

        #

        return out

    @cached_nullary
    def rewrite_compose_file(self) -> str:
        in_dct = read_yaml_file(self._cfg.compose_file)

        out_dct = self._rewrite_compose_dct(in_dct)

        #

        out_compose_file = make_temp_file()
        self._enter_context(defer(lambda: os.unlink(out_compose_file)))  # noqa

        compose_json = json_dumps_pretty(out_dct)

        with open(out_compose_file, 'w') as f:
            f.write(compose_json)

        return out_compose_file

    #

    async def _cleanup_dependencies(self) -> None:
        await asyncio_subprocesses.check_call(
            'docker',
            'compose',
            '-f', self.rewrite_compose_file(),
            'down',
        )

    async def run(self) -> None:
        compose_file = self.rewrite_compose_file()

        async with contextlib.AsyncExitStack() as es:
            if not (self._cfg.no_dependencies or self._cfg.no_dependency_cleanup):
                await es.enter_async_context(adefer(self._cleanup_dependencies()))  # noqa

            sh_cmd = ' '.join([
                'docker',
                'compose',
                '-f', compose_file,
                'run',
                '--rm',
                *itertools.chain.from_iterable(
                    ['-e', k]
                    for k in (self._cfg.cmd.env or [])
                ),
                *(self._cfg.run_options or []),
                self._cfg.service,
                'sh', '-c', shlex.quote(self._cfg.cmd.s),
            ])

            run_cmd = dc.replace(self._cfg.cmd, s=sh_cmd)

            await run_cmd.run(
                asyncio_subprocesses.check_call,
                **self._subprocess_kwargs,
            )


########################################
# ../docker/cache.py


##


@dc.dataclass(frozen=True)
class DockerCacheKey:
    prefixes: ta.Sequence[str]
    content: str

    def __post_init__(self) -> None:
        check.not_isinstance(self.prefixes, str)

    def append_prefix(self, *prefixes: str) -> 'DockerCacheKey':
        return dc.replace(self, prefixes=(*self.prefixes, *prefixes))

    SEPARATOR: ta.ClassVar[str] = '--'

    def __str__(self) -> str:
        return self.SEPARATOR.join([*self.prefixes, self.content])


##


class DockerCache(Abstract):
    @abc.abstractmethod
    def load_cache_docker_image(self, key: DockerCacheKey) -> ta.Awaitable[ta.Optional[str]]:
        raise NotImplementedError

    @abc.abstractmethod
    def save_cache_docker_image(self, key: DockerCacheKey, image: str) -> ta.Awaitable[None]:
        raise NotImplementedError


class DockerCacheImpl(DockerCache):
    def __init__(
            self,
            *,
            file_cache: ta.Optional[FileCache] = None,
    ) -> None:
        super().__init__()

        self._file_cache = file_cache

    async def load_cache_docker_image(self, key: DockerCacheKey) -> ta.Optional[str]:
        if self._file_cache is None:
            return None

        cache_file = await self._file_cache.get_file(str(key))
        if cache_file is None:
            return None

        get_cache_cmd = ShellCmd(f'cat {cache_file} | zstd -cd --long')

        return await load_docker_tar_cmd(get_cache_cmd)

    async def save_cache_docker_image(self, key: DockerCacheKey, image: str) -> None:
        if self._file_cache is None:
            return

        with temp_file_context() as tmp_file:
            write_tmp_cmd = ShellCmd(f'zstd > {tmp_file}')

            await save_docker_tar_cmd(image, write_tmp_cmd)

            await self._file_cache.put_file(str(key), tmp_file, steal=True)


########################################
# ../docker/repositories.py


##


class DockerImageRepositoryOpener(Abstract):
    @abc.abstractmethod
    def open_docker_image_repository(self, image: str) -> ta.AsyncContextManager[OciRepository]:
        raise NotImplementedError


#


class DockerImageRepositoryOpenerImpl(DockerImageRepositoryOpener):
    @contextlib.asynccontextmanager
    async def open_docker_image_repository(self, image: str) -> ta.AsyncGenerator[OciRepository, None]:
        with temp_dir_context() as save_dir:
            with log_timing_context(f'Saving docker image {image}'):
                await asyncio_subprocesses.check_call(
                    ' | '.join([
                        f'docker save {shlex.quote(image)}',
                        f'tar x -C {shlex.quote(save_dir)}',
                    ]),
                    shell=True,
                )

            yield DirectoryOciRepository(save_dir)


########################################
# ../docker/utils.py
"""
TODO:
 - some less stupid Dockerfile hash
  - doesn't change too much though
"""


##


def build_docker_file_hash(docker_file: str) -> str:
    with open(docker_file) as f:
        contents = f.read()

    return sha256_str(contents)


##


def read_docker_tar_image_tag(tar_file: str) -> str:
    with tarfile.open(tar_file) as tf:
        with contextlib.closing(check.not_none(tf.extractfile('manifest.json'))) as mf:
            m = mf.read()

    manifests = json.loads(m.decode('utf-8'))
    manifest = check.single(manifests)
    tag = check.non_empty_str(check.single(manifest['RepoTags']))
    return tag


def read_docker_tar_image_id(tar_file: str) -> str:
    with tarfile.open(tar_file) as tf:
        with contextlib.closing(check.not_none(tf.extractfile('index.json'))) as mf:
            i = mf.read()

    index = json.loads(i.decode('utf-8'))
    manifest = check.single(index['manifests'])
    image_id = check.non_empty_str(manifest['digest'])
    return image_id


########################################
# ../github/api/clients.py


log = get_module_logger(globals())  # noqa


##


class GithubCacheClient(Abstract):
    @dc.dataclass(frozen=True)
    class Entry(Abstract):
        pass

    @abc.abstractmethod
    def get_entry(self, key: str) -> ta.Awaitable[ta.Optional[Entry]]:
        raise NotImplementedError

    def get_entry_url(self, entry: Entry) -> ta.Optional[str]:
        return None

    @abc.abstractmethod
    def download_file(self, entry: Entry, out_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def upload_file(self, key: str, in_file: str) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class BaseGithubCacheClient(GithubCacheClient, Abstract):
    AUTH_TOKEN_ENV_VAR = register_github_env_var('ACTIONS_RUNTIME_TOKEN')  # noqa

    KEY_SUFFIX_ENV_VAR = register_github_env_var('GITHUB_RUN_ID')

    DEFAULT_CONCURRENCY = 4
    DEFAULT_CHUNK_SIZE = 64 * 1024 * 1024

    #

    def __init__(
            self,
            *,
            service_url: str,

            auth_token: ta.Optional[str] = None,

            key_prefix: ta.Optional[str] = None,
            key_suffix: ta.Optional[str] = None,

            cache_version: int = CI_CACHE_VERSION,

            loop: ta.Optional[asyncio.AbstractEventLoop] = None,

            concurrency: int = DEFAULT_CONCURRENCY,
            chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        super().__init__()

        #

        self._service_url = check.non_empty_str(service_url)

        if auth_token is None:
            auth_token = self.AUTH_TOKEN_ENV_VAR()
        self._auth_token = auth_token

        #

        self._key_prefix = key_prefix

        if key_suffix is None:
            key_suffix = self.KEY_SUFFIX_ENV_VAR()
        self._key_suffix = check.non_empty_str(key_suffix)

        #

        self._cache_version = check.isinstance(cache_version, int)

        #

        self._given_loop = loop

        #

        check.arg(concurrency > 0)
        self._concurrency = concurrency

        check.arg(chunk_size > 0)
        self._chunk_size = chunk_size

    ##
    # misc

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        if (loop := self._given_loop) is not None:
            return loop
        return asyncio.get_running_loop()

    #

    def _load_json_bytes(self, b: ta.Optional[bytes]) -> ta.Optional[ta.Any]:
        if not b:
            return None
        return json.loads(b.decode('utf-8-sig'))

    ##
    # requests

    def _build_request_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            *,
            no_auth: bool = False,
            content_type: ta.Optional[str] = None,
            json_content: bool = False,
    ) -> ta.Dict[str, str]:
        dct = {}

        if not no_auth and (auth_token := self._auth_token):
            dct['Authorization'] = f'Bearer {auth_token}'

        if content_type is None and json_content:
            content_type = 'application/json'
        if content_type is not None:
            dct['Content-Type'] = content_type

        if headers:
            dct.update(headers)

        return dct

    #

    async def _send_urllib_request(
            self,
            req: urllib.request.Request,
    ) -> ta.Tuple[http.client.HTTPResponse, ta.Optional[bytes]]:
        def run_sync():
            opener = urllib.request.build_opener(NonRaisingUrllibErrorProcessor)
            with opener.open(req) as resp:  # noqa
                body = resp.read()
            return (resp, body)

        return await self._get_loop().run_in_executor(None, run_sync)  # noqa

    #

    @dc.dataclass()
    class ServiceRequestError(RuntimeError):
        status_code: int
        body: ta.Optional[bytes]

        def __str__(self) -> str:
            return repr(self)

    async def _send_request(
            self,
            *,
            url: ta.Optional[str] = None,
            path: ta.Optional[str] = None,

            method: ta.Optional[str] = None,

            headers: ta.Optional[ta.Mapping[str, str]] = None,
            no_auth: bool = False,
            content_type: ta.Optional[str] = None,

            content: ta.Optional[bytes] = None,
            json_content: ta.Optional[ta.Any] = None,

            success_status_codes: ta.Optional[ta.Container[int]] = None,

            retry_status_codes: ta.Optional[ta.Container[int]] = None,
            num_retries: int = 0,
            retry_sleep: ta.Optional[float] = None,
    ) -> ta.Optional[ta.Any]:
        if url is not None and path is not None:
            raise RuntimeError('Must not pass both url and path')
        elif path is not None:
            url = f'{self._service_url}/{path}'
        url = check.non_empty_str(url)

        if content is not None and json_content is not None:
            raise RuntimeError('Must not pass both content and json_content')
        elif json_content is not None:
            content = json_dumps_compact(json_content).encode('utf-8')
            header_json_content = True
        else:
            header_json_content = False

        if method is None:
            method = 'POST' if content is not None else 'GET'

        headers = self._build_request_headers(
            headers,
            no_auth=no_auth,
            content_type=content_type,
            json_content=header_json_content,
        )

        #

        for n in itertools.count():
            req = urllib.request.Request(  # noqa
                url,
                method=method,
                headers=headers,
                data=content,
            )

            resp, body = await self._send_urllib_request(req)

            #

            if success_status_codes is not None:
                is_success = resp.status in success_status_codes
            else:
                is_success = (200 <= resp.status < 300)
            if is_success:
                return self._load_json_bytes(body)

            #

            log.debug(f'Request to url {url} got unsuccessful status code {resp.status}')  # noqa

            if not (
                retry_status_codes is not None and
                resp.status in retry_status_codes and
                n < num_retries
            ):
                raise self.ServiceRequestError(resp.status, body)

            if retry_sleep is not None:
                await asyncio.sleep(retry_sleep)

        raise RuntimeError('Unreachable')

    ##
    # keys

    KEY_PART_SEPARATOR = '---'

    def fix_key(self, s: str, partial_suffix: bool = False) -> str:
        return self.KEY_PART_SEPARATOR.join([
            *([self._key_prefix] if self._key_prefix else []),
            s,
            ('' if partial_suffix else self._key_suffix),
        ])

    ##
    # downloading

    @dc.dataclass(frozen=True)
    class _DownloadChunk:
        key: str
        url: str
        out_file: str
        offset: int
        size: int

    async def _download_file_chunk_urllib(self, chunk: _DownloadChunk) -> None:
        req = urllib.request.Request(  # noqa
            chunk.url,
            headers={
                'Range': f'bytes={chunk.offset}-{chunk.offset + chunk.size - 1}',
            },
        )

        _, buf_ = await self._send_urllib_request(req)

        buf = check.not_none(buf_)
        check.equal(len(buf), chunk.size)

        #

        def write_sync():
            with open(chunk.out_file, 'r+b') as f:  # noqa
                f.seek(chunk.offset, os.SEEK_SET)
                f.write(buf)

        await self._get_loop().run_in_executor(None, write_sync)  # noqa

    # async def _download_file_chunk_curl(self, chunk: _DownloadChunk) -> None:
    #     async with contextlib.AsyncExitStack() as es:
    #         f = open(chunk.out_file, 'r+b')
    #         f.seek(chunk.offset, os.SEEK_SET)
    #
    #         tmp_file = es.enter_context(temp_file_context())  # noqa
    #
    #         proc = await es.enter_async_context(asyncio_subprocesses.popen(
    #             'curl',
    #             '-s',
    #             '-w', '%{json}',
    #             '-H', f'Range: bytes={chunk.offset}-{chunk.offset + chunk.size - 1}',
    #             chunk.url,
    #             output=subprocess.PIPE,
    #         ))
    #
    #         futs = asyncio.gather(
    #
    #         )
    #
    #         await proc.wait()
    #
    #         with open(tmp_file, 'r') as f:  # noqa
    #             curl_json = tmp_file.read()
    #
    #     curl_res = json.loads(curl_json.decode().strip())
    #
    #     status_code = check.isinstance(curl_res['response_code'], int)
    #
    #     if not (200 <= status_code < 300):
    #         raise RuntimeError(f'Curl chunk download {chunk} failed: {curl_res}')

    async def _download_file_chunk(self, chunk: _DownloadChunk) -> None:
        with log_timing_context(
                'Downloading github cache '
                f'key {chunk.key} '
                f'file {chunk.out_file} '
                f'chunk {chunk.offset} - {chunk.offset + chunk.size}',
        ):
            await self._download_file_chunk_urllib(chunk)

    async def _download_file_chunks(
            self,
            *,
            key: str,
            url: str,
            out_file: str,
    ) -> None:
        check.non_empty_str(key)
        check.non_empty_str(url)

        head_resp, _ = await self._send_urllib_request(urllib.request.Request(  # noqa
            url,
            method='HEAD',
        ))
        file_size = int(head_resp.headers['Content-Length'])

        #

        with open(out_file, 'xb') as f:  # noqa
            f.truncate(file_size)

        #

        download_tasks = []
        chunk_size = self._chunk_size
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            offset = i * chunk_size
            size = min(chunk_size, file_size - offset)
            chunk = self._DownloadChunk(
                key,
                url,
                out_file,
                offset,
                size,
            )
            download_tasks.append(self._download_file_chunk(chunk))

        await asyncio_wait_concurrent(download_tasks, self._concurrency)

    ##
    # uploading

    @dc.dataclass(frozen=True)
    class _UploadChunk:
        url: str
        key: str
        in_file: str
        offset: int
        size: int

    UPLOAD_CHUNK_NUM_RETRIES = 10
    UPLOAD_CHUNK_RETRY_SLEEP = .5

    async def _upload_file_chunk_(self, chunk: _UploadChunk) -> None:
        with open(chunk.in_file, 'rb') as f:  # noqa
            f.seek(chunk.offset)
            buf = f.read(chunk.size)

        check.equal(len(buf), chunk.size)

        await self._send_request(
            url=chunk.url,

            method='PATCH',

            headers={
                'Content-Range': f'bytes {chunk.offset}-{chunk.offset + chunk.size - 1}/*',
            },
            no_auth=True,
            content_type='application/octet-stream',

            content=buf,

            success_status_codes=[204],

            # retry_status_codes=[405],
            num_retries=self.UPLOAD_CHUNK_NUM_RETRIES,
            retry_sleep=self.UPLOAD_CHUNK_RETRY_SLEEP,
        )

    async def _upload_file_chunk(self, chunk: _UploadChunk) -> None:
        with log_timing_context(
                f'Uploading github cache {chunk.key} '
                f'file {chunk.in_file} '
                f'chunk {chunk.offset} - {chunk.offset + chunk.size}',
        ):
            await self._upload_file_chunk_(chunk)

    def _generate_file_upload_chunks(
            self,
            *,
            in_file: str,
            url: str,
            key: str,

            file_size: ta.Optional[int] = None,
    ) -> ta.List[_UploadChunk]:
        check.state(os.path.isfile(in_file))

        if file_size is None:
            file_size = os.stat(in_file).st_size

        #

        upload_chunks: ta.List[BaseGithubCacheClient._UploadChunk] = []
        chunk_size = self._chunk_size
        for i in range((file_size // chunk_size) + (1 if file_size % chunk_size else 0)):
            offset = i * chunk_size
            size = min(chunk_size, file_size - offset)
            upload_chunks.append(self._UploadChunk(
                url=url,
                key=key,
                in_file=in_file,
                offset=offset,
                size=size,
            ))

        return upload_chunks

    async def _upload_file_chunks(
            self,
            *,
            in_file: str,
            url: str,
            key: str,

            file_size: ta.Optional[int] = None,
    ) -> None:
        upload_tasks = []
        for chunk in self._generate_file_upload_chunks(
            in_file=in_file,
            url=url,
            key=key,
            file_size=file_size,
        ):
            upload_tasks.append(self._upload_file_chunk(chunk))

        await asyncio_wait_concurrent(upload_tasks, self._concurrency)


########################################
# ../github/api/v2/azure.py
"""
TODO:
 - ominfra? no, circdep
"""


log = get_module_logger(globals())  # noqa


##


class AzureBlockBlobUploader:
    """
    https://learn.microsoft.com/en-us/rest/api/storageservices/put-block
    https://learn.microsoft.com/en-us/rest/api/storageservices/put-block-list
    """

    DEFAULT_CONCURRENCY = 4

    @dc.dataclass(frozen=True)
    class Request:
        method: str
        url: str
        headers: ta.Optional[ta.Dict[str, str]] = None
        body: ta.Optional[bytes] = None

    @dc.dataclass(frozen=True)
    class Response:
        status: int
        headers: ta.Optional[ta.Mapping[str, str]] = None
        data: ta.Optional[bytes] = None

        def get_header(self, name: str) -> ta.Optional[str]:
            for k, v in (self.headers or {}).items():
                if k.lower() == name.lower():
                    return v
            return None

    def __init__(
            self,
            blob_url_with_sas: str,
            make_request: ta.Callable[[Request], ta.Awaitable[Response]],
            *,
            api_version: str = '2020-10-02',
            concurrency: int = DEFAULT_CONCURRENCY,
    ) -> None:
        """
        blob_url_with_sas should be of the form:
           https://<account>.blob.core.windows.net/<container>/<blob>?<SAS-token>
        """

        super().__init__()

        self._make_request = make_request
        self._api_version = api_version
        check.arg(concurrency >= 1)
        self._concurrency = concurrency

        parsed = urllib.parse.urlparse(blob_url_with_sas)
        self._base_url = f'{parsed.scheme}://{parsed.netloc}'
        parts = parsed.path.lstrip('/').split('/', 1)
        self._container = parts[0]
        self._blob_name = parts[1]
        self._sas = parsed.query

    def _headers(self) -> ta.Dict[str, str]:
        """Standard headers for Azure Blob REST calls."""

        now = datetime.datetime.now(datetime.UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')
        return {
            'x-ms-date': now,
            'x-ms-version': self._api_version,
        }

    @dc.dataclass(frozen=True)
    class FileChunk:
        in_file: str
        offset: int
        size: int

    async def _upload_file_chunk_(
            self,
            block_id: str,
            chunk: FileChunk,
    ) -> None:
        with open(chunk.in_file, 'rb') as f:  # noqa
            f.seek(chunk.offset)
            data = f.read(chunk.size)

        check.equal(len(data), chunk.size)

        params = {
            'comp': 'block',
            'blockid': block_id,
        }
        query = self._sas + '&' + urllib.parse.urlencode(params)
        url = f'{self._base_url}/{self._container}/{self._blob_name}?{query}'

        log.debug(f'Uploading azure blob chunk {chunk} with block id {block_id}')  # noqa

        resp = await self._make_request(self.Request(
            'PUT',
            url,
            headers=self._headers(),
            body=data,
        ))
        if resp.status not in (201, 202):
            raise RuntimeError(f'Put Block failed: {block_id=} {resp.status=}')

    async def _upload_file_chunk(
            self,
            block_id: str,
            chunk: FileChunk,
    ) -> None:
        with log_timing_context(f'Uploading azure blob chunk {chunk} with block id {block_id}'):
            await self._upload_file_chunk_(
                block_id,
                chunk,
            )

    async def upload_file(
            self,
            chunks: ta.List[FileChunk],
    ) -> ta.Dict[str, ta.Any]:
        block_ids = []

        # 1) Stage each block
        upload_tasks = []
        for idx, chunk in enumerate(chunks):
            # Generate a predictable block ID (must be URL-safe base64)
            raw_id = f'{idx:08d}'.encode()
            block_id = base64.b64encode(raw_id).decode('utf-8')
            block_ids.append(block_id)

            upload_tasks.append(self._upload_file_chunk(
                block_id,
                chunk,
            ))

        await asyncio_wait_concurrent(upload_tasks, self._concurrency)

        # 2) Commit block list
        root = ET.Element('BlockList')
        for bid in block_ids:
            elm = ET.SubElement(root, 'Latest')
            elm.text = bid
        body = ET.tostring(root, encoding='utf-8', method='xml')

        params = {'comp': 'blocklist'}
        query = self._sas + '&' + urllib.parse.urlencode(params)
        url = f'{self._base_url}/{self._container}/{self._blob_name}?{query}'

        log.debug(f'Putting azure blob chunk list block ids {block_ids}')  # noqa

        resp = await self._make_request(self.Request(
            'PUT',
            url,
            headers={
                **self._headers(),
                'Content-Type': 'application/xml',
            },
            body=body,
        ))
        if resp.status not in (200, 201):
            raise RuntimeError(f'Put Block List failed: {resp.status} {resp.data!r}')

        ret = {
            'status_code': resp.status,
            'etag': resp.get_header('ETag'),
        }

        log.debug(f'Uploaded azure blob chunk {ret}')  # noqa

        return ret


########################################
# ../requirements.py
"""
TODO:
 - pip compile lol
  - but still support git+ stuff
 - req.txt format aware hash
  - more than just whitespace
 - pyproject req rewriting
 - download_requirements bootstrap off prev? not worth the dl?
  - big deps (torch) change less, probably worth it
 - follow embedded -r automatically like pyp
"""


##


def build_requirements_hash(
        requirements_txts: ta.Sequence[str],
) -> str:
    txt_file_contents: dict = {}

    for txt_file in requirements_txts:
        txt_file_name = os.path.basename(txt_file)
        check.not_in(txt_file_name, txt_file_contents)
        with open(txt_file) as f:
            txt_contents = f.read()
        txt_file_contents[txt_file_name] = txt_contents

    #

    lines = []
    for txt_file, txt_contents in sorted(txt_file_contents.items()):
        txt_hash = sha256_str(txt_contents)
        lines.append(f'{txt_file}={txt_hash}')

    return sha256_str('\n'.join(lines))


##


def download_requirements(
        image: str,
        requirements_dir: str,
        requirements_txts: ta.Sequence[str],
) -> None:
    requirements_txt_dir = tempfile.mkdtemp()
    with defer(lambda: shutil.rmtree(requirements_txt_dir)):
        for rt in requirements_txts:
            shutil.copyfile(rt, os.path.join(requirements_txt_dir, os.path.basename(rt)))

        subprocesses.check_call(
            'docker',
            'run',
            '--rm',
            '-i',
            '-v', f'{os.path.abspath(requirements_dir)}:/requirements',
            '-v', f'{requirements_txt_dir}:/requirements_txt',
            image,
            'pip',
            'download',
            '-d', '/requirements',
            *itertools.chain.from_iterable(
                ['-r', f'/requirements_txt/{os.path.basename(rt)}']
                for rt in requirements_txts
            ),
        )


########################################
# ../../oci/pack/repositories.py


##


class OciPackedRepositoryBuilder(ExitStacked):
    def __init__(
            self,
            source_repo: OciRepository,
            *,
            temp_dir: ta.Optional[str] = None,

            num_packed_files: int = 3,  # GH actions have this set to 3, the default
            packed_compression: ta.Optional[OciCompression] = OciCompression.ZSTD,
    ) -> None:
        super().__init__()

        self._source_repo = source_repo

        self._given_temp_dir = temp_dir

        check.arg(num_packed_files > 0)
        self._num_packed_files = num_packed_files

        self._packed_compression = packed_compression

    @cached_nullary
    def _temp_dir(self) -> str:
        if (given := self._given_temp_dir) is not None:
            return given
        else:
            return self._enter_context(temp_dir_context())  # noqa

    #

    @cached_nullary
    def _source_image_index(self) -> OciImageIndex:
        image_index = read_oci_repository_root_index(self._source_repo)
        return get_single_leaf_oci_image_index(image_index)

    @cached_nullary
    def _source_image_manifest(self) -> OciImageManifest:
        return get_single_oci_image_manifest(self._source_image_index())

    #

    @cached_nullary
    def _extracted_layer_tar_files(self) -> ta.List[str]:
        image = self._source_image_manifest()

        layer_tar_files = []

        for i, layer in enumerate(image.layers):
            if isinstance(layer.data, FileOciDataRef):
                input_file_path = layer.data.path

            else:
                input_file_path = os.path.join(self._temp_dir(), f'save-layer-{i}.tar')
                with open(input_file_path, 'wb') as input_file:  # noqa
                    with open_oci_data_ref(layer.data) as layer_file:
                        shutil.copyfileobj(layer_file, input_file, length=1024 * 1024)  # noqa

            layer_tar_files.append(input_file_path)

        return layer_tar_files

    #

    @cached_nullary
    def _unpacked_tar_file(self) -> str:
        layer_tar_files = self._extracted_layer_tar_files()
        unpacked_file = os.path.join(self._temp_dir(), 'unpacked.tar')

        with log_timing_context(f'Unpacking docker image {self._source_repo}'):
            with OciLayerUnpacker(
                    layer_tar_files,
                    unpacked_file,
            ) as lu:
                lu.write()

        return unpacked_file

    #

    @cached_nullary
    def _packed_tar_files(self) -> ta.Mapping[str, WrittenOciDataTarFileInfo]:
        unpacked_tar_file = self._unpacked_tar_file()

        packed_tar_files = [
            os.path.join(self._temp_dir(), f'packed-{i}.tar')
            for i in range(self._num_packed_files)
        ]

        with log_timing_context(f'Packing docker image {self._source_repo}'):
            with OciLayerPacker(
                    unpacked_tar_file,
                    packed_tar_files,
                    compression=self._packed_compression,
            ) as lp:
                return lp.write()

    #

    @cached_nullary
    def _packed_image_index(self) -> OciImageIndex:
        image_index = copy.deepcopy(self._source_image_index())

        image = get_single_oci_image_manifest(image_index)

        image.config.history = None

        written = self._packed_tar_files()

        # FIXME: use prebuilt sha256
        image.layers = [
            OciImageLayer(
                kind=OciImageLayer.Kind.from_compression(self._packed_compression),
                data=FileOciDataRef(output_file),
            )
            for output_file, output_file_info in written.items()
        ]

        image.config.rootfs.diff_ids = [
            f'sha256:{output_file_info.tar_sha256}'
            for output_file_info in written.values()
        ]

        return image_index

    #

    @cached_nullary
    def build(self) -> BuiltOciImageIndexRepository:
        return build_oci_index_repository(self._packed_image_index())


########################################
# ../docker/buildcaching.py


##


class DockerBuildCaching(Abstract):
    @abc.abstractmethod
    def cached_build_docker_image(
            self,
            cache_key: DockerCacheKey,
            build_and_tag: ta.Callable[[str], ta.Awaitable[str]],  # image_tag -> image_id
    ) -> ta.Awaitable[str]:
        raise NotImplementedError


class DockerBuildCachingImpl(DockerBuildCaching):
    @dc.dataclass(frozen=True)
    class Config:
        service: str

        always_build: bool = False

    def __init__(
            self,
            *,
            config: Config,

            docker_cache: ta.Optional[DockerCache] = None,
    ) -> None:
        super().__init__()

        self._config = config

        self._docker_cache = docker_cache

    async def cached_build_docker_image(
            self,
            cache_key: DockerCacheKey,
            build_and_tag: ta.Callable[[str], ta.Awaitable[str]],
    ) -> str:
        image_tag = f'{self._config.service}:{cache_key!s}'

        if not self._config.always_build and (await is_docker_image_present(image_tag)):
            return image_tag

        if (
                self._docker_cache is not None and
                (cache_image_id := await self._docker_cache.load_cache_docker_image(cache_key)) is not None
        ):
            await tag_docker_image(
                cache_image_id,
                image_tag,
            )
            return image_tag

        image_id = await build_and_tag(image_tag)

        if self._docker_cache is not None:
            await self._docker_cache.save_cache_docker_image(cache_key, image_id)

        return image_tag


########################################
# ../docker/cacheserved/cache.py


log = get_module_logger(globals())  # noqa


##


class CacheServedDockerCache(DockerCache):
    @dc.dataclass(frozen=True)
    class Config:
        port: int = 5021

        repack: bool = True

        key_prefix: ta.Optional[str] = 'cs'

        #

        pull_run_cmd: ta.Optional[str] = 'true'

        #

        server_start_timeout: TimeoutLike = 5.
        server_start_sleep: float = .1

    def __init__(
            self,
            *,
            config: Config = Config(),

            image_repo_opener: DockerImageRepositoryOpener,
            data_cache: DataCache,
    ) -> None:
        super().__init__()

        self._config = config

        self._image_repo_opener = image_repo_opener
        self._data_cache = data_cache

    async def load_cache_docker_image(self, key: DockerCacheKey) -> ta.Optional[str]:
        if (kp := self._config.key_prefix) is not None:
            key = key.append_prefix(kp)

        if (manifest_data := await self._data_cache.get_data(str(key))) is None:
            return None

        manifest_bytes = await read_data_cache_data(manifest_data)

        manifest: CacheServedDockerImageManifest = unmarshal_obj(
            json.loads(manifest_bytes.decode('utf-8')),
            CacheServedDockerImageManifest,
        )

        async def make_cache_key_target(target_cache_key: str, **target_kwargs: ta.Any) -> DataServerTarget:  # noqa
            cache_data = check.not_none(await self._data_cache.get_data(target_cache_key))

            if isinstance(cache_data, DataCache.BytesData):
                return DataServerTarget.of(
                    cache_data.data,
                    **target_kwargs,
                )

            elif isinstance(cache_data, DataCache.FileData):
                return DataServerTarget.of(
                    file_path=cache_data.file_path,
                    **target_kwargs,
                )

            elif isinstance(cache_data, DataCache.UrlData):
                return DataServerTarget.of(
                    url=cache_data.url,
                    methods=['GET'],
                    **target_kwargs,
                )

            else:
                raise TypeError(cache_data)

        data_server_routes = await build_cache_served_docker_image_data_server_routes(
            manifest,
            make_cache_key_target,
        )

        data_server = DataServer(DataServer.HandlerRoute.of_(*data_server_routes))

        image_url = f'localhost:{self._config.port}/{key!s}'

        async with DockerDataServer(
                self._config.port,
                data_server,
                handler_log=log,
        ) as dds:
            dds_run_task = asyncio.create_task(dds.run())
            try:
                timeout = Timeout.of(self._config.server_start_timeout)

                await asyncio_wait_until_can_connect(
                    'localhost',
                    self._config.port,
                    timeout=timeout,
                    on_fail=lambda _: log.exception('Failed to connect to cache server - will try again'),
                    sleep_s=self._config.server_start_sleep,
                )

                if (prc := self._config.pull_run_cmd) is not None:
                    pull_cmd = [
                        'run',
                        '--rm',
                        image_url,
                        prc,
                    ]
                else:
                    pull_cmd = [
                        'pull',
                        image_url,
                    ]

                await asyncio_subprocesses.check_call(
                    'docker',
                    *pull_cmd,
                )

            finally:
                dds.stop_event.set()
                await dds_run_task

        return image_url

    async def save_cache_docker_image(self, key: DockerCacheKey, image: str) -> None:
        if (kp := self._config.key_prefix) is not None:
            key = key.append_prefix(kp)

        async with contextlib.AsyncExitStack() as es:
            image_repo: OciRepository = await es.enter_async_context(
                self._image_repo_opener.open_docker_image_repository(image),
            )

            root_image_index = read_oci_repository_root_index(image_repo)
            image_index = get_single_leaf_oci_image_index(root_image_index)

            if self._config.repack:
                prb: OciPackedRepositoryBuilder = es.enter_context(OciPackedRepositoryBuilder(
                    image_repo,
                ))
                built_repo = await asyncio.get_running_loop().run_in_executor(None, prb.build)  # noqa

            else:
                built_repo = build_oci_index_repository(image_index)

            data_server_routes = build_oci_repository_data_server_routes(
                str(key),
                built_repo,
            )

            async def make_file_cache_key(file_path: str) -> str:
                target_cache_key = f'{key!s}--{os.path.basename(file_path).split(".")[0]}'
                await self._data_cache.put_data(
                    target_cache_key,
                    DataCache.FileData(file_path),
                )
                return target_cache_key

            cache_served_manifest = await build_cache_served_docker_image_manifest(
                data_server_routes,
                make_file_cache_key,
            )

        manifest_data = json_dumps_compact(marshal_obj(cache_served_manifest)).encode('utf-8')

        await self._data_cache.put_data(
            str(key),
            DataCache.BytesData(manifest_data),
        )


########################################
# ../docker/imagepulling.py


##


class DockerImagePulling(Abstract):
    @abc.abstractmethod
    def pull_docker_image(self, image: str) -> ta.Awaitable[None]:
        raise NotImplementedError


class DockerImagePullingImpl(DockerImagePulling):
    @dc.dataclass(frozen=True)
    class Config:
        always_pull: bool = False

    def __init__(
            self,
            *,
            config: Config = Config(),

            file_cache: ta.Optional[FileCache] = None,
            docker_cache: ta.Optional[DockerCache] = None,
    ) -> None:
        super().__init__()

        self._config = config

        self._file_cache = file_cache
        self._docker_cache = docker_cache

    async def _pull_docker_image(self, image: str) -> None:
        if not self._config.always_pull and (await is_docker_image_present(image)):
            return

        key_content = StringMangler.of('-', '/:._').mangle(image)

        cache_key = DockerCacheKey(['docker'], key_content)
        if (
                self._docker_cache is not None and
                (await self._docker_cache.load_cache_docker_image(cache_key)) is not None
        ):
            return

        await pull_docker_image(image)

        if self._docker_cache is not None:
            await self._docker_cache.save_cache_docker_image(cache_key, image)

    async def pull_docker_image(self, image: str) -> None:
        with log_timing_context(f'Load docker image: {image}'):
            await self._pull_docker_image(image)


########################################
# ../github/api/v1/client.py


log = get_module_logger(globals())  # noqa


##


class GithubCacheServiceV1Client(BaseGithubCacheClient):
    BASE_URL_ENV_VAR = register_github_env_var('ACTIONS_CACHE_URL')

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,

            **kwargs: ta.Any,
    ) -> None:
        if base_url is None:
            base_url = check.non_empty_str(self.BASE_URL_ENV_VAR())
        service_url = GithubCacheServiceV1.get_service_url(base_url)

        super().__init__(
            service_url=service_url,
            **kwargs,
        )

    #

    def _build_request_headers(
            self,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> ta.Dict[str, str]:
        return super()._build_request_headers(
            {
                'Accept': ';'.join([
                    'application/json',
                    f'api-version={GithubCacheServiceV1.API_VERSION}',
                ]),
                **(headers or {}),
            },
            **kwargs,
        )

    #

    @dc.dataclass(frozen=True)
    class Entry(GithubCacheClient.Entry):
        artifact: GithubCacheServiceV1.ArtifactCacheEntry

    def get_entry_url(self, entry: GithubCacheClient.Entry) -> ta.Optional[str]:
        entry1 = check.isinstance(entry, self.Entry)
        return entry1.artifact.archive_location

    #

    def _build_get_entry_url_path(self, *keys: str) -> str:
        qp = dict(
            keys=','.join(urllib.parse.quote_plus(k) for k in keys),
            version=str(self._cache_version),
        )

        return '?'.join([
            'cache',
            '&'.join([
                f'{k}={v}'
                for k, v in qp.items()
            ]),
        ])

    GET_ENTRY_SUCCESS_STATUS_CODES = (200, 204)

    #

    async def get_entry(self, key: str) -> ta.Optional[GithubCacheClient.Entry]:
        obj = await self._send_request(
            path=self._build_get_entry_url_path(self.fix_key(key, partial_suffix=True)),
        )
        if obj is None:
            return None

        return self.Entry(GithubCacheServiceV1.dataclass_from_json(
            GithubCacheServiceV1.ArtifactCacheEntry,
            obj,
        ))

    #

    async def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        entry1 = check.isinstance(entry, self.Entry)
        with log_timing_context(
                'Downloading github cache '
                f'key {entry1.artifact.cache_key} '
                f'version {entry1.artifact.cache_version} '
                f'to {out_file}',
        ):
            await self._download_file_chunks(
                key=check.non_empty_str(entry1.artifact.cache_key),
                url=check.non_empty_str(entry1.artifact.archive_location),
                out_file=out_file,
            )

    #

    async def _upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))
        file_size = os.stat(in_file).st_size

        #

        reserve_req = GithubCacheServiceV1.ReserveCacheRequest(
            key=fixed_key,
            cache_size=file_size,
            version=str(self._cache_version),
        )
        reserve_resp_obj = await self._send_request(
            path='caches',
            json_content=GithubCacheServiceV1.dataclass_to_json(reserve_req),
            success_status_codes=[201],
        )
        reserve_resp = GithubCacheServiceV1.dataclass_from_json(  # noqa
            GithubCacheServiceV1.ReserveCacheResponse,
            reserve_resp_obj,
        )
        cache_id = check.isinstance(reserve_resp.cache_id, int)

        log.debug(f'Github cache file {os.path.basename(in_file)} got id {cache_id}')  # noqa

        #

        url = f'{self._service_url}/caches/{cache_id}'

        await self._upload_file_chunks(
            in_file=in_file,
            url=url,
            key=fixed_key,
            file_size=file_size,
        )

        #

        commit_req = GithubCacheServiceV1.CommitCacheRequest(
            size=file_size,
        )
        await self._send_request(
            path=f'caches/{cache_id}',
            json_content=GithubCacheServiceV1.dataclass_to_json(commit_req),
            success_status_codes=[204],
        )

    async def upload_file(self, key: str, in_file: str) -> None:
        with log_timing_context(
                f'Uploading github cache file {os.path.basename(in_file)} '
                f'key {key}',
        ):
            await self._upload_file(key, in_file)


########################################
# ../github/api/v2/client.py


log = get_module_logger(globals())  # noqa


##


class GithubCacheServiceV2Client(BaseGithubCacheClient):
    BASE_URL_ENV_VAR = register_github_env_var('ACTIONS_RESULTS_URL')

    def __init__(
            self,
            *,
            base_url: ta.Optional[str] = None,

            **kwargs: ta.Any,
    ) -> None:
        if base_url is None:
            base_url = check.non_empty_str(self.BASE_URL_ENV_VAR())
        service_url = GithubCacheServiceV2.get_service_url(base_url)

        super().__init__(
            service_url=service_url,
            **kwargs,
        )

    #

    async def _send_method_request(
            self,
            method: GithubCacheServiceV2.Method[
                GithubCacheServiceV2RequestT,
                GithubCacheServiceV2ResponseT,
            ],
            request: GithubCacheServiceV2RequestT,
            **kwargs: ta.Any,
    ) -> ta.Optional[GithubCacheServiceV2ResponseT]:
        obj = await self._send_request(
            path=method.name,
            json_content=dc.asdict(request),  # type: ignore[call-overload]
            **kwargs,
        )

        if obj is None:
            return None
        return method.response(**obj)

    #

    @dc.dataclass(frozen=True)
    class Entry(GithubCacheClient.Entry):
        request: GithubCacheServiceV2.GetCacheEntryDownloadUrlRequest
        response: GithubCacheServiceV2.GetCacheEntryDownloadUrlResponse

        def __post_init__(self) -> None:
            check.state(self.response.ok)
            check.non_empty_str(self.response.signed_download_url)

    def get_entry_url(self, entry: GithubCacheClient.Entry) -> ta.Optional[str]:
        entry2 = check.isinstance(entry, self.Entry)
        return check.non_empty_str(entry2.response.signed_download_url)

    #

    async def get_entry(self, key: str) -> ta.Optional[GithubCacheClient.Entry]:
        version = str(self._cache_version).zfill(GithubCacheServiceV2.VERSION_LENGTH)

        req = GithubCacheServiceV2.GetCacheEntryDownloadUrlRequest(
            key=self.fix_key(key),
            restore_keys=[self.fix_key(key, partial_suffix=True)],
            version=version,
        )

        resp = await self._send_method_request(
            GithubCacheServiceV2.GET_CACHE_ENTRY_DOWNLOAD_URL_METHOD,
            req,
        )
        if resp is None or not resp.ok:
            return None

        return self.Entry(
            request=req,
            response=resp,
        )

    #

    async def download_file(self, entry: GithubCacheClient.Entry, out_file: str) -> None:
        entry2 = check.isinstance(entry, self.Entry)
        with log_timing_context(
                'Downloading github cache '
                f'key {entry2.response.matched_key} '
                f'version {entry2.request.version} '
                f'to {out_file}',
        ):
            await self._download_file_chunks(
                key=check.non_empty_str(entry2.response.matched_key),
                url=check.non_empty_str(entry2.response.signed_download_url),
                out_file=out_file,
            )

    #

    async def _upload_file(self, key: str, in_file: str) -> None:
        fixed_key = self.fix_key(key)

        check.state(os.path.isfile(in_file))
        file_size = os.stat(in_file).st_size

        #

        version = str(self._cache_version).zfill(GithubCacheServiceV2.VERSION_LENGTH)

        reserve_resp = check.not_none(await self._send_method_request(
            GithubCacheServiceV2.CREATE_CACHE_ENTRY_METHOD,  # type: ignore[arg-type]
            GithubCacheServiceV2.CreateCacheEntryRequest(
                key=fixed_key,
                version=version,
            ),
        ))
        check.state(reserve_resp.ok)

        log.debug(f'Github cache file {os.path.basename(in_file)} upload reserved for file size {file_size}')  # noqa

        #

        upload_chunks = self._generate_file_upload_chunks(
            in_file=in_file,
            url=reserve_resp.signed_upload_url,
            key=fixed_key,
            file_size=file_size,
        )

        az_chunks = [
            AzureBlockBlobUploader.FileChunk(
                in_file=in_file,
                offset=c.offset,
                size=c.size,
            )
            for c in upload_chunks
        ]

        async def az_make_request(req: AzureBlockBlobUploader.Request) -> AzureBlockBlobUploader.Response:
            u_req = urllib.request.Request(  # noqa
                req.url,
                method=req.method,
                headers=req.headers or {},
                data=req.body,
            )

            u_resp, u_body = await self._send_urllib_request(u_req)

            return AzureBlockBlobUploader.Response(
                status=u_resp.status,
                headers=dict(u_resp.headers),
                data=u_body,
            )

        az_uploader = AzureBlockBlobUploader(
            reserve_resp.signed_upload_url,
            az_make_request,
            concurrency=self._concurrency,
        )

        await az_uploader.upload_file(az_chunks)

        #

        commit_resp = check.not_none(await self._send_method_request(
            GithubCacheServiceV2.FINALIZE_CACHE_ENTRY_METHOD,  # type: ignore[arg-type]
            GithubCacheServiceV2.FinalizeCacheEntryUploadRequest(
                key=fixed_key,
                size_bytes=file_size,
                version=version,
            ),
        ))
        check.state(commit_resp.ok)

        log.debug(f'Github cache file {os.path.basename(in_file)} upload complete, entry id {commit_resp.entry_id}')  # noqa

    async def upload_file(self, key: str, in_file: str) -> None:
        with log_timing_context(
                f'Uploading github cache file {os.path.basename(in_file)} '
                f'key {key}',
        ):
            await self._upload_file(key, in_file)


########################################
# ../ci.py


##


class Ci(AsyncExitStacked):
    KEY_HASH_LEN = 16

    @dc.dataclass(frozen=True)
    class Config:
        project_dir: str

        docker_file: str

        compose_file: str
        service: str

        cmd: ShellCmd

        #

        requirements_txts: ta.Optional[ta.Sequence[str]] = None

        always_pull: bool = False
        always_build: bool = False

        setup_concurrency: ta.Optional[int] = None

        no_dependencies: bool = False

        setup_only: bool = False

        run_options: ta.Optional[ta.Sequence[str]] = None

        #

        def __post_init__(self) -> None:
            check.not_isinstance(self.requirements_txts, str)

    def __init__(
            self,
            config: Config,
            *,
            docker_build_caching: DockerBuildCaching,
            docker_image_pulling: DockerImagePulling,
    ) -> None:
        super().__init__()

        self._config = config

        self._docker_build_caching = docker_build_caching
        self._docker_image_pulling = docker_image_pulling

    #

    @cached_nullary
    def docker_file_hash(self) -> str:
        return build_docker_file_hash(self._config.docker_file)[:self.KEY_HASH_LEN]

    @cached_nullary
    def ci_base_image_cache_key(self) -> DockerCacheKey:
        return DockerCacheKey(['ci-base'], self.docker_file_hash())

    async def _resolve_ci_base_image(self) -> str:
        async def build_and_tag(image_tag: str) -> str:
            return await build_docker_image(
                self._config.docker_file,
                tag=image_tag,
                cwd=self._config.project_dir,
            )

        return await self._docker_build_caching.cached_build_docker_image(
            self.ci_base_image_cache_key(),
            build_and_tag,
        )

    @async_cached_nullary
    async def resolve_ci_base_image(self) -> str:
        with log_timing_context('Resolve ci base image') as ltc:
            image_id = await self._resolve_ci_base_image()
            ltc.set_description(f'Resolve ci base image: {image_id}')
            return image_id

    #

    @cached_nullary
    def requirements_txts(self) -> ta.Sequence[str]:
        return [
            os.path.join(self._config.project_dir, rf)
            for rf in check.not_none(self._config.requirements_txts)
        ]

    @cached_nullary
    def requirements_hash(self) -> str:
        return build_requirements_hash(self.requirements_txts())[:self.KEY_HASH_LEN]

    @cached_nullary
    def ci_image_cache_key(self) -> DockerCacheKey:
        return DockerCacheKey(['ci'], f'{self.docker_file_hash()}-{self.requirements_hash()}')

    async def _resolve_ci_image(self) -> str:
        async def build_and_tag(image_tag: str) -> str:
            base_image = await self.resolve_ci_base_image()

            setup_cmds = [
                ' '.join([
                    'pip install',
                    '--no-cache-dir',
                    '--root-user-action ignore',
                    'uv',
                ]),
                ' '.join([
                    'uv pip install',
                    '--no-cache',
                    '--index-strategy unsafe-best-match',
                    '--system',
                    *[f'-r /project/{rf}' for rf in self._config.requirements_txts or []],
                ]),
            ]
            setup_cmd = ' && '.join(setup_cmds)

            docker_file_lines = [
                f'FROM {base_image}',
                'RUN mkdir /project',
                *[f'COPY {rf} /project/{rf}' for rf in self._config.requirements_txts or []],
                f'RUN {setup_cmd}',
                'RUN rm /project/*',
                'WORKDIR /project',
            ]

            with temp_file_context() as docker_file:
                with open(docker_file, 'w') as f:  # noqa
                    f.write('\n'.join(docker_file_lines))

                return await build_docker_image(
                    docker_file,
                    tag=image_tag,
                    cwd=self._config.project_dir,
                )

        return await self._docker_build_caching.cached_build_docker_image(
            self.ci_image_cache_key(),
            build_and_tag,
        )

    @async_cached_nullary
    async def resolve_ci_image(self) -> str:
        with log_timing_context('Resolve ci image') as ltc:
            image_id = await self._resolve_ci_image()
            ltc.set_description(f'Resolve ci image: {image_id}')
            return image_id

    #

    @cached_nullary
    def get_dependency_images(self) -> ta.Sequence[str]:
        deps = get_compose_service_dependencies(
            self._config.compose_file,
            self._config.service,
        )
        return sorted(deps.values())

    @cached_nullary
    def pull_dependencies_funcs(self) -> ta.Sequence[ta.Callable[[], ta.Awaitable]]:
        return [
            async_cached_nullary(functools.partial(
                self._docker_image_pulling.pull_docker_image,
                dep_image,
            ))
            for dep_image in self.get_dependency_images()
        ]

    #

    @cached_nullary
    def setup_funcs(self) -> ta.Sequence[ta.Callable[[], ta.Awaitable]]:
        return [
            self.resolve_ci_image,

            *(self.pull_dependencies_funcs() if not self._config.no_dependencies else []),
        ]

    @async_cached_nullary
    async def setup(self) -> None:
        await asyncio_wait_maybe_concurrent(
            [fn() for fn in self.setup_funcs()],
            self._config.setup_concurrency,
        )

    #

    async def _run_compose_(self) -> None:
        async with DockerComposeRun(DockerComposeRun.Config(
            compose_file=self._config.compose_file,
            service=self._config.service,

            image=await self.resolve_ci_image(),

            cmd=self._config.cmd,

            run_options=[
                '-v', f'{os.path.abspath(self._config.project_dir)}:/project',
                *(self._config.run_options or []),
            ],

            cwd=self._config.project_dir,

            no_dependencies=self._config.no_dependencies,
        )) as ci_compose_run:
            await ci_compose_run.run()

    async def _run_compose(self) -> None:
        with log_timing_context('Run compose'):
            await self._run_compose_()

    #

    async def _run_setup_only(self) -> None:
        image_ids = [
            await self.resolve_ci_image(),

            *(self.get_dependency_images() if not self._config.no_dependencies else []),
        ]

        for image_id in image_ids:
            with log_timing_context(f'Run setup only: {image_id}'):
                await ensure_docker_image_setup(
                    image_id,
                    cwd=self._config.project_dir,
                )

    #

    async def run(self) -> None:
        await self.setup()

        if self._config.setup_only:
            await self._run_setup_only()
        else:
            await self._run_compose()


########################################
# ../docker/inject.py


##


def bind_docker(
        *,
        build_caching_config: DockerBuildCachingImpl.Config,
        cache_served_docker_cache_config: ta.Optional[CacheServedDockerCache.Config] = None,
        image_pulling_config: DockerImagePullingImpl.Config = DockerImagePullingImpl.Config(),
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = []

    #

    lst.extend([
        inj.bind(build_caching_config),
        inj.bind(DockerBuildCachingImpl, singleton=True),
        inj.bind(DockerBuildCaching, to_key=DockerBuildCachingImpl),
    ])

    #

    if cache_served_docker_cache_config is not None:
        lst.extend([
            inj.bind(DockerImageRepositoryOpenerImpl, singleton=True),
            inj.bind(DockerImageRepositoryOpener, to_key=DockerImageRepositoryOpenerImpl),

            inj.bind(cache_served_docker_cache_config),
            inj.bind(CacheServedDockerCache, singleton=True),
            inj.bind(DockerCache, to_key=CacheServedDockerCache),
        ])

    else:
        lst.extend([
            inj.bind(DockerCacheImpl, singleton=True),
            inj.bind(DockerCache, to_key=DockerCacheImpl),
        ])

    #

    lst.extend([
        inj.bind(image_pulling_config),
        inj.bind(DockerImagePullingImpl, singleton=True),
        inj.bind(DockerImagePulling, to_key=DockerImagePullingImpl),
    ])

    #

    return inj.as_bindings(*lst)


########################################
# ../github/cache.py


##


class GithubCache(FileCache, DataCache):
    @dc.dataclass(frozen=True)
    class Config:
        pass

    DEFAULT_CLIENT_VERSION: ta.ClassVar[int] = 2

    DEFAULT_CLIENTS_BY_VERSION: ta.ClassVar[ta.Mapping[int, ta.Callable[..., GithubCacheClient]]] = {
        1: GithubCacheServiceV1Client,
        2: GithubCacheServiceV2Client,
    }

    def __init__(
            self,
            config: Config = Config(),
            *,
            client: ta.Optional[GithubCacheClient] = None,
            default_client_version: ta.Optional[int] = None,

            version: ta.Optional[CacheVersion] = None,

            local: DirectoryFileCache,
    ) -> None:
        super().__init__(
            version=version,
        )

        self._config = config

        if client is None:
            client_cls = self.DEFAULT_CLIENTS_BY_VERSION[default_client_version or self.DEFAULT_CLIENT_VERSION]
            client = client_cls(
                cache_version=self._version,
            )
        self._client: GithubCacheClient = client

        self._local = local

    #

    async def get_file(self, key: str) -> ta.Optional[str]:
        local_file = self._local.get_cache_file_path(key)
        if os.path.exists(local_file):
            return local_file

        if (entry := await self._client.get_entry(key)) is None:
            return None

        tmp_file = self._local.format_incomplete_file(local_file)
        with unlinking_if_exists(tmp_file):
            await self._client.download_file(entry, tmp_file)

            os.replace(tmp_file, local_file)

        return local_file

    async def put_file(
            self,
            key: str,
            file_path: str,
            *,
            steal: bool = False,
    ) -> str:
        cache_file_path = await self._local.put_file(
            key,
            file_path,
            steal=steal,
        )

        await self._client.upload_file(key, cache_file_path)

        return cache_file_path

    #

    async def get_data(self, key: str) -> ta.Optional[DataCache.Data]:
        local_file = self._local.get_cache_file_path(key)
        if os.path.exists(local_file):
            return DataCache.FileData(local_file)

        if (entry := await self._client.get_entry(key)) is None:
            return None

        return DataCache.UrlData(check.non_empty_str(self._client.get_entry_url(entry)))

    async def put_data(self, key: str, data: DataCache.Data) -> None:
        await FileCacheDataCache(self).put_data(key, data)


########################################
# ../github/cli.py
"""
See:
 - https://docs.github.com/en/rest/actions/cache?apiVersion=2022-11-28
"""


##


class GithubCli(ArgparseCli):
    @argparse_cmd()
    def list_referenced_env_vars(self) -> None:
        print('\n'.join(sorted(ev.k for ev in GITHUB_ENV_VARS)))

    @argparse_cmd(
        argparse_arg('key'),
    )
    async def get_cache_entry(self) -> None:
        client = GithubCacheServiceV1Client()
        entry = await client.get_entry(self.args.key)
        if entry is None:
            return
        print(json_dumps_pretty(dc.asdict(entry)))  # noqa

    @argparse_cmd(
        argparse_arg('repository-id'),
    )
    def list_cache_entries(self) -> None:
        raise NotImplementedError


########################################
# ../github/inject.py


##


def bind_github() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(GithubCache, singleton=True),
        inj.bind(DataCache, to_key=GithubCache),
        inj.bind(FileCache, to_key=GithubCache),
    ]

    return inj.as_bindings(*lst)


########################################
# ../inject.py


##


def bind_ci(
        *,
        config: Ci.Config,

        directory_file_cache_config: ta.Optional[DirectoryFileCache.Config] = None,

        github: bool = False,

        cache_served_docker: bool = False,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [  # noqa
        inj.bind(config),
        inj.bind(Ci, singleton=True),
    ]

    lst.append(bind_docker(
        build_caching_config=DockerBuildCachingImpl.Config(
            service=config.service,

            always_build=config.always_build,
        ),

        cache_served_docker_cache_config=CacheServedDockerCache.Config(
            #
        ) if cache_served_docker else None,

        image_pulling_config=DockerImagePullingImpl.Config(
            always_pull=config.always_pull,
        ),
    ))

    if directory_file_cache_config is not None:
        lst.extend([
            inj.bind(directory_file_cache_config),
            inj.bind(DirectoryFileCache, singleton=True),
        ])

        if github:
            lst.append(bind_github())

        else:
            lst.extend([
                inj.bind(FileCache, to_key=DirectoryFileCache),

                inj.bind(FileCacheDataCache, singleton=True),
                inj.bind(DataCache, to_key=FileCacheDataCache),
            ])

    return inj.as_bindings(*lst)


########################################
# cli.py


log = get_module_logger(globals())  # noqa


##


class CiCli(ArgparseCli):
    #

    @argparse_cmd(
        argparse_arg('requirements-txt', nargs='+'),
    )
    def print_requirements_hash(self) -> None:
        requirements_txts = self.args.requirements_txt

        print(build_requirements_hash(requirements_txts))

    #

    @argparse_cmd(
        argparse_arg('compose-file'),
        argparse_arg('service'),
    )
    def dump_compose_deps(self) -> None:
        compose_file = self.args.compose_file
        service = self.args.service

        print(get_compose_service_dependencies(
            compose_file,
            service,
        ))

    #

    @argparse_cmd(
        accepts_unknown=True,
    )
    async def github(self) -> ta.Optional[int]:
        return await GithubCli(self.unknown_args).async_cli_run()

    #

    DEFAULT_PURGE_MAX_AGE_S = 60 * 60 * 24 * 30
    DEFAULT_PURGE_MAX_SIZE_B = 1024 * 1024 * 1024 * 4

    @argparse_cmd(
        argparse_arg('project-dir'),
        argparse_arg('service'),
        argparse_arg('--docker-file'),
        argparse_arg('--compose-file'),
        argparse_arg('-r', '--requirements-txt', action='append'),

        argparse_arg('--cache-dir'),

        argparse_arg('--no-purge', action='store_true'),

        argparse_arg('--github', action='store_true'),
        argparse_arg('--github-detect', action='store_true'),

        argparse_arg('--cache-served-docker', action='store_true'),

        argparse_arg('--setup-concurrency', type=int),

        argparse_arg('--always-pull', action='store_true'),
        argparse_arg('--always-build', action='store_true'),

        argparse_arg('--no-dependencies', action='store_true'),

        argparse_arg('--setup-only', action='store_true'),

        argparse_arg('-e', '--env', action='append'),
        argparse_arg('-v', '--volume', action='append'),

        argparse_arg('cmd', nargs=argparse.REMAINDER),
    )
    async def run(self) -> None:
        project_dir = self.args.project_dir
        docker_file = self.args.docker_file
        compose_file = self.args.compose_file
        requirements_txts = self.args.requirements_txt
        cache_dir = self.args.cache_dir

        #

        cmd = ' '.join(self.args.cmd)
        check.non_empty_str(cmd)

        #

        check.state(os.path.isdir(project_dir))

        #

        def find_alt_file(*alts: str) -> ta.Optional[str]:
            for alt in alts:
                alt_file = os.path.abspath(os.path.join(project_dir, alt))
                if os.path.isfile(alt_file):
                    log.debug('Using %s', alt_file)
                    return alt_file
            return None

        if docker_file is None:
            docker_file = find_alt_file(
                'docker/ci/Dockerfile',
                'docker/ci.Dockerfile',
                'ci.Dockerfile',
                'Dockerfile',
            )
        check.state(os.path.isfile(docker_file))

        if compose_file is None:
            compose_file = find_alt_file(*[
                f'{f}.{x}'
                for f in [
                    'docker/docker-compose',
                    'docker/compose',
                    'docker-compose',
                    'compose',
                ]
                for x in ['yaml', 'yml']
            ])
        check.state(os.path.isfile(compose_file))

        if not requirements_txts:
            requirements_txts = []
            for rf in [
                'requirements.txt',
                'requirements-dev.txt',
                'requirements-ci.txt',
            ]:
                if os.path.exists(os.path.join(project_dir, rf)):
                    log.debug('Using %s', rf)
                    requirements_txts.append(rf)
        else:
            for rf in requirements_txts:
                check.state(os.path.isfile(rf))

        #

        github = self.args.github
        if not github and self.args.github_detect:
            github = is_in_github_actions()
            if github:
                log.debug('Github detected')

        #

        if cache_dir is not None:
            cache_dir = os.path.abspath(cache_dir)
            log.debug('Using cache dir %s', cache_dir)

        #

        run_options: ta.List[str] = []
        for run_arg, run_arg_vals in [
            ('-e', self.args.env or []),
            ('-v', self.args.volume or []),
        ]:
            run_options.extend(itertools.chain.from_iterable(
                [run_arg, run_arg_val]
                for run_arg_val in run_arg_vals
            ))

        #

        config = Ci.Config(
            project_dir=project_dir,

            docker_file=docker_file,

            compose_file=compose_file,
            service=self.args.service,

            requirements_txts=requirements_txts,

            cmd=ShellCmd(cmd),

            always_pull=self.args.always_pull,
            always_build=self.args.always_build,

            setup_concurrency=self.args.setup_concurrency,

            no_dependencies=self.args.no_dependencies,

            setup_only=self.args.setup_only,

            run_options=run_options,
        )

        directory_file_cache_config: ta.Optional[DirectoryFileCache.Config] = None
        if cache_dir is not None:
            directory_file_cache_config = DirectoryFileCache.Config(
                dir=cache_dir,

                no_purge=bool(self.args.no_purge),

                purge_max_age_s=self.DEFAULT_PURGE_MAX_AGE_S,
                purge_max_size_b=self.DEFAULT_PURGE_MAX_SIZE_B,
            )

        injector = inj.create_injector(bind_ci(
            config=config,

            directory_file_cache_config=directory_file_cache_config,

            github=github,

            cache_served_docker=self.args.cache_served_docker,
        ))

        async with injector[Ci] as ci:
            await ci.run()

        if directory_file_cache_config is not None and not directory_file_cache_config.no_purge:
            dfc = injector[DirectoryFileCache]
            dfc.purge()


async def _async_main() -> ta.Optional[int]:
    return await CiCli().async_cli_run()


def _main() -> None:
    configure_standard_logging('DEBUG')

    raise SystemExit(rc if isinstance(rc := asyncio.run(_async_main()), int) else 0)


if __name__ == '__main__':
    _main()
