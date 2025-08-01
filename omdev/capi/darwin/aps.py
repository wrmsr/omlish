import ctypes as ct
import ctypes.util
import typing as ta

from omlish import check

from . import cf


##


aps = ct.cdll.LoadLibrary(check.not_none(ct.util.find_library('ApplicationServices')))


OSStatus: ta.TypeAlias = ct.c_int32

PasteboardItemID: ta.TypeAlias = ct.c_ulong
PasteboardRef: ta.TypeAlias = ct.c_void_p

PasteboardCopyItemFlavorData = aps.PasteboardCopyItemFlavorData
PasteboardCopyItemFlavorData.argtypes = [PasteboardRef, PasteboardItemID, cf.CFStringRef, ct.POINTER(cf.CFDataRef)]
PasteboardCopyItemFlavorData.restype = OSStatus

PasteboardCopyItemFlavors = aps.PasteboardCopyItemFlavors
PasteboardCopyItemFlavors.argtypes = [PasteboardRef, PasteboardItemID, ct.POINTER(cf.CFArrayRef)]
PasteboardCopyItemFlavors.restype = OSStatus

PasteboardCreate = aps.PasteboardCreate
PasteboardCreate.argtypes = [cf.CFStringRef, ct.POINTER(PasteboardRef)]
PasteboardCreate.restype = OSStatus

PasteboardGetItemCount = aps.PasteboardGetItemCount
PasteboardGetItemCount.argtypes = [PasteboardRef, ct.POINTER(ct.c_ulong)]
PasteboardGetItemCount.restype = OSStatus

PasteboardGetItemIdentifier = aps.PasteboardGetItemIdentifier
PasteboardGetItemIdentifier.argtypes = [PasteboardRef, ct.c_ulong, ct.POINTER(PasteboardItemID)]
PasteboardGetItemIdentifier.restype = OSStatus
