set -ex ;

groupadd --gid ${NEWGID} ${NEWUSER} ;
useradd --uid ${NEWUID} --gid ${NEWGID} -m -s /bin/bash -d /${NEWUSER} ${NEWUSER} ;
echo "${NEWUSER} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${NEWUSER} ;
chmod 0440 /etc/sudoers.d/${NEWUSER} ;
