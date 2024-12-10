import resource


PAGE_SIZE = resource.getpagesize()


def round_to_page_size(sz: int) -> int:
    sz += PAGE_SIZE - 1
    return sz - (sz % PAGE_SIZE)
