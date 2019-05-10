#! /bin/bash

TYPE="$1"

[ -s "/usr/local/rvm/scripts/rvm" ] && . "/usr/local/rvm/scripts/rvm"

rvm 2.4.1@arclight

echo "$(date) $line Indexing $TYPE" >> /media/SPE/index.log
cd /home/gw234478/arclight-UAlbany

find /home/gw234478/collections/$TYPE -mtime -1 -type f -name '*.xml' -exec \
bundle exec rake arclight:index SOLR_URL=https://solr.library.albany.edu:8984/solr/arclight-testing REPOSITORY_ID=$TYPE FILE={} ';'
