# ruff: noqa: RUF012
# flake8: noqa: E302 E305
import ctypes as ct

from ..capi.linux import x11


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

    event = x11.XEvent()
    x11.XNextEvent(display, ct.byref(event))

    if event.type != 31:  # SelectionNotify event type
        print('Failed to receive SelectionNotify event')
        return

    if event.xselection[4] == 0:  # None
        print('No clipboard data available')
        return

    actual_type = x11.Atom()
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
        0,
        ct.byref(actual_type),
        ct.byref(actual_format),
        ct.byref(nitems),
        ct.byref(bytes_after),
        ct.byref(data),
    )
    try:
        if status != 0 or not data:
            print('Failed to get clipboard data')
            return

        clipboard_text = ct.cast(data, ct.c_char_p).value
        print(f'Clipboard text: {clipboard_text.decode("utf-8") if clipboard_text else ""}')

    finally:
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

    event = x11.XEvent()
    x11.XNextEvent(display, ct.byref(event))

    if event.type != 31 or event.xselection[4] == 0:
        print('Failed to receive SelectionNotify event for image')
        return

    actual_type = x11.Atom()
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
    try:
        if status != 0 or not data:
            print('Failed to get available targets')
            return

        png_atom = x11.XInternAtom(display, b'image/png', False)
        atoms = ct.cast(data, ct.POINTER(x11.Atom))
        for i in range(nitems.value):
            if atoms[i] != png_atom:
                continue

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
                data_bytes = ct.string_at(data.value, nitems.value)  # type: ignore

                print(f'Clipboard image: {len(data_bytes)} bytes')

            return

        print('No image data available on clipboard')

    finally:
        if data:
            x11.XFree(data)


##


def main() -> None:
    display = x11.XOpenDisplay(None)
    try:
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
        try:
            get_clipboard_text(display, window)
            get_clipboard_image(display, window)

        finally:
            x11.XDestroyWindow(display, window)

    finally:
        if display:
            x11.XCloseDisplay(display)


if __name__ == '__main__':
    main()
