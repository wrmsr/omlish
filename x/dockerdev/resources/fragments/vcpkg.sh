set -ex ;

git clone 'https://github.com/microsoft/vcpkg' /root/.vcpkg_root ;
(cd /root/.vcpkg_root && ./bootstrap-vcpkg.sh) ;

echo '\n
export VCPKG_ROOT="$HOME/.vcpkg_root"\n
' >> ~/.bashrc ;
