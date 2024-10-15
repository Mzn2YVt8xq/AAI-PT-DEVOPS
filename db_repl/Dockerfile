FROM postgres:15

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=psql
ENV POSTGRES_DB=db_data

ENV DB_REPL_USER=slave_user
ENV DB_REPL_PASSWORD=Slave_password10!
ENV DB_MASTER_HOST=primary
ENV DB_MASTER_PORT=5432

RUN mkdir -p /usr/local/bin/ && \
    chmod +x /usr/local/bin/

RUN echo "#!/bin/bash \n\
set -e \n\
\n\
echo \"Configuring replica...\" \n\
\n\
until pg_isready -h \"\$DB_MASTER_HOST\" -p \"\$DB_MASTER_PORT\" -U \"\$DB_REPL_USER\"; do \n\
    sleep 2 \n\
done \n\
\n\
rm -rf \"\$PGDATA\"/* \n\
PGPASSWORD=\"\$DB_REPL_PASSWORD\" pg_basebackup -h \"\$DB_MASTER_HOST\" -D \"\$PGDATA\" -U \"\$DB_REPL_USER\" -v -P --wal-method=stream \n\
\n\
touch \"\$PGDATA\"/standby.signal \n\
\n\
echo \"primary_conninfo = 'host=\$DB_MASTER_HOST port=\$DB_MASTER_PORT user=\$DB_REPL_USER password=\$DB_REPL_PASSWORD'\" >> \"\$PGDATA\"/postgresql.conf \n\
\n\
chown -R postgres:postgres \"\$PGDATA\" \n\
\n\
exec postgres" > /usr/local/bin/replica_entrypoint.sh

RUN chmod +x /usr/local/bin/replica_entrypoint.sh

ENTRYPOINT ["/usr/local/bin/replica_entrypoint.sh"]
