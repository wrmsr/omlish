set -ex ;

sudo add-apt-repository ppa:mozillateam/ppa ;

echo "
Package: *\n
Pin: release o=LP-PPA-mozillateam\n
Pin-Priority: 1001\n
\n
Package: firefox\n
Pin: version 1:1snap1-0ubuntu2\n
Pin-Priority: -1\n
" | sudo tee /etc/apt/preferences.d/mozilla-firefox ;

sudo apt-get update ;
sudo apt-get install -y firefox ;

echo 'Unattended-Upgrade::Allowed-Origins:: "LP-PPA-mozillateam:${distro_codename}";' |
  sudo tee /etc/apt/apt.conf.d/51unattended-upgrades-firefox ;
