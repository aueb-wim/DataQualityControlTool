#!/bin/sh

docker run -d --name mipmap \
       -v mapping:/opt/map:rw \
       -v target:/opt/target:rw \
       -v scripts:/opt/script:rw \
       -v source:/opt/source:rw \
       -v output:/output:rw \
       -v dbproperties:/opt/postgresdb.properties:rw \
       hbpmip/mipmap 
