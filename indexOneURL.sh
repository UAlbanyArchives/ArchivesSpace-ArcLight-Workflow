#! /bin/bash

TYPE="$1"

[ -s "/usr/local/rvm/scripts/rvm" ] && . "/usr/local/rvm/scripts/rvm"

rvm 2.4.1@arclight

echo "$(date) $line Indexing $TYPE.xml" >> /media/SPE/indexing-logs/index.log
cd /var/www/arclight-UAlbany

AREA=${TYPE//[0-9.]/}
echo $AREA/$TYPE.xml

bundle exec rake arclight:index_url URL=https://raw.githubusercontent.com/UAlbanyArchives/collections/master/$AREA/$TYPE.xml REPOSITORY_ID=$AREA SOLR_URL=https://solr.library.albany.edu:8984/solr/arclight-prod
