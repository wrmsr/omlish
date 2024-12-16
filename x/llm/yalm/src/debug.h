#include <fstream>
#include <vector>
#include <cstdint>
#include <iostream>

struct BinaryDumper {
  // Save T array to binary file
  template <typename T>
  static bool save(const std::string& filename, const T* data, size_t count);
  
  // Load T array from binary file
  template <typename T>
  static std::vector<T> load(const std::string& filename);
};