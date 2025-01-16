//usr/bin/true; exec om cc run "$0" "$@"
/* @omlish-cdeps [
    {
        "git": {
            "url": "https://github.com/libcpr/cpr",
            "rev": "dec9422db3af470641f8b0d90e4b451c4daebf64"
        },
        "sources": [
            ["cpr/", "*.cpp"]
        ],
        "include": [
            "include"
        ],
        "cmake": {
            "fetch_content": {
                "git": {
                    "repository": "https://github.com/libcpr/cpr.git",
                    "tag": "dec9422db3af470641f8b0d90e4b451c4daebf64"
                }
            }
        }
    }
] */
#include <iostream>

#include <cpr/cpr.h>


int main() {
    cpr::Response r = cpr::Get(
        cpr::Url{"https://api.github.com/repos/whoshuu/cpr/contributors"},
        cpr::Authentication{"user", "pass", cpr::AuthMode::BASIC},
        cpr::Parameters{{"anon", "true"}, {"key", "value"}}
    );
    std::cout << r.status_code << std::endl;             // 200
    std::cout << r.header["content-type"] << std::endl;  // application/json; charset=utf-8
    std::cout << r.text << std::endl;                    // JSON text string
    return 0;
}
