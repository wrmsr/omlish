from .. import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .clients.asyncs import (  # noqa
        AsyncStreamHttpResponse,

        async_close_http_client_response,
        async_closing_http_client_response,
        async_read_http_client_response,

        AsyncHttpClient,
    )

    from .clients.base import (  # noqa
        DEFAULT_ENCODING,
        is_success_status,

        HttpRequest,

        BaseHttpResponse,
        HttpResponse,

        HttpClientContext,

        HttpClientError,
        HttpStatusError,

        BaseHttpClient,
    )

    from .clients.default import (  # noqa
        client,
        manage_client,

        request,

        async_client,
        manage_async_client,

        async_request,
    )

    from .clients.httpx import (  # noqa
        HttpxHttpClient,

        HttpxAsyncHttpClient,
    )

    from .clients.middleware import (  # noqa
        HttpClientMiddleware,
        AbstractMiddlewareHttpClient,

        MiddlewareHttpClient,
        MiddlewareAsyncHttpClient,

        TooManyRedirectsHttpClientError,
        RedirectHandlingHttpClientMiddleware,
    )

    from .clients.sync import (  # noqa
        StreamHttpResponse,

        close_http_client_response,
        closing_http_client_response,
        read_http_client_response,

        HttpClient,
    )

    from .clients.syncasync import (  # noqa
        SyncAsyncHttpClient,
    )

    from .clients.urllib import (  # noqa
        UrllibHttpClient,
    )

    from . import asgi  # noqa

    from . import consts  # noqa

    from .cookies import (  # noqa
        CookieTooBigError,
        dump_cookie,
        parse_cookie,
    )

    from .dates import (  # noqa
        http_date,
        parse_date,
    )

    from .encodings import (  # noqa
        latin1_decode,
        latin1_encode,
    )

    from .headers import (  # noqa
        CanHttpHeaders,
        DuplicateHttpHeaderError,
        HttpHeaders,
        headers,
    )

    from .json import (  # noqa
        JSON_TAGGER,
        JsonTag,
        JsonTagger,
        json_dumps,
        json_loads,
    )

    from .multipart import (  # noqa
        MultipartData,
        MultipartEncoder,
        MultipartField,
    )

    from . import wsgi  # noqa
