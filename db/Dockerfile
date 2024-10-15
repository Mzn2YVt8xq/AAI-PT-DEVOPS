FROM postgres:latest

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=db_data
ENV DB_USER=master_user
ENV DB_PASSWORD=Master_password10!
ENV DB_REPL_USER=slave_user
ENV DB_REPL_PASSWORD=Slave_password10!

RUN mkdir -p /oracle/pg_data/archive/ && chown -R postgres:postgres /oracle && chmod -R 700 /oracle

RUN echo "#!/bin/bash \n\
echo \"listen_addresses = '*'\" >> \$PGDATA/postgresql.conf \n\
echo \"wal_level = replica\" >> \$PGDATA/postgresql.conf \n\echo \"archive_mode = on\" >> \$PGDATA/postgresql.conf \n\
echo \"archive_command = 'cp %p /oracle/pg_data/archive/%f'\" >> \$PGDATA/postgresql.conf \n\echo \"max_wal_senders = 10\" >> \$PGDATA/postgresql.conf \n\
echo \"wal_keep_size = 16\" >> \$PGDATA/postgresql.conf \n\echo \"host replication ${DB_REPL_USER} 0.0.0.0/0 scram-sha-256\" >> \$PGDATA/pg_hba.conf \n\
" > /docker-entrypoint-initdb.d/00-config.sh

RUN chmod +x /docker-entrypoint-initdb.d/00-config.sh

RUN echo "\
CREATE USER ${DB_USER} WITH SUPERUSER ENCRYPTED PASSWORD '${DB_PASSWORD}'; \
CREATE USER ${DB_REPL_USER} WITH REPLICATION ENCRYPTED PASSWORD '${DB_REPL_PASSWORD}'; \
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${DB_USER}; \
" > /docker-entrypoint-initdb.d/01-init.sql

COPY ./init.sql /docker-entrypoint-initdb.d/02-data.sql
