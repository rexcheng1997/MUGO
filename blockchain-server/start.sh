#!/bin/sh

docker build . -t blockchain-container
docker run --name blockchain-server -p 5000:5000 -dit blockchain-container
