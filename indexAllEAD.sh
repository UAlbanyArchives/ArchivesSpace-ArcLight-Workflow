#! /bin/bash

TYPE="$1"
CORE="$2"
#VERSION="$3"


#[ -s "/home/railsdev/.rvm/scripts/rvm" ] && . "/home/railsdev/.rvm/scripts/rvm"
[ -s "~/.rvm/scripts/rvm" ] && . "~/.rvm/scripts/rvm"

export REPOSITORY_ID=$TYPE

rvm 2.6.5@arclight

#echo "$(date) $line Export $TYPE" #>> /media/SPE/indexing-logs/index-$VERSION.log
cd ~/arclight-UAlbany

find /media/SPE/collections/$TYPE -type f -name '*.xml' -exec \
~/.rvm/gems/ruby-2.6.5@arclight/bin/traject -u https://solr2020.library.albany.edu:8984/solr/$CORE -i xml \
-c ~/.rvm/gems/ruby-2.6.5@arclight/bundler/gems/arclight-f9b61c2cf12c/lib/arclight/traject/ead2_config.rb {} ';'
