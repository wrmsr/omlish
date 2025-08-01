import contextlib
import ctypes as ct
import ctypes.util
import typing as ta


T = ta.TypeVar('T')


##


cf = ct.CDLL(ct.util.find_library('CoreFoundation'))


##
# type aliases

CFArrayRef: ta.TypeAlias = ct.c_void_p
CFDataRef: ta.TypeAlias = ct.c_void_p
CFIndex: ta.TypeAlias = ct.c_long
CFStringEncoding: ta.TypeAlias = ct.c_uint32
CFStringRef: ta.TypeAlias = ct.c_void_p
CFTypeID: ta.TypeAlias = ct.c_ulong

##
# ref counts

CFRetain = cf.CFRetain
CFRetain.argtypes = [ct.c_void_p]
CFRetain.restype = ct.c_void_p

# void CFRelease(CFTypeRef cf)
CFRelease = cf.CFRelease
CFRelease.argtypes = [ct.c_void_p]
CFRelease.restype = None

##
# arrays

# CFIndex CFArrayGetCount(CFArrayRef theArray)
CFArrayGetCount = cf.CFArrayGetCount
CFArrayGetCount.argtypes = [CFArrayRef]
CFArrayGetCount.restype = CFIndex

# const void *CFArrayGetValueAtIndex(CFArrayRef theArray, CFIndex idx)
CFArrayGetValueAtIndex = cf.CFArrayGetValueAtIndex
CFArrayGetValueAtIndex.argtypes = [CFArrayRef, CFIndex]
CFArrayGetValueAtIndex.restype = CFStringRef

##
# dicts

# const void *CFDictionaryGetValue(CFDictionaryRef theDict, const void *key)
CFDictionaryGetValue = cf.CFDictionaryGetValue
CFDictionaryGetValue.argtypes = [ct.c_void_p, ct.c_void_p]
CFDictionaryGetValue.restype = ct.c_void_p

##
# strings

kCFStringEncodingUTF8 = 0x08000100  # noqa

# CFStringRef CFStringCreateWithCString(CFAllocatorRef alloc, const char *cStr, CFStringEncoding encoding)
CFStringCreateWithCString = cf.CFStringCreateWithCString
CFStringCreateWithCString.argtypes = [ct.c_void_p, ct.c_char_p, ct.c_uint32]
CFStringCreateWithCString.restype = CFStringRef

# Boolean CFStringGetCString(CFStringRef theString, char *buffer, CFIndex bufferSize, CFStringEncoding encoding)
CFStringGetCString = cf.CFStringGetCString
CFStringGetCString.argtypes = [CFStringRef, ct.c_char_p, ct.c_long, ct.c_uint32]
CFStringGetCString.restype = ct.c_bool

CFStringGetLength = cf.CFStringGetLength
CFStringGetLength.argtypes = [CFStringRef]
CFStringGetLength.restype = CFIndex

CFStringGetMaximumSizeForEncoding = cf.CFStringGetMaximumSizeForEncoding
CFStringGetMaximumSizeForEncoding.argtypes = [CFIndex, CFStringEncoding]
CFStringGetMaximumSizeForEncoding.restype = CFIndex

CFStringGetTypeID = cf.CFStringGetTypeID
CFStringGetTypeID.argtypes = []
CFStringGetTypeID.restype = CFTypeID

##
# numbers

kCFNumberIntType = 9  # noqa
kCFNumberCGFloatType = 16  # noqa

# Boolean CFNumberGetValue(CFNumberRef number, CFNumberType theType, void *valuePtr)
CFNumberGetValue = cf.CFNumberGetValue
CFNumberGetValue.argtypes = [ct.c_void_p, ct.c_int, ct.c_void_p]
CFNumberGetValue.restype = ct.c_bool

##
# other

CFDataGetBytePtr = cf.CFDataGetBytePtr
CFDataGetBytePtr.argtypes = [CFDataRef]
CFDataGetBytePtr.restype = ct.POINTER(ct.c_uint8)

CFDataGetLength = cf.CFDataGetLength
CFDataGetLength.argtypes = [CFDataRef]
CFDataGetLength.restype = CFIndex

CFGetTypeID = cf.CFGetTypeID
CFGetTypeID.argtypes = [ct.c_void_p]
CFGetTypeID.restype = CFTypeID


##


def es_release(es: contextlib.ExitStack, p: T) -> T:
    if p:
        es.callback(CFRelease, p)
    return p


#


def string(s: ta.Any, encoding: ta.Any = None) -> CFStringRef:
    if isinstance(s, str) and encoding is None:
        s = s.encode('utf-8')
        encoding = kCFStringEncodingUTF8
    elif encoding is None:
        encoding = kCFStringEncodingUTF8
    return CFStringCreateWithCString(None, s, encoding)


def es_string(es: contextlib.ExitStack, s: ta.Any, encoding: ta.Any = None) -> CFStringRef:
    p = string(s, encoding)
    es_release(es, p)
    return p


def read_string(p: CFStringRef) -> str | None:
    if not p:
        return None

    sz = cf.CFStringGetLength(p)
    max_sz = cf.CFStringGetMaximumSizeForEncoding(sz, kCFStringEncodingUTF8) + 1
    buf = ct.create_string_buffer(max_sz)

    rc = cf.CFStringGetCString(p, buf, max_sz, kCFStringEncodingUTF8)
    if not rc:
        return None

    return buf.value.decode('utf-8')
