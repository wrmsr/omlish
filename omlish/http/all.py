from .. import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .clients.base import (  # noqa
        DEFAULT_ENCODING,

        is_success_status,

        HttpRequest,

        BaseHttpResponse,
        HttpResponse,

        HttpClientError,
        HttpStatusError,
    )

    from .clients.default import (  # noqa
        client,

        request,
    )

    from .clients.httpx import (  # noqa
        HttpxHttpClient,
    )

    from .clients.sync import (  # noqa
        StreamHttpResponse,

        close_response,
        closing_response,
        read_response,

        HttpClient,
    )

    from .clients.urllib import (  # noqa
        UrllibHttpClient,
    )

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
