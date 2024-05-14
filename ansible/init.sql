SELECT 'CREATE DATABASE replacedbname' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'replacedbname')\gexec
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'replacerepluser') THEN
        CREATE USER replacerepluser WITH REPLICATION ENCRYPTED PASSWORD 'replacereplpassword'; 
    END IF; 
END $$;
ALTER USER replacepostgresuser WITH PASSWORD 'replacepostgrespassword';
\c replacedbname;
DROP DATABASE IF EXISTS base_1;
CREATE DATABASE base_1;
\c base_1;
CREATE TABLE IF NOT EXISTS email(id INT PRIMARY KEY, email VARCHAR(255) NOT NULL);
CREATE TABLE IF NOT EXISTS phone_number(id INT PRIMARY KEY, phone_number VARCHAR(255) NOT NULL);
INSERT INTO email(id,email) VALUES(1,'optipro38@gmail.com');
INSERT INTO phone_number(id,phone_number) VALUES(1,'89877585983');
