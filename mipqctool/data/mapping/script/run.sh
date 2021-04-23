#!/bin/sh

#dockerize -template /opt/postgresdb.properties/mipmap-db.properties.tmpl:/opt/postgresdb.properties/mipmap-db.properties
cp /opt/map/map.xml /opt/map.xml


# Mapping Section
echo "Performing mapping task"
 
java -jar /opt/MIPMapReduced.jar /opt/map.xml /opt/postgresdb.properties/mipmap-db.properties -csv /output
