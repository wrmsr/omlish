import ctypes
import ctypes.util


# Load the required frameworks
core_foundation = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreFoundation'))
application_services = ctypes.cdll.LoadLibrary(ctypes.util.find_library('ApplicationServices'))

# Constants
kPasteboardClipboard = ctypes.c_void_p.in_dll(application_services, 'kPasteboardClipboard')

# CoreFoundation Data Types
CFIndex = ctypes.c_long
CFStringRef = ctypes.c_void_p
CFDataRef = ctypes.c_void_p
CFArrayRef = ctypes.c_void_p
PasteboardRef = ctypes.c_void_p
PasteboardItemID = ctypes.c_ulong

# OSStatus is represented as an integer
OSStatus = ctypes.c_int32

# Function prototypes

# OSStatus PasteboardCreate(CFStringRef, PasteboardRef*)
PasteboardCreate = application_services.PasteboardCreate
PasteboardCreate.argtypes = [CFStringRef, ctypes.POINTER(PasteboardRef)]
PasteboardCreate.restype = OSStatus

# OSStatus PasteboardGetItemCount(PasteboardRef, ItemCount*)
PasteboardGetItemCount = application_services.PasteboardGetItemCount
PasteboardGetItemCount.argtypes = [PasteboardRef, ctypes.POINTER(ctypes.c_ulong)]
PasteboardGetItemCount.restype = OSStatus

# OSStatus PasteboardGetItemIdentifier(PasteboardRef, ItemIndex, PasteboardItemID*)
PasteboardGetItemIdentifier = application_services.PasteboardGetItemIdentifier
PasteboardGetItemIdentifier.argtypes = [PasteboardRef, ctypes.c_ulong, ctypes.POINTER(PasteboardItemID)]
PasteboardGetItemIdentifier.restype = OSStatus

# OSStatus PasteboardCopyItemFlavors(PasteboardRef, PasteboardItemID, CFArrayRef*)
PasteboardCopyItemFlavors = application_services.PasteboardCopyItemFlavors
PasteboardCopyItemFlavors.argtypes = [PasteboardRef, PasteboardItemID, ctypes.POINTER(CFArrayRef)]
PasteboardCopyItemFlavors.restype = OSStatus

# OSStatus PasteboardCopyItemFlavorData(PasteboardRef, PasteboardItemID, CFStringRef, CFDataRef*)
PasteboardCopyItemFlavorData = application_services.PasteboardCopyItemFlavorData
PasteboardCopyItemFlavorData.argtypes = [PasteboardRef, PasteboardItemID, CFStringRef, ctypes.POINTER(CFDataRef)]
PasteboardCopyItemFlavorData.restype = OSStatus

# CFIndex CFArrayGetCount(CFArrayRef)
CFArrayGetCount = core_foundation.CFArrayGetCount
CFArrayGetCount.argtypes = [CFArrayRef]
CFArrayGetCount.restype = CFIndex

# CFStringRef CFArrayGetValueAtIndex(CFArrayRef, CFIndex)
CFArrayGetValueAtIndex = core_foundation.CFArrayGetValueAtIndex
CFArrayGetValueAtIndex.argtypes = [CFArrayRef, CFIndex]
CFArrayGetValueAtIndex.restype = CFStringRef

# CFIndex CFDataGetLength(CFDataRef)
CFDataGetLength = core_foundation.CFDataGetLength
CFDataGetLength.argtypes = [CFDataRef]
CFDataGetLength.restype = CFIndex

# const UInt8 *CFDataGetBytePtr(CFDataRef)
CFDataGetBytePtr = core_foundation.CFDataGetBytePtr
CFDataGetBytePtr.argtypes = [CFDataRef]
CFDataGetBytePtr.restype = ctypes.POINTER(ctypes.c_uint8)

# CFRelease
CFRelease = core_foundation.CFRelease
CFRelease.argtypes = [ctypes.c_void_p]
CFRelease.restype = None


def get_clipboard_data():
    # Create the pasteboard reference
    pasteboard = PasteboardRef()
    status = PasteboardCreate(kPasteboardClipboard, ctypes.byref(pasteboard))

    if status != 0:
        print("Failed to access the clipboard")
        return

    # Get the number of items in the clipboard
    item_count = ctypes.c_ulong(0)
    status = PasteboardGetItemCount(pasteboard, ctypes.byref(item_count))
    if status != 0 or item_count.value == 0:
        print("No items on the clipboard")
        return

    # Iterate over each item in the clipboard
    for i in range(1, item_count.value + 1):
        item_id = PasteboardItemID()
        status = PasteboardGetItemIdentifier(pasteboard, i, ctypes.byref(item_id))
        if status != 0:
            continue

        # Get available data types for the current item
        data_types = CFArrayRef()
        status = PasteboardCopyItemFlavors(pasteboard, item_id, ctypes.byref(data_types))
        if status != 0 or not data_types:
            continue

        # Iterate through data types to find supported ones
        type_count = CFArrayGetCount(data_types)
        for j in range(type_count):
            data_type = CFArrayGetValueAtIndex(data_types, j)

            # Convert CFStringRef to Python string for display
            data_type_str = cfstring_to_string(data_type)
            print(f"Data type: {data_type_str}")

            # Retrieve data of this type
            data = CFDataRef()
            status = PasteboardCopyItemFlavorData(pasteboard, item_id, data_type, ctypes.byref(data))
            if status == 0 and data:
                # Handle the binary data (e.g., images, files, etc.)
                data_size = CFDataGetLength(data)
                data_ptr = CFDataGetBytePtr(data)

                # Save to a file for testing
                with open("clipboard_output.bin", "wb") as f:
                    f.write(ctypes.string_at(data_ptr, data_size))
                    print(f"Data saved to clipboard_output.bin (size: {data_size} bytes)")

                CFRelease(data)

        CFRelease(data_types)

    CFRelease(pasteboard)


def cfstring_to_string(cf_string):
    """Convert a CFStringRef to a Python string."""
    if not cf_string:
        return ""

    length = core_foundation.CFStringGetLength(cf_string)
    buffer = ctypes.create_unicode_buffer(length)
    core_foundation.CFStringGetCString(cf_string, buffer, len(buffer), 0)
    return buffer.value


if __name__ == "__main__":
    get_clipboard_data()
