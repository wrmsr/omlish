groupadd --gid ${NEW_GID} ${NEW_USER} ;
useradd --uid ${NEW_UID} --gid ${NEW_GID} -m -s /bin/bash -d /${NEW_USER} ${NEW_USER} ;
echo "${NEW_USER} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${NEW_USER} ;
chmod 0440 /etc/sudoers.d/${NEW_USER} ;
