# """
# https://developers.google.com/custom-search/vo1/reference/rest/v1/cse/list?apix=true
# https://developers.google.com/custom-search/v1/reference/rest/v1/Search
# https://google.aip.dev/127
# """
# import urllib.request
# import typing as ta
#
# from omdev.secrets import load_secrets
# from omlish import dataclasses as dc
# from omlish import marshal as msh
# from omlish import lang
# from omlish.formats import json
#
#
# @dc.dataclass(frozen=True)
# @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
# class SearchResult(lang.Final):
#     kind: str | None = None
#
#     title: str | None = None
#     html_title: str | None = None
#
#     link: str | None = None
#     display_link: str | None = None
#
#     snippet: str | None = None
#     html_snippet: str | None = None
#
#     cacheId: str | None = None
#
#     formatted_url: str | None = None
#     html_formatted_url: str | None = None
#
#     mime: str | None = None
#     file_format: str | None = None
#
#     x: ta.Mapping[str, ta.Any] | None = dc.field(default=None, repr=False)
#
#
# @dc.dataclass(frozen=True)
# @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
# class SearchInfo(lang.Final):
#     search_time: float | None = None
#     total_results: int | None = None
#
#     x: ta.Mapping[str, ta.Any] | None = dc.field(default=None, repr=False)
#
#
# @dc.dataclass(frozen=True)
# @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL, unknown_field='x')
# class SearchResponse(lang.Final):
#     kind: str | None = None
#     info: SearchInfo | None = dc.xfield(None) | msh.update_field_metadata(name='searchInformation')
#     items: ta.Sequence[SearchResult] | None = None
#
#     x: ta.Mapping[str, ta.Any] | None = dc.field(default=None, repr=False)
#
#
# def _main() -> None:
#     sec = load_secrets()
#     cse_id = sec.get('google_cse_id')
#     cse_api_key = sec.get('google_cse_api_key')
#
#     with urllib.request.urlopen(
#         f'https://www.googleapis.com/customsearch/v1'
#         f'?key={cse_api_key.reveal()}'
#         f'&cx={cse_id.reveal()}'
#         # f':omuauf_lfve'
#         f'&q=lectures'
#     ) as resp:
#         out = resp.read()
#
#     dct = json.loads(out.decode('utf-8'))
#     res = msh.unmarshal(dct, SearchResponse)
#     print(res)
#
#
# if __name__ == '__main__':
#     _main()
