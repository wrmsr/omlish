# @omlish-lite
import urllib.request


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
