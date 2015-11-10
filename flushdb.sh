#!/bin/bash

OS=`uname`

if [[ $OS == Darwin ]]; then
    shopt -s expand_aliases
    alias psql="psql95"
fi

echo -e "\n[ Creating template for unicode databases ]"
psql -c "UPDATE pg_database SET datistemplate = FALSE WHERE datname = 'template1'"
psql -c "DROP DATABASE template1"
psql -c "CREATE DATABASE template1 WITH TEMPLATE = template0 ENCODING = 'UNICODE'"
psql -c "UPDATE pg_database SET datistemplate = TRUE WHERE datname = 'template1'"

echo -e "\n[ Creating waspc database, user and grant rights]"
psql -c "DROP DATABASE waspc"
psql -c "DROP USER waspc"
psql -c "CREATE DATABASE waspc encoding='UTF8'"
psql -c "CREATE USER waspc WITH PASSWORD 'waspc'"
psql -c "GRANT ALL PRIVILEGES ON DATABASE waspc to waspc"

echo ""
