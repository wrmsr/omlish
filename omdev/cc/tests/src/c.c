//usr/bin/true; exec om cc run "$0" "$@"
// @omlish-llm-author "gemini-2.5-pro"
#include <stdio.h>

struct Point {
    int x;
    int y;
    int z;
};

int main() {
    // Designated initializers for a struct
    // Initializes members by name, in any order (though often written in order)
    struct Point p1 = { .y = 20, .x = 10, .z = 30 };

    // Designated initializers for an array
    // Initializes specific elements by index
    int numbers[5] = { [2] = 200, [0] = 100, [4] = 400 };

    printf("Point p1: x = %d, y = %d, z = %d\n", p1.x, p1.y, p1.z);

    printf("Numbers: ");
    for (int i = 0; i < 5; i++) {
        printf("%d ", numbers[i]); // Uninitialized elements are zero-initialized
    }
    printf("\n");

    return 0;
}
