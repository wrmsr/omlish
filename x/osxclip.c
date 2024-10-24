#include <CoreFoundation/CoreFoundation.h>
#include <ApplicationServices/ApplicationServices.h>
#include <stdio.h>
#include <string.h>

void get_clipboard_data() {
    PasteboardRef pasteboard;
    OSStatus status = PasteboardCreate(kPasteboardClipboard, &pasteboard);

    if (status != noErr) {
        fprintf(stderr, "Failed to access the clipboard\n");
        return;
    }

    // Synchronize the pasteboard to get the latest data
    PasteboardSynchronize(pasteboard);

    // Get the number of items in the clipboard
    ItemCount itemCount;
    status = PasteboardGetItemCount(pasteboard, &itemCount);
    if (status != noErr || itemCount == 0) {
        fprintf(stderr, "No items on the clipboard\n");
        return;
    }

    // Iterate over each item in the clipboard
    for (ItemCount i = 1; i <= itemCount; i++) {
        PasteboardItemID itemID;
        status = PasteboardGetItemIdentifier(pasteboard, i, &itemID);
        if (status != noErr) continue;

        // Get available data types for the current item
        CFArrayRef dataTypes = NULL;
        status = PasteboardCopyItemFlavors(pasteboard, itemID, &dataTypes);
        if (status != noErr || !dataTypes) {
            fprintf(stderr, "Failed to get data types for item %ld\n", i);
            continue;
        }

        // Iterate through data types to find supported ones
        CFIndex typeCount = CFArrayGetCount(dataTypes);
        for (CFIndex j = 0; j < typeCount; j++) {
            CFStringRef dataType = (CFStringRef)CFArrayGetValueAtIndex(dataTypes, j);

            // Print data type for debugging
            char typeBuffer[256];
            if (CFStringGetCString(dataType, typeBuffer, sizeof(typeBuffer), kCFStringEncodingUTF8)) {
                printf("Data type: %s\n", typeBuffer);
            }

            // Retrieve data of this type
            CFDataRef data = NULL;
            status = PasteboardCopyItemFlavorData(pasteboard, itemID, dataType, &data);
            if (status == noErr && data) {
                // Handle the binary data (e.g., images, files, etc.)
                CFIndex dataSize = CFDataGetLength(data);
                const UInt8* dataPtr = CFDataGetBytePtr(data);

                // Save to a file for testing
                FILE* file = fopen("clipboard_output.bin", "wb");
                if (file) {
                    fwrite(dataPtr, 1, dataSize, file);
                    fclose(file);
                    printf("Data saved to clipboard_output.bin (size: %ld bytes)\n", dataSize);
                }

                CFRelease(data);
            }
        }

        CFRelease(dataTypes);
    }

    CFRelease(pasteboard);
}

int main() {
    get_clipboard_data();
    return 0;
}
