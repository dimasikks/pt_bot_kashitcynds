CREATE USER replicator with replication encrypted password 'Qq12345';
SELECT pg_create_physical_replication_slot('replication_slot');
CREATE TABLE IF NOT EXISTS email(id SERIAL PRIMARY KEY, email VARCHAR (100) NOT NULL);
CREATE TABLE IF NOT EXISTS phone_number(id SERIAL PRIMARY KEY, phone_number VARCHAR (100) NOT NULL);
INSERT INTO email(email) VALUES ('optipro38@gmail.com');
INSERT INTO phone_number(phone_number) VALUES ('89877585983');
