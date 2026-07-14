//usr/bin/true; exec om cc run "$0" "$@"
// @om-cdeps ["httplib"]
#include <iostream>

// #define CPPHTTPLIB_OPENSSL_SUPPORT
#include "httplib.h"


int main() {
    httplib::Client cli("http://www.google.com");

    auto res = cli.Get("/");
    std::cout << res->status << std::endl;
    std::cout << res->body << std::endl;

    return 0;
}
