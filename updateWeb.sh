#!/usr/bin/bash

output=$( git --git-dir=/var/www/spe_website.git --work-tree=/var/www/spe_website fetch --dry-run 2>&1 )

if [[ $output ]]; then
    git --git-dir=/var/www/spe_website/.git --work-tree=/var/www/spe_website fetch
    cd /var/www/spe_website && jekyll build
else
    true
fi