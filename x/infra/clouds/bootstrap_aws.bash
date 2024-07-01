sudo yum update -y
sudo yum install -y yum-utils
sudo yum groupinstall -y 'Development tools'

sudo yum install -y \
    bzip2-devel \
    kernel-devel \
    libffi-devel \
    libuuid-devel \
    ncurses-devel \
    openssl-devel \
    readline-devel \
    sqlite-devel \
    xz-devel \
    zlib-devel \

sudo yum install -y \
    libdb-devel \
