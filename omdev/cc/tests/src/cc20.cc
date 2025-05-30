//usr/bin/true; exec om cc run "$0" "$@"
// @omlish-llm-author "gemini-2.5-pro"
#include <iostream>
#include <vector>
#include <algorithm>
#include <ranges> // For ranges library
#include <concepts> // For concepts
#include <string>   // For std::string

// 1. C++20 CONCEPTS
// Define a concept 'Numeric' that checks if a type is arithmetic (integer or floating-point)
template <typename T>
concept Numeric = std::is_arithmetic_v<T>;

// A function constrained by the 'Numeric' concept
template <Numeric T>
T add(T a, T b) {
    return a + b;
}

// Define a concept 'HasOutputStreamOperator' to check if a type can be printed with <<
template <typename T>
concept HasOutputStreamOperator = requires(std::ostream& os, const T& t) {
    { os << t } -> std::same_as<std::ostream&>;
};

// A function template constrained by this concept using 'auto'
void print_item(const HasOutputStreamOperator auto& item) {
    std::cout << item;
}

int main() {
    std::cout << "## C++20 Concepts ##\n";
    std::cout << "add(5, 3): " << add(5, 3) << std::endl;          // Works, int is Numeric
    std::cout << "add(2.5, 3.7): " << add(2.5, 3.7) << std::endl;  // Works, double is Numeric
    // The following line would cause a compile-time error because std::string is not Numeric:
    // std::cout << add(std::string("hello"), std::string(" world")) << std::endl;

    std::cout << "Printing items using constrained function: " << std::endl;
    std::cout << "  Item (int): ";
    print_item(101);
    std::cout << std::endl;

    std::cout << "  Item (double): ";
    print_item(3.14159);
    std::cout << std::endl;

    std::cout << "  Item (string): ";
    print_item(std::string("Hello C++20!"));
    std::cout << std::endl;

    struct NonPrintable {};
    // The following line would cause a compile-time error because NonPrintable doesn't satisfy HasOutputStreamOperator:
    // print_item(NonPrintable{});


    // std::cout << "\n## C++20 Ranges ##\n";
    // std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};

    // // 2. Using ranges to filter, transform, and take elements
    // //    - 'std::views::filter' takes even numbers
    // //    - 'std::views::transform' squares each of those elements
    // //    - 'std::views::take' takes the first 3 such results
    // auto results = numbers
    //              | std::views::filter([](int n){ return n % 2 == 0; }) // Keep even numbers
    //              | std::views::transform([](int n){ return n * n; })   // Square them
    //              | std::views::take(3);                                // Take the first 3

    // std::cout << "First 3 squares of even numbers: ";
    // for (int num : results) { // The operations are lazily evaluated here
    //     std::cout << num << " ";
    // }
    // std::cout << std::endl;

    // // Example: Find all numbers greater than 5 and drop the first one found
    // auto greater_than_5_drop_1 = numbers
    //                            | std::views::filter([](int n){ return n > 5; })
    //                            | std::views::drop(1);

    // std::cout << "Numbers greater than 5, dropping the first one: ";
    // for (int num : greater_than_5_drop_1) {
    //     std::cout << num << " ";
    // }
    // std::cout << std::endl;

    return 0;
}