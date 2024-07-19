#include <iostream>

struct foo {
    int x{};
    int y;
};

int main(int argc, const char * const * argv) {
    foo f{};
    std::cout << f.x << " " << f.y << std::endl;
    return 0;
}
