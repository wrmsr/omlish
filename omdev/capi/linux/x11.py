import ctypes as ct
import ctypes.util
import typing as ta


##


x11 = ct.CDLL(ct.util.find_library('X11'))


Atom: ta.TypeAlias = ct.c_ulong
Bool: ta.TypeAlias = ct.c_int
Display: ta.TypeAlias = ct.c_void_p
Status: ta.TypeAlias = ct.c_int
Time: ta.TypeAlias = ct.c_ulong
Window: ta.TypeAlias = ct.c_ulong


class XEvent(ct.Structure):
    _fields_ = (
        ('type', ct.c_int),
        ('xselection', ct.c_ulong * 24),  # noqa
    )


XCloseDisplay = x11.XCloseDisplay
XCloseDisplay.argtypes = [Display]
XCloseDisplay.restype = None

XConvertSelection = x11.XConvertSelection
XConvertSelection.argtypes = [Display, Atom, Atom, Atom, Window, Time]
XConvertSelection.restype = None

XCreateSimpleWindow = x11.XCreateSimpleWindow
XCreateSimpleWindow.argtypes = [
    Display,
    Window,
    ct.c_int,
    ct.c_int,
    ct.c_uint,
    ct.c_uint,
    ct.c_uint,
    ct.c_ulong,
    ct.c_ulong,
]
XCreateSimpleWindow.restype = Window

XDefaultScreen = x11.XDefaultScreen
XDefaultScreen.argtypes = [Display]
XDefaultScreen.restype = ct.c_int

XDestroyWindow = x11.XDestroyWindow
XDestroyWindow.argtypes = [Display, Window]
XDestroyWindow.restype = None

XFlush = x11.XFlush
XFlush.argtypes = [Display]
XFlush.restype = None

XFree = x11.XFree
XFree.argtypes = [ct.c_void_p]
XFree.restype = None

XGetWindowProperty = x11.XGetWindowProperty
XGetWindowProperty.argtypes = [
    Display,
    Window,
    Atom,
    ct.c_long,
    ct.c_long,
    Bool,
    Atom,
    ct.POINTER(Atom),
    ct.POINTER(ct.c_int),
    ct.POINTER(ct.c_ulong),
    ct.POINTER(ct.c_ulong),
    ct.POINTER(ct.c_void_p),
]
XGetWindowProperty.restype = Status

XInternAtom = x11.XInternAtom
XInternAtom.argtypes = [Display, ct.c_char_p, Bool]
XInternAtom.restype = Atom

XNextEvent = x11.XNextEvent
XNextEvent.argtypes = [Display, ct.POINTER(XEvent)]
XNextEvent.restype = None

XOpenDisplay = x11.XOpenDisplay
XOpenDisplay.argtypes = [ct.c_char_p]
XOpenDisplay.restype = Display

XRootWindow = x11.XRootWindow
XRootWindow.argtypes = [Display, ct.c_int]
XRootWindow.restype = Window

XGetAtomName = x11.XGetAtomName
XGetAtomName.argtypes = [Display, Atom]
XGetAtomName.restype = ct.c_char_p


##


def atom_to_string(display, atom) -> str:
    return XGetAtomName(display, atom).decode('utf-8')
