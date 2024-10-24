#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Helper function to convert atom to string for debugging
const char* atom_to_string(Display* display, Atom atom) {
    return XGetAtomName(display, atom);
}

// Function to get clipboard contents as text
void get_clipboard_text(Display* display, Window window) {
    Atom clipboard = XInternAtom(display, "CLIPBOARD", False);
    Atom utf8_string = XInternAtom(display, "UTF8_STRING", False);
    Atom target_property = XInternAtom(display, "XSEL_DATA", False);

    // Request the contents of the clipboard
    XConvertSelection(display, clipboard, utf8_string, target_property, window, CurrentTime);
    XFlush(display);

    // Wait for SelectionNotify event
    XEvent event;
    XNextEvent(display, &event);
    if (event.type != SelectionNotify) {
        fprintf(stderr, "Failed to receive SelectionNotify event\n");
        return;
    }

    if (event.xselection.property == None) {
        fprintf(stderr, "No clipboard data available\n");
        return;
    }

    // Get the data from the property
    Atom actual_type;
    int actual_format;
    unsigned long nitems, bytes_after;
    unsigned char* data = NULL;
    int status = XGetWindowProperty(display, window, target_property, 0, (~0L), False,
                                    AnyPropertyType, &actual_type, &actual_format,
                                    &nitems, &bytes_after, &data);

    if (status != Success || !data) {
        fprintf(stderr, "Failed to get clipboard data\n");
        return;
    }

    // Print the text data
    printf("Clipboard text: %s\n", data);

    // Free the data
    XFree(data);
}

// Function to get clipboard contents as an image (in PNG format)
void get_clipboard_image(Display* display, Window window) {
    Atom clipboard = XInternAtom(display, "CLIPBOARD", False);
    Atom target_property = XInternAtom(display, "XSEL_DATA", False);

    // The TARGETS atom is used to list available formats, including image formats
    Atom targets_atom = XInternAtom(display, "TARGETS", False);

    // Request the list of available formats
    XConvertSelection(display, clipboard, targets_atom, target_property, window, CurrentTime);
    XFlush(display);

    // Wait for SelectionNotify event
    XEvent event;
    XNextEvent(display, &event);
    if (event.type != SelectionNotify || event.xselection.property == None) {
        fprintf(stderr, "Failed to receive SelectionNotify event for image\n");
        return;
    }

    // Get the available targets
    Atom actual_type;
    int actual_format;
    unsigned long nitems, bytes_after;
    unsigned char* data = NULL;
    int status = XGetWindowProperty(display, window, target_property, 0, (~0L), False,
                                    XA_ATOM, &actual_type, &actual_format,
                                    &nitems, &bytes_after, &data);

    if (status != Success || !data) {
        fprintf(stderr, "Failed to get available targets\n");
        return;
    }

    // Check if the clipboard contains image data (e.g., image/png)
    Atom png_atom = XInternAtom(display, "image/png", False);
    for (unsigned long i = 0; i < nitems; i++) {
        Atom target = ((Atom*)data)[i];
        if (target == png_atom) {
            // Request the image data in PNG format
            XConvertSelection(display, clipboard, png_atom, target_property, window, CurrentTime);
            XFlush(display);

            // Wait for SelectionNotify event
            XNextEvent(display, &event);
            if (event.type != SelectionNotify || event.xselection.property == None) {
                fprintf(stderr, "Failed to receive SelectionNotify event for PNG image\n");
                XFree(data);
                return;
            }

            // Get the image data
            status = XGetWindowProperty(display, window, target_property, 0, (~0L), False,
                                        AnyPropertyType, &actual_type, &actual_format,
                                        &nitems, &bytes_after, &data);

            if (status != Success || !data) {
                fprintf(stderr, "Failed to get PNG image data\n");
                XFree(data);
                return;
            }

            // Save the image data to a file
            FILE* file = fopen("clipboard_image.png", "wb");
            if (file) {
                fwrite(data, 1, nitems, file);
                fclose(file);
                printf("Clipboard image saved to clipboard_image.png\n");
            } else {
                fprintf(stderr, "Failed to open file for writing\n");
            }
            XFree(data);
            return;
        }
    }

    fprintf(stderr, "No image data available on clipboard\n");
    XFree(data);
}

int main() {
    // Open the X display
    Display* display = XOpenDisplay(NULL);
    if (!display) {
        fprintf(stderr, "Failed to open X display\n");
        return EXIT_FAILURE;
    }

    // Create a window to receive events
    int screen = DefaultScreen(display);
    Window window = XCreateSimpleWindow(display, RootWindow(display, screen), 0, 0, 1, 1, 0, 0, 0);

    // Get clipboard text
    get_clipboard_text(display, window);

    // Get clipboard image
    get_clipboard_image(display, window);

    // Close the display
    XDestroyWindow(display, window);
    XCloseDisplay(display);
    return EXIT_SUCCESS;
}
