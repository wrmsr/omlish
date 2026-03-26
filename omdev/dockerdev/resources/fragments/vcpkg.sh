set -ex ;

git clone 'https://github.com/microsoft/vcpkg' ~/.vcpkg_root ;
(cd ~/.vcpkg_root && ./bootstrap-vcpkg.sh) ;

echo '\n
export VCPKG_ROOT="$HOME/.vcpkg_root"\n
' >> ~/.bashrc ;
