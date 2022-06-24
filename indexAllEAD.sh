#! /bin/bash

TYPE="$1"
CORE="$2"
#VERSION="$3"

# The user running this script must have an arclight rvm gemset with the correct gems
# clone the arclight-UAlbany repo into your home dir and run 'bundle install' from there
[ -s "~/.rvm/scripts/rvm" ] && . "~/.rvm/scripts/rvm"
rvm 2.6.5@arclight

cd ~/arclight-UAlbany
export REPOSITORY_ID=$TYPE

find /media/Library/SPE_Automated/collections/$TYPE -type f -name '*.xml' -exec \
bundle exec traject -u https://solr2020.library.albany.edu:8984/solr/$CORE -i xml \
-c ~/.rvm/gems/ruby-2.6.5@arclight/bundler/gems/arclight-f9b61c2cf12c/lib/arclight/traject/ead2_config.rb {} ';'
