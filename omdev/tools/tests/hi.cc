//usr/bin/true; exec om cc run "$0" "$@"
#include <iostream>

int main(int argc, const char *argv[]) {
   std::cout << "Arguments (" << argc << "):" << std::endl;

  for (int i = 0; i < argc; ++i) {
    std::cout << "argv[" << i << "]: " << argv[i] << std::endl;
  }

  return 0;
}
