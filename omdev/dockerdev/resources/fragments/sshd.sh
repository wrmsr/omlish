set -ex ;

sed -i 's/^#*PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config ;
sed -i 's/^#X11UseLocalhost yes/X11UseLocalhost no/' /etc/ssh/sshd_config ;
sed -i 's/^# Ciphers and keying/Ciphers chacha20-poly1305@openssh.com/' /etc/ssh/sshd_config ;
sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd ;
mkdir /var/run/sshd ;
