import ctypes
import ctypes.util


# Load the required frameworks
core_foundation = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreFoundation'))
application_services = ctypes.cdll.LoadLibrary(ctypes.util.find_library('ApplicationServices'))

# CoreFoundation data types
CFStringRef = ctypes.c_void_p
CFTypeID = ctypes.c_ulong
PasteboardRef = ctypes.c_void_p
CFIndex = ctypes.c_long
CFArrayRef = ctypes.c_void_p
CFDataRef = ctypes.c_void_p
PasteboardItemID = ctypes.c_ulong
OSStatus = ctypes.c_int32


# Define CFSTR to create CFStringRef constants
def CFSTR(string):
    core_foundation.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int32]
    core_foundation.CFStringCreateWithCString.restype = CFStringRef
    return core_foundation.CFStringCreateWithCString(None, string.encode('utf-8'), 0)


# Define kPasteboardClipboard
kPasteboardClipboard = CFSTR("com.apple.pasteboard.clipboard")

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

# CFTypeID CFGetTypeID(CFTypeRef)
CFGetTypeID = core_foundation.CFGetTypeID
CFGetTypeID.argtypes = [ctypes.c_void_p]
CFGetTypeID.restype = CFTypeID

# CFTypeID CFStringGetTypeID(void)
CFStringGetTypeID = core_foundation.CFStringGetTypeID
CFStringGetTypeID.restype = CFTypeID

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

            # Strictly check if the flavor is a CFStringRef
            if CFGetTypeID(data_type) == CFStringGetTypeID():
                data_type_str = cfstring_to_string(data_type)
                print(f"Data type: {data_type_str}")
            else:
                print("Data type is not a CFStringRef, skipping.")

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


# Correctly set the argument and return types for CFStringGetCString
core_foundation.CFStringGetCString.argtypes = [CFStringRef, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint32]
core_foundation.CFStringGetCString.restype = ctypes.c_bool


def cfstring_to_string(cf_string):
    """Convert a CFStringRef to a Python string."""
    if not cf_string:
        return ""

    # Define kCFStringEncodingUTF8 (the correct encoding constant for UTF-8)
    kCFStringEncodingUTF8 = 0x08000100

    # Calculate the maximum buffer size needed for the string
    length = core_foundation.CFStringGetLength(cf_string)
    max_size = core_foundation.CFStringGetMaximumSizeForEncoding(length, kCFStringEncodingUTF8) + 1

    # Create a buffer to hold the C string
    buffer = ctypes.create_string_buffer(max_size)

    # Attempt to convert CFStringRef to a C string
    success = core_foundation.CFStringGetCString(
        cf_string,
        buffer,
        max_size,
        kCFStringEncodingUTF8
    )

    # If conversion fails, return an empty string
    if not success:
        return ""

    return buffer.value.decode('utf-8')

if __name__ == "__main__":
    get_clipboard_data()
