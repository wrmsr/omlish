set -ex ;

curl -fsSL "https://ziglang.org/download/${ZIG_VERSION}/zig-$(uname -m)-linux-${ZIG_VERSION}.tar.xz" | tar -xJ -C "$HOME" ;
mv "$HOME/zig-$(uname -m)-linux-${ZIG_VERSION}" "$HOME/.zig" ;

echo '\n
export PATH="$HOME/.zig:$PATH"\n
' >> ~/.bashrc ;
