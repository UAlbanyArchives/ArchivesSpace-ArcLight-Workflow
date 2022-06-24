#! /bin/bash
# A simplier path to exporting from ArchivesSpace to ArcLight
# not used in practice yet

#source /nhome/gw234478/.bashrc
#pyenv activate aspaceExport

# Export from ASpace to Github
python3 /opt/lib/ArchivesSpace-ArcLight-Workflow/exportPublicData.py 1>> /media/Library/SPE_Automated/indexing-logs/export.log

# Pull files from Github
echo "$(date) $line git pull" >> /media/SPE/indexing-logs/git.log && git --git-dir=/opt/lib/collections/.git --work-tree=/opt/lib/collections pull 1>> /media/Library/SPE_Automated/indexing-logs/git.log 2>&1

# index all new files in ArcLight Solr core
/opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "apap"
/opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "ua"
/opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "ndpa"
/opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "ger"
/opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "mss"
