//usr/bin/true; exec om cc run "$0" "$@"
/* @omlish-cdeps [
    {
        "git": {
            "url": "https://github.com/boost-ext/ut",
            "rev": "f83e15c7f1edb49b4ec20f866eec06940d18a47d",
            "subtrees": [
                "include"
            ]
        },
        "include": [
            "include"
        ]
    }
] */
#include <boost/ut.hpp> // import boost.ut;

constexpr auto sum(auto... values) { return (values + ...); }

int main() {
  using namespace boost::ut;

  "sum"_test = [] {
    expect(sum(0) == 0_i);
    expect(sum(1, 2) == 3_i);
    expect(sum(1, 2) > 0_i and 41_i == sum(40, 2));
  };
}
