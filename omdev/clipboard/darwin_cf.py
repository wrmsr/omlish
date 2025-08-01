# ruff: noqa: N802 N816
import ctypes as ct
import dataclasses as dc
import typing as ta

from ..capi.darwin import aps
from ..capi.darwin import cf
from .clipboard import Clipboard
from .clipboard import ClipboardContents
from .clipboard import ImageClipboardContents
from .clipboard import TextClipboardContents


##


kPasteboardClipboard = cf.string('com.apple.pasteboard.clipboard')


##


class DarwinClipboardError(Exception):
    pass


@dc.dataclass(frozen=True)
class StatusDarwinClipboardError(DarwinClipboardError):
    fn: str
    status: int


@dc.dataclass(frozen=True)
class DarwinClipboardItem:
    type: str | None
    data: bytes | None


def get_darwin_clipboard_data(
        *,
        types: ta.Container[str | None] | None = None,
        skip_types: ta.Container[str | None] | None = None,
        strict: bool = False,
        types_only: bool = False,
) -> list[DarwinClipboardItem]:
    lst: list[DarwinClipboardItem] = []

    pasteboard = aps.PasteboardRef()
    if status := aps.PasteboardCreate(kPasteboardClipboard, ct.byref(pasteboard)):
        raise StatusDarwinClipboardError('PasteboardCreate', status)

    try:
        item_count = ct.c_ulong(0)
        if status := aps.PasteboardGetItemCount(pasteboard, ct.byref(item_count)):
            raise StatusDarwinClipboardError('PasteboardGetItemCount', status)

        for i in range(1, item_count.value + 1):
            item_id = aps.PasteboardItemID()
            if status := aps.PasteboardGetItemIdentifier(pasteboard, i, ct.byref(item_id)):
                raise StatusDarwinClipboardError('PasteboardGetItemIdentifier', status)

            data_types = cf.CFArrayRef()
            if status := aps.PasteboardCopyItemFlavors(pasteboard, item_id, ct.byref(data_types)):
                raise StatusDarwinClipboardError('PasteboardCopyItemFlavors', status)
            if not data_types:
                continue

            try:
                type_count = cf.CFArrayGetCount(data_types)
                for j in range(type_count):
                    data_type = cf.CFArrayGetValueAtIndex(data_types, j)

                    if cf.CFGetTypeID(data_type) == cf.CFStringGetTypeID():
                        data_type_str = cf.read_string(data_type)
                    else:
                        data_type_str = None

                    if types is not None and data_type_str not in types:
                        continue
                    if skip_types is not None and data_type_str in skip_types:
                        continue

                    if types_only:
                        lst.append(DarwinClipboardItem(
                            type=data_type_str,
                            data=None,
                        ))
                        continue

                    data = cf.CFDataRef()

                    # FIXME: dumps to stderr lol:
                    #  data_type_str = 'public.heics'
                    if status := aps.PasteboardCopyItemFlavorData(pasteboard, item_id, data_type, ct.byref(data)):
                        if not strict:
                            continue
                        raise StatusDarwinClipboardError('PasteboardCopyItemFlavorData', status)

                    if not data:
                        continue

                    try:
                        data_size = cf.CFDataGetLength(data)
                        data_ptr = cf.CFDataGetBytePtr(data)
                        data_bytes = ct.string_at(data_ptr, data_size)

                        lst.append(DarwinClipboardItem(
                            type=data_type_str,
                            data=data_bytes,
                        ))

                    finally:
                        cf.CFRelease(data)

            finally:
                cf.CFRelease(data_types)

    finally:
        cf.CFRelease(pasteboard)

    return lst


##


_TEXT_TYPE = 'public.utf8-plain-text'
_IMAGE_TYPE = 'public.png'


class CfDarwinClipboard(Clipboard):
    def get(self) -> list[ClipboardContents]:
        ret: list[ClipboardContents] = []
        for i in get_darwin_clipboard_data(types={_TEXT_TYPE, _IMAGE_TYPE}):
            if i.type == _TEXT_TYPE:
                if i.data is not None:
                    ret.append(TextClipboardContents(i.data.decode('utf-8')))
            elif i.type == _IMAGE_TYPE:
                if i.data is not None:
                    ret.append(ImageClipboardContents(i.data))
            else:
                raise KeyError(i.type)
        return ret

    def put(self, c: ClipboardContents) -> None:
        raise TypeError(self)


##


def _main() -> None:
    for i in get_darwin_clipboard_data(skip_types={'public.heics'}):
        print(f'type: {i.type}, len: {len(i.data) if i.data is not None else None}')


if __name__ == '__main__':
    _main()
