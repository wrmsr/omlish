            if [ "x$REPLICATE_FROM" == "x" ] ; then
                docker_init_database_dir
            else
                until psql --host ${REPLICATE_FROM} --username ${POSTGRES_USER} <<<"SELECT 1"
                do
                    echo "Waiting for master to ping..."
                    sleep 1s
                done
                until pg_basebackup -c fast -X fetch -h ${REPLICATE_FROM} -D ${PGDATA} -U ${POSTGRES_USER} -vP -w
                do
                    echo "Waiting for master to connect..."
                    sleep 1s
                done
            fi

            pg_setup_hba_conf

            if [ "x$REPLICATE_FROM" == "x" ] ; then
                cat >> ${PGDATA}/postgresql.conf <<EOF
wal_level = logical
max_replication_slots = 4
max_wal_senders = ${PG_MAX_WAL_SENDERS:-8}
wal_keep_segments = ${PG_WAL_KEEP_SEGMENTS:-8}
hot_standby = on
EOF
            else
                cat >> ${PGDATA}/postgresql.conf <<EOF
primary_conninfo = 'host=${REPLICATE_FROM} port=5432 user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}'
promote_trigger_file = '/tmp/touch_me_to_promote_to_me_master'
EOF
                touch ${PGDATA}/standby.signal
                chown postgres ${PGDATA}/standby.signal
                chmod 600 ${PGDATA}/standby.signal
            fi

            docker_temp_server_start "$@"

            if [ "x$REPLICATE_FROM" == "x" ] ; then
                docker_setup_db
            fi
