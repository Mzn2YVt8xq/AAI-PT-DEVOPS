CREATE USER slave_user REPLICATION LOGIN PASSWORD '${DB_REPL_PASSWORD}';

CREATE DATABASE ${DB_DATABASE};

\c db_data;

CREATE TABLE IF NOT EXISTS  emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(15) NOT NULL
);

INSERT INTO emails (email) VALUES    
    ('max@pt.sec'),
    ('nikita2@pt.sec');

INSERT INTO phone_numbers (phone_number) VALUES
    ('+74858342309'),
    ('87492936143');
