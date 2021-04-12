#!/bin/sh

HOST=mysql-db
PASSWD=best_blockchain_music_platform

docker run --name $HOST -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_DATABASE=mugo -p 3306:3306 -dit mysql:latest --default-authentication-plugin=mysql_native_password
