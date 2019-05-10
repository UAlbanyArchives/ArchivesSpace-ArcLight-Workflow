#! /bin/bash

TYPE="$1"

[ -s "/usr/local/rvm/scripts/rvm" ] && . "/usr/local/rvm/scripts/rvm"

rvm 2.4.1@arclight

echo "$(date) $line Export $TYPE" #>> /media/SPE/indexing-logs/index.log
cd /var/www/arclight-UAlbany

find /opt/lib/collections/$TYPE -type f -name '*.xml' -exec \
bundle exec rake arclight:index SOLR_URL=https://solr.library.albany.edu:8984/solr/arclight-prod REPOSITORY_ID=$TYPE FILE={} ';' #\
#&>> /media/SPE/indexing-logs/index.log ';'
