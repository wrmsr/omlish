import ctypes
import ctypes.util


# Load the X11 library
libX11 = ctypes.CDLL(ctypes.util.find_library('X11'))

# Define necessary types and constants
Display = ctypes.c_void_p
Window = ctypes.c_ulong
Atom = ctypes.c_ulong
Time = ctypes.c_ulong
Bool = ctypes.c_int
Status = ctypes.c_int


# Define structures
class XEvent(ctypes.Structure):
    _fields_ = [('type', ctypes.c_int), ('xselection', ctypes.c_ulong * 24)]


# Function prototypes
libX11.XOpenDisplay.argtypes = [ctypes.c_char_p]
libX11.XOpenDisplay.restype = Display

libX11.XInternAtom.argtypes = [Display, ctypes.c_char_p, Bool]
libX11.XInternAtom.restype = Atom

libX11.XCreateSimpleWindow.argtypes = [
    Display,
    Window,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_uint,
    ctypes.c_uint,
    ctypes.c_uint,
    ctypes.c_ulong,
    ctypes.c_ulong,
]
libX11.XCreateSimpleWindow.restype = Window

libX11.XConvertSelection.argtypes = [Display, Atom, Atom, Atom, Window, Time]
libX11.XConvertSelection.restype = None

libX11.XNextEvent.argtypes = [Display, ctypes.POINTER(XEvent)]
libX11.XNextEvent.restype = None

libX11.XGetWindowProperty.argtypes = [
    Display,
    Window,
    Atom,
    ctypes.c_long,
    ctypes.c_long,
    Bool,
    Atom,
    ctypes.POINTER(Atom),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_ulong),
    ctypes.POINTER(ctypes.c_ulong),
    ctypes.POINTER(ctypes.c_void_p),
]
libX11.XGetWindowProperty.restype = Status

libX11.XFree.argtypes = [ctypes.c_void_p]
libX11.XFree.restype = None

libX11.XFlush.argtypes = [Display]
libX11.XFlush.restype = None

libX11.XDestroyWindow.argtypes = [Display, Window]
libX11.XDestroyWindow.restype = None

libX11.XCloseDisplay.argtypes = [Display]
libX11.XCloseDisplay.restype = None

libX11.XDefaultScreen.argtypes = [Display]
libX11.XDefaultScreen.restype = ctypes.c_int

libX11.XRootWindow.argtypes = [Display, ctypes.c_int]
libX11.XRootWindow.restype = Window


# Helper function to convert atom to string
def atom_to_string(display, atom):
    libX11.XGetAtomName.argtypes = [Display, Atom]
    libX11.XGetAtomName.restype = ctypes.c_char_p
    return libX11.XGetAtomName(display, atom).decode('utf-8')


# Function to get clipboard contents as text
def get_clipboard_text(display, window):
    clipboard = libX11.XInternAtom(display, b'CLIPBOARD', False)
    utf8_string = libX11.XInternAtom(display, b'UTF8_STRING', False)
    target_property = libX11.XInternAtom(display, b'XSEL_DATA', False)

    # Request the clipboard contents
    libX11.XConvertSelection(
        display, clipboard, utf8_string, target_property, window, 0,
    )
    libX11.XFlush(display)

    # Wait for SelectionNotify event
    event = XEvent()
    libX11.XNextEvent(display, ctypes.byref(event))

    if event.type != 31:  # SelectionNotify event type
        print('Failed to receive SelectionNotify event')
        return

    if event.xselection[4] == 0:  # None
        print('No clipboard data available')
        return

    # Get the clipboard data
    actual_type = Atom()
    actual_format = ctypes.c_int()
    nitems = ctypes.c_ulong()
    bytes_after = ctypes.c_ulong()
    data = ctypes.c_void_p()

    status = libX11.XGetWindowProperty(
        display,
        window,
        target_property,
        0,
        (~0),
        False,
        0,
        ctypes.byref(actual_type),
        ctypes.byref(actual_format),
        ctypes.byref(nitems),
        ctypes.byref(bytes_after),
        ctypes.byref(data),
    )

    if status != 0 or not data:
        print('Failed to get clipboard data')
        return

    clipboard_text = ctypes.cast(data, ctypes.c_char_p).value
    print('Clipboard text:', clipboard_text.decode('utf-8') if clipboard_text else '')

    libX11.XFree(data)


# Function to get clipboard contents as an image (in PNG format)
def get_clipboard_image(display, window):
    clipboard = libX11.XInternAtom(display, b'CLIPBOARD', False)
    target_property = libX11.XInternAtom(display, b'XSEL_DATA', False)
    targets_atom = libX11.XInternAtom(display, b'TARGETS', False)

    # Request the list of available formats
    libX11.XConvertSelection(
        display, clipboard, targets_atom, target_property, window, 0,
    )
    libX11.XFlush(display)

    event = XEvent()
    libX11.XNextEvent(display, ctypes.byref(event))

    if event.type != 31 or event.xselection[4] == 0:
        print('Failed to receive SelectionNotify event for image')
        return

    actual_type = Atom()
    actual_format = ctypes.c_int()
    nitems = ctypes.c_ulong()
    bytes_after = ctypes.c_ulong()
    data = ctypes.c_void_p()

    status = libX11.XGetWindowProperty(
        display,
        window,
        target_property,
        0,
        (~0),
        False,
        4,
        ctypes.byref(actual_type),
        ctypes.byref(actual_format),
        ctypes.byref(nitems),
        ctypes.byref(bytes_after),
        ctypes.byref(data),
    )

    if status != 0 or not data:
        print('Failed to get available targets')
        return

    png_atom = libX11.XInternAtom(display, b'image/png', False)
    atoms = ctypes.cast(data, ctypes.POINTER(Atom))
    for i in range(nitems.value):
        if atoms[i] == png_atom:
            libX11.XConvertSelection(
                display, clipboard, png_atom, target_property, window, 0,
            )
            libX11.XFlush(display)
            libX11.XNextEvent(display, ctypes.byref(event))

            if event.type != 31 or event.xselection[4] == 0:
                print('Failed to receive SelectionNotify event for PNG image')
                libX11.XFree(data)
                return

            status = libX11.XGetWindowProperty(
                display,
                window,
                target_property,
                0,
                (~0),
                False,
                0,
                ctypes.byref(actual_type),
                ctypes.byref(actual_format),
                ctypes.byref(nitems),
                ctypes.byref(bytes_after),
                ctypes.byref(data),
            )

            if status == 0 and data:
                with open('clipboard_image.png', 'wb') as file:
                    file.write(ctypes.string_at(data.value, nitems.value))
                    print('Clipboard image saved to clipboard_image.png')
            libX11.XFree(data)
            return

    print('No image data available on clipboard')
    libX11.XFree(data)


def main():
    display = libX11.XOpenDisplay(None)
    if not display:
        print('Failed to open X display')
        return

    screen = libX11.XDefaultScreen(display)
    window = libX11.XCreateSimpleWindow(
        display, libX11.XRootWindow(display, screen), 0, 0, 1, 1, 0, 0, 0,
    )

    get_clipboard_text(display, window)
    get_clipboard_image(display, window)

    libX11.XDestroyWindow(display, window)
    libX11.XCloseDisplay(display)


if __name__ == '__main__':
    main()
