from omnibus import check


def quote(val: str, quote: str) -> str:
    return quote + val.replace(quote, quote * 2) + quote


def unquote(val: str, quote: str) -> str:
    check.arg(val.startswith(quote) and val.endswith(quote))
    return val[1:-1].replace(quote * 2, quote)
