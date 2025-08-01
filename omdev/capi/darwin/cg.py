import ctypes as ct
import ctypes.util


##


cg = ct.CDLL(ct.util.find_library('CoreGraphics'))


# Define constants (from CGWindow.h)
kCGWindowListExcludeDesktopElements = 1 << 4  # 16  # noqa
kCGWindowListOptionOnScreenOnly = 1 << 0  # 1  # noqa
kCGNullWindowID = 0  # noqa

# Define Core Foundation string constants. These are defined as extern const CFStringRef in the headers.
kCGWindowNumber = ct.c_char_p(b"kCGWindowNumber")  # noqa
kCGWindowOwnerName = ct.c_char_p(b"kCGWindowOwnerName")  # noqa
kCGWindowName = ct.c_char_p(b"kCGWindowName")  # noqa
kCGWindowBounds = ct.c_char_p(b"kCGWindowBounds")  # noqa
kCGWindowOwnerPID = ct.c_char_p(b"kCGWindowOwnerPID")  # noqa

# CFArrayRef CGWindowListCopyWindowInfo(CGWindowListOption option, CGWindowID relativeToWindow)
CGWindowListCopyWindowInfo = cg.CGWindowListCopyWindowInfo
CGWindowListCopyWindowInfo.argtypes = [ct.c_uint32, ct.c_uint32]
CGWindowListCopyWindowInfo.restype = ct.c_void_p

# CGPreflightScreenCaptureAccess() - available on macOS 10.15+
CGPreflightScreenCaptureAccess = cg.CGPreflightScreenCaptureAccess
CGPreflightScreenCaptureAccess.argtypes = []
CGPreflightScreenCaptureAccess.restype = ct.c_bool

CGWindowListCreateImage = cg.CGWindowListCreateImage
CGWindowListCreateImage.argtypes = [ct.c_void_p, ct.c_uint32, ct.c_uint32, ct.c_uint32]
CGWindowListCreateImage.restype = ct.c_void_p

# CGMainDisplayID() - get the main display
CGMainDisplayID = cg.CGMainDisplayID
CGMainDisplayID.argtypes = []
CGMainDisplayID.restype = ct.c_uint32


# Define CGRect structure
class CGRect(ct.Structure):
    _fields_ = (
        ('origin_x', ct.c_double),
        ('origin_y', ct.c_double),
        ('size_width', ct.c_double),
        ('size_height', ct.c_double),
    )


# CGDisplayBounds(CGDirectDisplayID display) - get display bounds
CGDisplayBounds = cg.CGDisplayBounds
CGDisplayBounds.argtypes = [ct.c_uint32]
CGDisplayBounds.restype = CGRect

# Get process PID from window number - we'll use GetWindowProperty or similar
CGWindowListCopyWindowInfo = cg.CGWindowListCopyWindowInfo
CGWindowListCopyWindowInfo.argtypes = [ct.c_uint32, ct.c_uint32]
CGWindowListCopyWindowInfo.restype = ct.c_void_p


# Define CGPoint and CGSize structures for Accessibility API
class CGPoint(ct.Structure):
    _fields_ = (
        ('x', ct.c_double),
        ('y', ct.c_double),
    )


class CGSize(ct.Structure):
    _fields_ = (
        ('width', ct.c_double),
        ('height', ct.c_double),
    )


# CoreGraphics functions for mouse events
CGEventCreateMouseEvent = cg.CGEventCreateMouseEvent
CGEventCreateMouseEvent.argtypes = [ct.c_void_p, ct.c_uint32, CGPoint, ct.c_uint32]
CGEventCreateMouseEvent.restype = ct.c_void_p

CGEventPost = cg.CGEventPost
CGEventPost.argtypes = [ct.c_uint32, ct.c_void_p]
CGEventPost.restype = None

CGEventSetType = cg.CGEventSetType
CGEventSetType.argtypes = [ct.c_void_p, ct.c_uint32]
CGEventSetType.restype = None

# Mouse event types
kCGEventLeftMouseDown = 1  # noqa
kCGEventLeftMouseUp = 2  # noqa
kCGEventRightMouseDown = 3  # noqa
kCGEventRightMouseUp = 4  # noqa
kCGEventMouseMoved = 5  # noqa
kCGHIDEventTap = 0  # noqa

# Event tap locations
kCGSessionEventTap = 1  # noqa

# Mouse button constants
kCGMouseButtonLeft = 0  # noqa
kCGMouseButtonRight = 1  # noqa
