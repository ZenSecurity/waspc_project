#!/bin/bash

psql -c 'DROP DATABASE waspc'
psql -c 'DROP USER waspc'
psql -c 'CREATE DATABASE waspc'
psql -c "CREATE USER waspc WITH PASSWORD 'waspc'"
psql -c 'GRANT ALL PRIVILEGES ON DATABASE waspc to waspc'
