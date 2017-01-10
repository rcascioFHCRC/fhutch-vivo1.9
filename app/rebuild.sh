#!/bin/sh
set -e

#
# Rebuild VIVO
# - stop tomcat
# - run mvn clean install with fhutch specific settings
# - start tomcat
#

sudo initctl stop tomcat
mvn clean install -s fhutch.xml
sudo initctl start tomcat
