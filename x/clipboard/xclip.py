import ctypes as ct
import ctypes.util
import sys


##


if getattr(sys, 'platform') != 'darwin':
    raise OSError(sys.platform)


##
# x11

x11 = ct.CDLL(ct.util.find_library('X11'))

#

Display = ct.c_void_p
Window = ct.c_ulong
Atom = ct.c_ulong
Time = ct.c_ulong
Bool = ct.c_int
Status = ct.c_int

#

class XEvent(ct.Structure):
    _fields_ = [
        ('type', ct.c_int),
        ('xselection', ct.c_ulong * 24),  # noqa
    ]

#

x11.XOpenDisplay.argtypes = [ct.c_char_p]
x11.XOpenDisplay.restype = Display

x11.XInternAtom.argtypes = [Display, ct.c_char_p, Bool]
x11.XInternAtom.restype = Atom

x11.XCreateSimpleWindow.argtypes = [
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
x11.XCreateSimpleWindow.restype = Window

x11.XConvertSelection.argtypes = [Display, Atom, Atom, Atom, Window, Time]
x11.XConvertSelection.restype = None

x11.XNextEvent.argtypes = [Display, ct.POINTER(XEvent)]
x11.XNextEvent.restype = None

x11.XGetWindowProperty.argtypes = [
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
x11.XGetWindowProperty.restype = Status

x11.XFree.argtypes = [ct.c_void_p]
x11.XFree.restype = None

x11.XFlush.argtypes = [Display]
x11.XFlush.restype = None

x11.XDestroyWindow.argtypes = [Display, Window]
x11.XDestroyWindow.restype = None

x11.XCloseDisplay.argtypes = [Display]
x11.XCloseDisplay.restype = None

x11.XDefaultScreen.argtypes = [Display]
x11.XDefaultScreen.restype = ct.c_int

x11.XRootWindow.argtypes = [Display, ct.c_int]
x11.XRootWindow.restype = Window


##


def atom_to_string(display, atom):
    x11.XGetAtomName.argtypes = [Display, Atom]
    x11.XGetAtomName.restype = ct.c_char_p
    return x11.XGetAtomName(display, atom).decode('utf-8')


##


def get_clipboard_text(display, window):
    clipboard = x11.XInternAtom(display, b'CLIPBOARD', False)
    utf8_string = x11.XInternAtom(display, b'UTF8_STRING', False)
    target_property = x11.XInternAtom(display, b'XSEL_DATA', False)

    x11.XConvertSelection(
        display,
        clipboard,
        utf8_string,
        target_property,
        window,
        0,
    )
    x11.XFlush(display)

    event = XEvent()
    x11.XNextEvent(display, ct.byref(event))

    if event.type != 31:  # SelectionNotify event type
        print('Failed to receive SelectionNotify event')
        return

    if event.xselection[4] == 0:  # None
        print('No clipboard data available')
        return

    actual_type = Atom()
    actual_format = ct.c_int()
    nitems = ct.c_ulong()
    bytes_after = ct.c_ulong()
    data = ct.c_void_p()

    status = x11.XGetWindowProperty(
        display,
        window,
        target_property,
        0,
        (~0),
        False,
        0,
        ct.byref(actual_type),
        ct.byref(actual_format),
        ct.byref(nitems),
        ct.byref(bytes_after),
        ct.byref(data),
    )

    if status != 0 or not data:
        print('Failed to get clipboard data')
        return

    clipboard_text = ct.cast(data, ct.c_char_p).value
    print('Clipboard text:', clipboard_text.decode('utf-8') if clipboard_text else '')

    x11.XFree(data)


def get_clipboard_image(display, window):
    clipboard = x11.XInternAtom(display, b'CLIPBOARD', False)
    target_property = x11.XInternAtom(display, b'XSEL_DATA', False)
    targets_atom = x11.XInternAtom(display, b'TARGETS', False)

    x11.XConvertSelection(
        display,
        clipboard,
        targets_atom,
        target_property,
        window,
        0,
    )
    x11.XFlush(display)

    event = XEvent()
    x11.XNextEvent(display, ct.byref(event))

    if event.type != 31 or event.xselection[4] == 0:
        print('Failed to receive SelectionNotify event for image')
        return

    actual_type = Atom()
    actual_format = ct.c_int()
    nitems = ct.c_ulong()
    bytes_after = ct.c_ulong()
    data = ct.c_void_p()

    status = x11.XGetWindowProperty(
        display,
        window,
        target_property,
        0,
        ~0,
        False,
        4,
        ct.byref(actual_type),
        ct.byref(actual_format),
        ct.byref(nitems),
        ct.byref(bytes_after),
        ct.byref(data),
    )

    if status != 0 or not data:
        print('Failed to get available targets')
        return

    png_atom = x11.XInternAtom(display, b'image/png', False)
    atoms = ct.cast(data, ct.POINTER(Atom))
    for i in range(nitems.value):
        if atoms[i] == png_atom:
            x11.XConvertSelection(
                display,
                clipboard,
                png_atom,
                target_property,
                window,
                0,
            )
            x11.XFlush(display)
            x11.XNextEvent(display, ct.byref(event))

            if event.type != 31 or event.xselection[4] == 0:
                print('Failed to receive SelectionNotify event for PNG image')
                x11.XFree(data)
                return

            status = x11.XGetWindowProperty(
                display,
                window,
                target_property,
                0,
                ~0,
                False,
                0,
                ct.byref(actual_type),
                ct.byref(actual_format),
                ct.byref(nitems),
                ct.byref(bytes_after),
                ct.byref(data),
            )

            if status == 0 and data:
                with open('clipboard_image.png', 'wb') as file:
                    file.write(ct.string_at(data.value, nitems.value))
                    print('Clipboard image saved to clipboard_image.png')

            x11.XFree(data)
            return

    print('No image data available on clipboard')
    x11.XFree(data)


##


def main() -> None:
    display = x11.XOpenDisplay(None)
    if not display:
        print('Failed to open X display')
        return

    screen = x11.XDefaultScreen(display)
    window = x11.XCreateSimpleWindow(
        display,
        x11.XRootWindow(display, screen),
        0,
        0,
        1,
        1,
        0,
        0,
        0,
    )

    get_clipboard_text(display, window)
    get_clipboard_image(display, window)

    x11.XDestroyWindow(display, window)
    x11.XCloseDisplay(display)


if __name__ == '__main__':
    main()
