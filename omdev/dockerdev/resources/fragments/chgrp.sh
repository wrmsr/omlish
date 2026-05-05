for D in ${CHGRP_ROOTS} ; do
  chgrp -R $(id -g) "$D" && chmod -R g=u "$D" ;
done ;
