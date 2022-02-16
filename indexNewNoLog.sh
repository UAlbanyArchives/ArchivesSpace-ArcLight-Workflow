#! /bin/bash

TYPE="$1"

[ -s "~/.rvm/scripts/rvm" ] && . "~/.rvm/scripts/rvm"

rvm 2.6.5@arclight

export REPOSITORY_ID=$TYPE
cd ~/arclight-UAlbany

find /opt/lib/collections/$TYPE -mtime -1 -type f -name '*.xml' -exec \
bundle exec traject -u https://solr2020.library.albany.edu:8984/solr/arclight2 -i xml \
-c ~/.rvm/gems/ruby-2.6.5@arclight/bundler/gems/arclight-f9b61c2cf12c/lib/arclight/traject/ead2_config.rb {} ';'
