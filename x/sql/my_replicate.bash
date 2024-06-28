_setup_replication_prestart() {
    if [ "x$REPLICATE_FROM" == "x" ] ; then
        sudo -u root bash -c "cat >/etc/mysql/conf.d/replication.cnf" <<EOM
[mysqld]
server-id=1
binlog-ignore-db=mysql
binlog-ignore-db=informationschema

log-bin=mysql-bin
innodb_flush_log_at_trx_commit=1
sync_binlog=1
binlog-format=row
EOM
        echo
    else
        sudo -u root bash -c "cat >/etc/mysql/conf.d/replication.cnf" <<EOM
[mysqld]
server-id=2
replicate-ignore-db=mysql
replicate-ignore-db=informationschema
EOM
        echo
    fi
}

_setup_replication_poststart() {
    if [ "x$REPLICATE_FROM" == "x" ] ; then
        echo
    else
        MYSQL_MASTER_WAIT_TIME=${MYSQL_MASTER_WAIT_TIME:-30}

        # Wait for eg. 10 seconds for the master to come up
        # do at least one iteration
        for i in $(seq $((MYSQL_MASTER_WAIT_TIME + 1))); do
            if ! mysql "-u$MYSQL_USER" "-p$MYSQL_PASSWORD" "-h$REPLICATE_FROM" -e 'SELECT 1;' | grep -q 1; then
                echo >&2 "Waiting for $MYSQL_USER@$REPLICATE_FROM"
                sleep 1
            else
                break
            fi
        done

        if [ "$i" -gt "$MYSQL_MASTER_WAIT_TIME" ]; then
            echo 2>&1 "Master is not reachable"
            exit 1
        fi

        mysql "-uroot" "-p$MYSQL_ROOT_PASSWORD" "-h$REPLICATE_FROM" -e "GRANT REPLICATION SLAVE ON *.* TO '$MYSQL_USER'@'%'"
        mysql "-uroot" "-p$MYSQL_ROOT_PASSWORD" "-h$REPLICATE_FROM" -e "FLUSH PRIVILEGES"

        # Get master position and set it on the slave. NB: MASTER_PORT and MASTER_LOG_POS must not be quoted
        MASTER_POSITION=$(mysql "-uroot" "-p$MYSQL_ROOT_PASSWORD" "-h$REPLICATE_FROM" -e "SHOW MASTER STATUS \G" | awk '/Position/ {print $2}')
        MASTER_FILE=$(mysql  "-uroot" "-p$MYSQL_ROOT_PASSWORD" "-h$REPLICATE_FROM" -e "SHOW MASTER STATUS \G" | awk '/File/ {print $2}')

        docker_process_sql --database=mysql <<<"CHANGE MASTER TO MASTER_HOST='$REPLICATE_FROM', MASTER_PORT=3306, MASTER_USER='$MYSQL_USER', MASTER_PASSWORD='$MYSQL_PASSWORD', MASTER_LOG_FILE='$MASTER_FILE', MASTER_LOG_POS=$MASTER_POSITION;"
        docker_process_sql --database=mysql <<<"START SLAVE;"
        echo "Replication started"
    fi
}

###

            _setup_replication_prestart

            mysql_note "Starting temporary server"
            docker_temp_server_start "$@"
            mysql_note "Temporary server started."

            docker_setup_db
            docker_process_init_files /docker-entrypoint-initdb.d/*

            mysql_expire_root_user

            _setup_replication_poststart

