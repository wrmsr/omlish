//usr/bin/true; exec om cc run "$0" "$@"
/* @omlish-cdeps [
    {
        "git": {
            "url": "https://github.com/yhirose/cpp-httplib",
            "rev": "a7bc00e3307fecdb4d67545e93be7b88cfb1e186",
            "subtrees": [
                "httplib.h"
            ]
        },
        "include": [
            "."
        ],
        "cmake": {
            "fetch_content": {
                "git": {
                    "repository": "https://github.com/yhirose/cpp-httplib.git",
                    "tag": "a7bc00e3307fecdb4d67545e93be7b88cfb1e186"
                }
            }
        }
    }
] */
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
