import ctypes as ct
import ctypes.util


##
# CoreFoundation


cf = ct.cdll.LoadLibrary(ct.util.find_library('CoreFoundation'))

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


aps = ct.cdll.LoadLibrary(ct.util.find_library('ApplicationServices'))

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


kPasteboardClipboard = CFSTR('com.apple.pasteboard.clipboard')


def cfstring_to_string(cf_string):
    """Convert a CFStringRef to a Python string."""

    if not cf_string:
        return ""

    # Define kCFStringEncodingUTF8 (the correct encoding constant for UTF-8)
    kCFStringEncodingUTF8 = 0x08000100

    # Calculate the maximum buffer size needed for the string
    length = cf.CFStringGetLength(cf_string)
    max_size = cf.CFStringGetMaximumSizeForEncoding(length, kCFStringEncodingUTF8) + 1

    # Create a buffer to hold the C string
    buffer = ct.create_string_buffer(max_size)

    # Attempt to convert CFStringRef to a C string
    success = cf.CFStringGetCString(
        cf_string,
        buffer,
        max_size,
        kCFStringEncodingUTF8
    )

    # If conversion fails, return an empty string
    if not success:
        return ""

    return buffer.value.decode('utf-8')


##


def get_clipboard_data():
    # Create the pasteboard reference
    pasteboard = PasteboardRef()
    status = aps.PasteboardCreate(kPasteboardClipboard, ct.byref(pasteboard))
    if status != 0:
        print("Failed to access the clipboard")
        return

    try:
        # Get the number of items in the clipboard
        item_count = ct.c_ulong(0)
        status = aps.PasteboardGetItemCount(pasteboard, ct.byref(item_count))
        if status != 0 or item_count.value == 0:
            print("No items on the clipboard")
            return

        # Iterate over each item in the clipboard
        for i in range(1, item_count.value + 1):
            item_id = PasteboardItemID()
            status = aps.PasteboardGetItemIdentifier(pasteboard, i, ct.byref(item_id))
            if status != 0:
                continue

            # Get available data types for the current item
            data_types = CFArrayRef()
            status = aps.PasteboardCopyItemFlavors(pasteboard, item_id, ct.byref(data_types))
            if status != 0 or not data_types:
                continue

            try:
                # Iterate through data types to find supported ones
                type_count = cf.CFArrayGetCount(data_types)
                for j in range(type_count):
                    data_type = cf.CFArrayGetValueAtIndex(data_types, j)

                    # Strictly check if the flavor is a CFStringRef
                    if cf.CFGetTypeID(data_type) == cf.CFStringGetTypeID():
                        data_type_str = cfstring_to_string(data_type)
                    else:
                        data_type_str = None

                    # Retrieve data of this type
                    data = CFDataRef()
                    try:
                        status = aps.PasteboardCopyItemFlavorData(pasteboard, item_id, data_type, ct.byref(data))
                        if status == 0 and data:
                            # Handle the binary data (e.g., images, files, etc.)
                            data_size = cf.CFDataGetLength(data)
                            data_ptr = cf.CFDataGetBytePtr(data)
                            data_bytes = ct.string_at(data_ptr, data_size)

                            # Save to a file for testing
                            print(f'Data (type: {data_type_str}, size: {data_size}): {data_bytes!r}')

                    finally:
                        cf.CFRelease(data)

            finally:
                cf.CFRelease(data_types)

    finally:
        cf.CFRelease(pasteboard)


if __name__ == "__main__":
    get_clipboard_data()
