#include "debug.h"
#include "model.h"

template <typename T>
bool BinaryDumper::save(const std::string& filename, const T* data, size_t count) {
  std::ofstream file(filename, std::ios::binary);
  if (!file) return false;
  
  // Write count first
  file.write(reinterpret_cast<const char*>(&count), sizeof(count));
  // Write T data
  file.write(reinterpret_cast<const char*>(data), count * sizeof(T));
  
  return file.good();
}

template bool BinaryDumper::save<float>(const std::string&, const float*, size_t);
template bool BinaryDumper::save<f16_t>(const std::string&, const f16_t*, size_t);

template <typename T>
std::vector<T> BinaryDumper::load(const std::string& filename) {
  std::ifstream file(filename, std::ios::binary);
  if (!file) return {};
  
  // Read count
  size_t count;
  file.read(reinterpret_cast<char*>(&count), sizeof(count));
  
  // Read T data
  std::vector<T> data(count);
  file.read(reinterpret_cast<char*>(data.data()), count * sizeof(T));
  
  if (!file.good()) return {};
  return data;
}

template std::vector<float> BinaryDumper::load(const std::string&);
template std::vector<f16_t> BinaryDumper::load(const std::string&);