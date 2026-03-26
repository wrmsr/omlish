set -ex ;

rm -f /etc/apt/apt.conf.d/docker-clean ;
rm -f /etc/dpkg/dpkg.cfg.d/excludes ;

export DEBIAN_FRONTEND=noninteractive ;
apt-get update ;

apt-get install -y locales ;
locale-gen en_US.UTF-8 ;

apt-get upgrade -y ;
apt-get install -y apt-utils ;
