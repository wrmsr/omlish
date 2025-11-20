"""
https://docs.tavily.com/documentation/api-reference/endpoint/search
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


def _set_class_marshal_options(cls):
    msh.update_object_metadata(
        cls,
        field_defaults=msh.FieldMetadata(
            options=msh.FieldOptions(
                omit_if=lang.is_none,
            ),
        ),
    )

    return cls


##


KNOWN_COUNTRIES = frozenset([
    'afghanistan',
    'albania',
    'algeria',
    'andorra',
    'angola',
    'argentina',
    'armenia',
    'australia',
    'austria',
    'azerbaijan',
    'bahamas',
    'bahrain',
    'bangladesh',
    'barbados',
    'belarus',
    'belgium',
    'belize',
    'benin',
    'bhutan',
    'bolivia',
    'bosnia and herzegovina',
    'botswana',
    'brazil',
    'brunei',
    'bulgaria',
    'burkina faso',
    'burundi',
    'cambodia',
    'cameroon',
    'canada',
    'cape verde',
    'central african republic',
    'chad',
    'chile',
    'china',
    'colombia',
    'comoros',
    'congo',
    'costa rica',
    'croatia',
    'cuba',
    'cyprus',
    'czech republic',
    'denmark',
    'djibouti',
    'dominican republic',
    'ecuador',
    'egypt',
    'el salvador',
    'equatorial guinea',
    'eritrea',
    'estonia',
    'ethiopia',
    'fiji',
    'finland',
    'france',
    'gabon',
    'gambia',
    'georgia',
    'germany',
    'ghana',
    'greece',
    'guatemala',
    'guinea',
    'haiti',
    'honduras',
    'hungary',
    'iceland',
    'india',
    'indonesia',
    'iran',
    'iraq',
    'ireland',
    'israel',
    'italy',
    'jamaica',
    'japan',
    'jordan',
    'kazakhstan',
    'kenya',
    'kuwait',
    'kyrgyzstan',
    'latvia',
    'lebanon',
    'lesotho',
    'liberia',
    'libya',
    'liechtenstein',
    'lithuania',
    'luxembourg',
    'madagascar',
    'malawi',
    'malaysia',
    'maldives',
    'mali',
    'malta',
    'mauritania',
    'mauritius',
    'mexico',
    'moldova',
    'monaco',
    'mongolia',
    'montenegro',
    'morocco',
    'mozambique',
    'myanmar',
    'namibia',
    'nepal',
    'netherlands',
    'new zealand',
    'nicaragua',
    'niger',
    'nigeria',
    'north korea',
    'north macedonia',
    'norway',
    'oman',
    'pakistan',
    'panama',
    'papua new guinea',
    'paraguay',
    'peru',
    'philippines',
    'poland',
    'portugal',
    'qatar',
    'romania',
    'russia',
    'rwanda',
    'saudi arabia',
    'senegal',
    'serbia',
    'singapore',
    'slovakia',
    'slovenia',
    'somalia',
    'south africa',
    'south korea',
    'south sudan',
    'spain',
    'sri lanka',
    'sudan',
    'sweden',
    'switzerland',
    'syria',
    'taiwan',
    'tajikistan',
    'tanzania',
    'thailand',
    'togo',
    'trinidad and tobago',
    'tunisia',
    'turkey',
    'turkmenistan',
    'uganda',
    'ukraine',
    'united arab emirates',
    'united kingdom',
    'united states',
    'uruguay',
    'uzbekistan',
    'venezuela',
    'vietnam',
    'yemen',
    'zambia',
    'zimbabwe',
])


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SearchRequest:
    query: str

    # optional
    auto_parameters: bool | None = None

    topic: ta.Literal['general', 'news', 'finance'] | None = None
    search_depth: ta.Literal['basic', 'advanced'] | None = None

    chunks_per_source: int | None = None
    max_results: int | None = None

    time_range: ta.Literal['day', 'week', 'month', 'year', 'd', 'w', 'm', 'y'] | None = None
    start_date: str | None = None  # YYYY-MM-DD
    end_date: str | None = None    # YYYY-MM-DD

    # Booleans with extra enum-like modes per docs
    include_answer: bool | ta.Literal['basic', 'advanced'] | None = None
    include_raw_content: bool | ta.Literal['markdown', 'text'] | None = None

    include_images: bool | None = None
    include_image_descriptions: bool | None = None
    include_favicon: bool | None = None

    include_domains: ta.Sequence[str] | None = None
    exclude_domains: ta.Sequence[str] | None = None

    country: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SearchResponse:
    query: str
    answer: str

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Image:
        url: str | None = None
        description: str | None = None

    images: ta.Sequence[Image] | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Result:
        title: str | None = None
        url: str | None = None
        content: str | None = None
        score: float | None = None
        raw_content: str | None = None
        favicon: str | None = None

    results: ta.Sequence[Result] | None = None

    follow_up_questions: ta.Sequence[str] | None = None

    auto_parameters: ta.Mapping[str, ta.Any] | None = None

    response_time: str | None = None  # seconds
    request_id: str | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class ExtractRequest:
    urls: str | ta.Sequence[str]
    include_images: bool | None = None
    include_favicon: bool | None = None
    extract_depth: ta.Literal['basic', 'advanced'] | None = None
    format: ta.Literal['markdown', 'text'] | None = None
    timeout: str | None = None  # seconds


@dc.dataclass(frozen=True, kw_only=True)
class ExtractResponse:
    @dc.dataclass(frozen=True, kw_only=True)
    class Result:
        url: str
        raw_content: str
        images: ta.Sequence[str] | None = None
        favicon: str | None = None

    results: ta.Sequence[Result]

    @dc.dataclass(frozen=True, kw_only=True)
    class FailedResult:
        url: str
        error: str

    failed_results: ta.Sequence[FailedResult] | None = None

    response_time: str | None = None
    request_id: str | None = None
