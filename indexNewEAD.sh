#! /bin/bash

TYPE="$1"

# The user running this script must have an arclight rvm gemset with the correct gems
# clone the arclight-UAlbany repo into your home dir and run 'bundle install' from there
#[ -s "~/.rvm/scripts/rvm" ] && . "~/.rvm/scripts/rvm"
source "$HOME/.rvm/scripts/rvm"
rvm 2.6.5@arclight

export REPOSITORY_ID=$TYPE
cd ~/arclight-UAlbany

echo "$(date) $line Export $TYPE" >> /media/Library/SPE_Automated/indexing-logs/index.log

find /opt/lib/collections/$TYPE -mtime -7 -type f -name '*.xml' -exec \
bundle exec traject -u https://solr2020.library.albany.edu:8984/solr/arclight2 -i xml \
-c ~/.rvm/gems/ruby-2.6.5@arclight/bundler/gems/arclight-f9b61c2cf12c/lib/arclight/traject/ead2_config.rb {} ';' \
-exec echo "Indexed" {} >> /media/Library/SPE_Automated/indexing-logs/index.log ';'

