//usr/bin/true; exec om cc run "$0" "$@"
// @omlish-llm-author "gemini-2.5-pro"
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// VLAs are a C99 feature, made optional in C11 (status maintained in C17).
// They are not standard C++. Compilers may provide them as an extension in C++.
// We can check if the implementation claims to support VLAs.
// __STDC_NO_VLA__ is defined to 1 if VLAs are *not* supported.
// If it's not defined, or defined as 0, they are expected to be supported.

void process_vla(size_t n, int array[n]) {
    printf("  Inside process_vla with VLA of size %zu:\n", n);
    for (size_t i = 0; i < n; ++i) {
        array[i] = (int)(i * 10); // Initialize with some values
        printf("  array[%zu] = %d\n", i, array[i]);
    }
}

int main() {
    printf("--- C Program Demonstrating Features in C17 Standard ---\n\n");

    printf("1. Variable Length Arrays (VLAs) (C99, optional in C11/C17, not in C++):\n");
#if defined(__STDC_NO_VLA__) && __STDC_NO_VLA__ == 1
    printf("   Compiler indicates VLAs are not supported (__STDC_NO_VLA__ is defined as 1).\n");
    printf("   Cannot run VLA specific parts of this demo.\n");
#else
    printf("   Compiler does not define __STDC_NO_VLA__ as 1; attempting to use VLAs.\n");

    size_t size1 = 5;
    int vla1[size1]; // Declare a VLA

    printf("   Declared VLA 'vla1' with compile-time known size %zu\n", size1);
    for (size_t i = 0; i < size1; ++i) {
        vla1[i] = (int)(i + 1);
    }
    printf("   VLA 'vla1' elements: ");
    for (size_t i = 0; i < size1; ++i) {
        printf("%d ", vla1[i]);
    }
    printf("\n");

    const int min_size = 10;
    const int max_size = 20;
    srand(time(NULL));
    size_t size2 = (size_t) (rand() % (max_size + 1 - min_size) + min_size);

    int vla2[size2]; // VLA size determined at runtime
    printf("   Dynamically sized VLA 'vla2' declared with size %zu.\n", size2);
    process_vla(size2, vla2);
#endif
    printf("\n");

    printf("2. _Static_assert (C11 keyword, part of C17 standard):\n");
    // _Static_assert allows compile-time checks. C++ also has static_assert.
    // Its presence is part of modern C (C11/C17).
    _Static_assert(sizeof(int) >= 2, "Integer size must be at least 2 bytes for this program.");
    _Static_assert(sizeof(char) == 1, "Character size must be 1 byte.");
    printf("   _Static_assert checks passed at compile time.\n\n");


    printf("3. __has_include (C17 preprocessor feature, also in C++17):\n");
    // This directive checks for the availability of a header file.
#if __has_include(<stdlib.h>)
    printf("   __has_include(<stdlib.h>) is true. (Standard header)\n");
#else
    printf("   __has_include(<stdlib.h>) is false. (Unexpected for stdlib.h)\n");
#endif

#if __has_include(<non_existent_header_c17.h>)
    printf("   __has_include(<non_existent_header_c17.h>) is true. (Unexpected)\n");
#else
    printf("   __has_include(<non_existent_header_c17.h>) is false. (Expected for non-existent header)\n");
#endif
    printf("\n");

    printf("Note on C17: The C17 standard is primarily C11 with defect resolutions and clarifications.\n");
    printf("It didn't introduce many entirely new language features exclusive to C17. Features like\n");
    printf("VLAs (from C99, optional status confirmed in C11/C17) and _Static_assert (from C11)\n");
    printf("are part of the C17 standard and highlight aspects of C, some of which differ from C++.\n");

    return 0;
}
