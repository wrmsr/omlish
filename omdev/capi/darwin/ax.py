import ctypes as ct


##


ax = ct.CDLL('/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/HIServices.framework/Versions/A/HIServices')  # noqa


# AXUIElementCreateApplication(pid_t pid)
AXUIElementCreateApplication = ax.AXUIElementCreateApplication
AXUIElementCreateApplication.argtypes = [ct.c_int]
AXUIElementCreateApplication.restype = ct.c_void_p

# AXUIElementSetAttributeValue(AXUIElementRef element, CFStringRef attr, CFTypeRef value)
AXUIElementSetAttributeValue = ax.AXUIElementSetAttributeValue
AXUIElementSetAttributeValue.argtypes = [ct.c_void_p, ct.c_void_p, ct.c_void_p]
AXUIElementSetAttributeValue.restype = ct.c_int

# AXUIElementCopyAttributeValue(AXUIElementRef element, CFStringRef attr, CFTypeRef *value)
AXUIElementCopyAttributeValue = ax.AXUIElementCopyAttributeValue
AXUIElementCopyAttributeValue.argtypes = [ct.c_void_p, ct.c_void_p, ct.POINTER(ct.c_void_p)]
AXUIElementCopyAttributeValue.restype = ct.c_int

# AXValueCreate functions
AXValueCreate = ax.AXValueCreate
AXValueCreate.argtypes = [ct.c_int, ct.c_void_p]
AXValueCreate.restype = ct.c_void_p

# AXValueGetValue - extract data from AXValue objects
AXValueGetValue = ax.AXValueGetValue
AXValueGetValue.argtypes = [ct.c_void_p, ct.c_int, ct.c_void_p]
AXValueGetValue.restype = ct.c_bool

# AX value types
kAXValueCGPointType = 1  # noqa
kAXValueCGSizeType = 2  # noqa

# Accessibility permissions checking
AXIsProcessTrusted = ax.AXIsProcessTrusted
AXIsProcessTrusted.argtypes = []
AXIsProcessTrusted.restype = ct.c_bool

AXIsProcessTrustedWithOptions = ax.AXIsProcessTrustedWithOptions
AXIsProcessTrustedWithOptions.argtypes = [ct.c_void_p]
AXIsProcessTrustedWithOptions.restype = ct.c_bool

AXUIElementCopyAttributeNames = ax.AXUIElementCopyAttributeNames
AXUIElementCopyAttributeNames.argtypes = [ct.c_void_p, ct.POINTER(ct.c_void_p)]
AXUIElementCopyAttributeNames.restype = ct.c_int

AXUIElementGetAttributeValueCount = ax.AXUIElementGetAttributeValueCount
AXUIElementGetAttributeValueCount.argtypes = [ct.c_void_p, ct.c_void_p, ct.POINTER(ct.c_long)]
AXUIElementGetAttributeValueCount.restype = ct.c_int
