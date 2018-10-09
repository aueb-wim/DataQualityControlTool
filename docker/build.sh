#!/bin/bash

if groups $USER | grep &>/dev/null '\bdocker\b'; then
  DOCKER="docker"
else
  DOCKER="sudo docker"
fi

$DOCKER build -t python/qclibs --build-arg BUILD_DATE=$(date --iso-8601=seconds) .
