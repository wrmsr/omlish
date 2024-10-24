# ruff: noqa: N802 N816
import ctypes as ct
import ctypes.util
import dataclasses as dc
import sys
import typing as ta

from omlish import check


##


if getattr(sys, 'platform') != 'darwin':
    raise OSError(sys.platform)


##
# CoreFoundation

cf = ct.cdll.LoadLibrary(check.not_none(ct.util.find_library('CoreFoundation')))

#

CFArrayRef = ct.c_void_p
CFDataRef = ct.c_void_p
CFIndex = ct.c_long
CFStringEncoding = ct.c_uint32
CFStringRef = ct.c_void_p
CFTypeID = ct.c_ulong

#

cf.CFArrayGetCount.argtypes = [CFArrayRef]
cf.CFArrayGetCount.restype = CFIndex

cf.CFArrayGetValueAtIndex.argtypes = [CFArrayRef, CFIndex]
cf.CFArrayGetValueAtIndex.restype = CFStringRef

cf.CFDataGetBytePtr.argtypes = [CFDataRef]
cf.CFDataGetBytePtr.restype = ct.POINTER(ct.c_uint8)

cf.CFDataGetLength.argtypes = [CFDataRef]
cf.CFDataGetLength.restype = CFIndex

cf.CFGetTypeID.argtypes = [ct.c_void_p]
cf.CFGetTypeID.restype = CFTypeID

cf.CFRelease.argtypes = [ct.c_void_p]
cf.CFRelease.restype = None

cf.CFStringCreateWithCString.argtypes = [ct.c_void_p, ct.c_char_p, ct.c_int32]
cf.CFStringCreateWithCString.restype = CFStringRef

cf.CFStringGetCString.argtypes = [CFStringRef, ct.c_char_p, ct.c_long, ct.c_uint32]
cf.CFStringGetCString.restype = ct.c_bool

cf.CFStringGetLength.argtypes = [CFStringRef]
cf.CFStringGetLength.restype = CFIndex

cf.CFStringGetMaximumSizeForEncoding.argtypes = [CFIndex, CFStringEncoding]
cf.CFStringGetMaximumSizeForEncoding.restype = CFIndex

cf.CFStringGetTypeID.argtypes = []
cf.CFStringGetTypeID.restype = CFTypeID


##
# ApplicationServices

aps = ct.cdll.LoadLibrary(check.not_none(ct.util.find_library('ApplicationServices')))

#

OSStatus = ct.c_int32

PasteboardItemID = ct.c_ulong
PasteboardRef = ct.c_void_p

#

aps.PasteboardCopyItemFlavorData.argtypes = [PasteboardRef, PasteboardItemID, CFStringRef, ct.POINTER(CFDataRef)]
aps.PasteboardCopyItemFlavorData.restype = OSStatus

aps.PasteboardCopyItemFlavors.argtypes = [PasteboardRef, PasteboardItemID, ct.POINTER(CFArrayRef)]
aps.PasteboardCopyItemFlavors.restype = OSStatus

aps.PasteboardCreate.argtypes = [CFStringRef, ct.POINTER(PasteboardRef)]
aps.PasteboardCreate.restype = OSStatus

aps.PasteboardGetItemCount.argtypes = [PasteboardRef, ct.POINTER(ct.c_ulong)]
aps.PasteboardGetItemCount.restype = OSStatus

aps.PasteboardGetItemIdentifier.argtypes = [PasteboardRef, ct.c_ulong, ct.POINTER(PasteboardItemID)]
aps.PasteboardGetItemIdentifier.restype = OSStatus


##


def CFSTR(string):
    return cf.CFStringCreateWithCString(None, string.encode('utf-8'), 0)


kCFStringEncodingUTF8 = 0x08000100
kPasteboardClipboard = CFSTR('com.apple.pasteboard.clipboard')


def cfstring_to_string(cf_string: CFStringRef) -> str:
    if not cf_string:
        return ''

    length = cf.CFStringGetLength(cf_string)
    max_size = cf.CFStringGetMaximumSizeForEncoding(length, kCFStringEncodingUTF8) + 1
    buffer = ct.create_string_buffer(max_size)

    if success := cf.CFStringGetCString(cf_string, buffer, max_size, kCFStringEncodingUTF8):  # noqa
        return ''

    return buffer.value.decode('utf-8')


##


class OsxClipboardError(Exception):
    pass


@dc.dataclass(frozen=True)
class StatusOsxClipboardError(OsxClipboardError):
    fn: str
    status: int


@dc.dataclass(frozen=True)
class OsxClipboardItem:
    type: str | None
    data: bytes | None


def get_osx_clipboard_data(
        *,
        types: ta.Container[str | None] | None = None,
        strict: bool = False,
        types_only: bool = False,
) -> list[OsxClipboardItem]:
    lst: list[OsxClipboardItem] = []

    pasteboard = PasteboardRef()
    if status := aps.PasteboardCreate(kPasteboardClipboard, ct.byref(pasteboard)):
        raise StatusOsxClipboardError('PasteboardCreate', status)

    try:
        item_count = ct.c_ulong(0)
        if status := aps.PasteboardGetItemCount(pasteboard, ct.byref(item_count)):
            raise StatusOsxClipboardError('PasteboardGetItemCount', status)

        for i in range(1, item_count.value + 1):
            item_id = PasteboardItemID()
            if status := aps.PasteboardGetItemIdentifier(pasteboard, i, ct.byref(item_id)):
                raise StatusOsxClipboardError('PasteboardGetItemIdentifier', status)

            data_types = CFArrayRef()
            if status := aps.PasteboardCopyItemFlavors(pasteboard, item_id, ct.byref(data_types)):
                raise StatusOsxClipboardError('PasteboardCopyItemFlavors', status)
            if not data_types:
                continue

            try:
                type_count = cf.CFArrayGetCount(data_types)
                for j in range(type_count):
                    data_type = cf.CFArrayGetValueAtIndex(data_types, j)

                    if cf.CFGetTypeID(data_type) == cf.CFStringGetTypeID():
                        data_type_str = cfstring_to_string(data_type)
                    else:
                        data_type_str = None

                    if types is not None and data_type_str not in types:
                        continue

                    if types_only:
                        lst.append(OsxClipboardItem(
                            type=data_type_str,
                            data=None,
                        ))
                        continue

                    data = CFDataRef()
                    if status := aps.PasteboardCopyItemFlavorData(pasteboard, item_id, data_type, ct.byref(data)):
                        if not strict:
                            continue
                        raise StatusOsxClipboardError('PasteboardCopyItemFlavorData', status)
                    if not data:
                        continue

                    try:
                        data_size = cf.CFDataGetLength(data)
                        data_ptr = cf.CFDataGetBytePtr(data)
                        data_bytes = ct.string_at(data_ptr, data_size)

                        lst.append(OsxClipboardItem(
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


def _main() -> None:
    for i in get_osx_clipboard_data():
        print(i)


if __name__ == '__main__':
    _main()
