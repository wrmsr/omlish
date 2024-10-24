#include <wayland-client.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

struct wl_display* display;
struct wl_registry* registry;
struct wl_data_device_manager* data_device_manager;
struct wl_data_device* data_device;
struct wl_seat* seat;
int clipboard_fd = -1;
char clipboard_data[4096];  // Buffer for clipboard data

// Registry listener
static void registry_handler(void* data, struct wl_registry* registry, uint32_t id, const char* interface, uint32_t version) {
    if (strcmp(interface, "wl_seat") == 0) {
        seat = wl_registry_bind(registry, id, &wl_seat_interface, 1);
    } else if (strcmp(interface, "wl_data_device_manager") == 0) {
        data_device_manager = wl_registry_bind(registry, id, &wl_data_device_manager_interface, 1);
    }
}

static void registry_remover(void* data, struct wl_registry* registry, uint32_t id) {
    // Do nothing
}

static const struct wl_registry_listener registry_listener = {
    .global = registry_handler,
    .global_remove = registry_remover,
};

// Data device listener for clipboard data
static void data_device_data_offer(void* data, struct wl_data_device* data_device, struct wl_data_offer* offer) {
    // Accept the data offer
    wl_data_offer_accept(offer, 0, "text/plain;charset=utf-8");
    clipboard_fd = open("/tmp/clipboard.txt", O_WRONLY | O_CREAT | O_TRUNC, 0666);
    wl_data_offer_receive(offer, "text/plain;charset=utf-8", clipboard_fd);
}

static void data_device_selection(void* data, struct wl_data_device* data_device, struct wl_data_offer* offer) {
    if (offer) {
        data_device_data_offer(data, data_device, offer);
    } else {
        fprintf(stderr, "No clipboard data available\n");
    }
}

static const struct wl_data_device_listener data_device_listener = {
    .data_offer = data_device_data_offer,
    .selection = data_device_selection,
};

void clipboard_read(void) {
    ssize_t bytes_read = read(clipboard_fd, clipboard_data, sizeof(clipboard_data) - 1);
    if (bytes_read > 0) {
        clipboard_data[bytes_read] = '\0';
        printf("Clipboard text: %s\n", clipboard_data);
    }
    close(clipboard_fd);
}

int main() {
    // Connect to the Wayland display
    display = wl_display_connect(NULL);
    if (!display) {
        fprintf(stderr, "Failed to connect to the Wayland display\n");
        return EXIT_FAILURE;
    }

    // Get the registry and bind the required interfaces
    registry = wl_display_get_registry(display);
    wl_registry_add_listener(registry, &registry_listener, NULL);
    wl_display_roundtrip(display);

    // Check if the required interfaces are available
    if (!seat || !data_device_manager) {
        fprintf(stderr, "Required Wayland interfaces not available\n");
        return EXIT_FAILURE;
    }

    // Create a data device for the clipboard
    data_device = wl_data_device_manager_get_data_device(data_device_manager, seat);
    wl_data_device_add_listener(data_device, &data_device_listener, NULL);

    // Enter the main Wayland event loop
    wl_display_roundtrip(display);
    clipboard_read();

    // Clean up
    wl_data_device_destroy(data_device);
    wl_seat_destroy(seat);
    wl_data_device_manager_destroy(data_device_manager);
    wl_registry_destroy(registry);
    wl_display_disconnect(display);
    return EXIT_SUCCESS;
}
