# ArchivesSpace-ArcLight-Workflow
This repo contains the overnight exporting and indexing scripts for the [M.E. Grenander Department of Special Collections & Archives](library.albany.edu/archive/). These files connect our [ArchivesSpace](https://github.com/archivesspace/archivesspace), [ArcLight](https://github.com/sul-dlss/arclight), and [Hyrax](https://github.com/samvera/hyrax) instances and keep everything synced together.



## High-Level Overview

![Diagram of how these script work to keep different services interconnected.](https://archives.albany.edu/static/web/images/overnightScripts.png)

## What Each Script Does

### exportPublicData.py

* Each night, `exportPublicData.py` uses [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake) to query ArchivesSpace for resources updated since the last run.
* For collections with the complete set of [DACS-minimum](https://github.com/saa-ts-dacs/dacs/blob/70f2edb35eae2085dfbe66a89642421dcf25de52/part_I/chapter_1.md#requirements-for-single-level-descriptions) elements it exports EAD 2002 files and for collections with only abstracts and extents it saves them to Pipe-delimited CSVs.
* It also builds a [CSV of local subjects](https://github.com/UAlbanyArchives/collections/blob/master/staticData/subjects.csv) and collection IDs. 
* All this data is pushed to [Github](https://github.com/UAlbanyArchives/collections). 

### staticPages.py

* `exportPublicData.py` runs `staticPages.py` when its finished, which builds static browse pages for all collections, including a [complete A-Z list](https://archives.albany.edu/browse/alpha.html), [alpha lists](https://archives.albany.edu/browse/apap.html#G) for each [collecting area](https://archives.albany.edu/browse/91.html), and [pages for each local subject](https://archives.albany.edu/browse/subjects.html).

### Indexing Shell Scripts

* Later, collection data is updated with `git pull` and [indexNewEAD.sh](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/indexNewEAD.sh) indexes EAD files updated in the past day with `find -mtime -1` into the ArcLight Solr instance.
* There are also additional indexing shell scripts for ad hoc updates. 
  * `indexAllEAD.sh` reindexes all EAD files
  * `indexOneEAD.sh` indexes only one EAD by collection ID (`./indexOneEAD.sh apap101`)
  * `indexOneNDPA.sh` indexes one NDPA EAD file, necessary because they have the same collection ID prefixes
  * `indexNewNoLog.sh` indexes one EAD file, but logs to the stdout instead of a log file
  * `indexOneURL.sh` indexes via a URL instead of from disk (not actively used)

### processNewUploads.py

* Finally, `processNewUploads.py` queries the Hyrax Solr index for new uploads that are connected to ArchivesSpace ref_ids, but do not have accession numbers. 
* It downloads the new binaries and metadata and creates basic Archival Information Packages (AIPs) using [bagit-python](https://github.com/LibraryOfCongress/bagit-python) 
* It then uses [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake) to add a new Digital Object Record in ArchivesSpace that links to the object in Hyrax
* Last, it adds a new accession ID in Hyrax

### dacs.py

* A simple library that converts Posix timestamps and ISO 8601 Dates to [DACS-compliant display dates](https://github.com/saa-ts-dacs/dacs/blob/master/part_I/chapter_2/4_date.md).
* `exportPublicData.py` uses this to make dates for the static browse pages.

### image_a_day.py

* Queries the [Bing background image API](http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8) each night to display new background images for ArchivesSpace and [Find-It](https://github.com/UAlbanyArchives/find-it).

## Example crontab

```
# get new image from Bing
0 2 * * * source /nhome/user/.bashrc; pyenv activate aspaceExport && python /opt/lib/ArchivesSpace-ArcLight-Workflow/image_a_day.py 1>> /media/SPE/indexing-logs/image_a_day.log 2>&1 && pyenv deactivate

# export data from ASpace
0 0 * * * source /nhome/user/.bashrc; pyenv activate aspaceExport && python /opt/lib/ArchivesSpace-ArcLight-Workflow/exportPublicData.py 1>> /media/SPE/indexing-logs/export.log 2>&1 && pyenv deactivate

# pull new EADs from Gitub
30 0 * * * echo "$(date) $line git pull" >> /media/SPE/indexing-logs/git.log && git --git-dir=/opt/lib/collections/.git --work-tree=/opt/lib/collections pull 1>> /media/SPE/indexing-logs/git.log 2>&1

# Index modified apap collections
5 1 * * * /opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "apap"

# Index modified ua collections
15 1 * * * /opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "ua"

# Index modified ndpa collections
25 1 * * * /opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "ndpa"

# Index modified ger collections
35 1 * * * /opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "ger"

# Index modified mss collections
45 1 * * * /opt/lib/ArchivesSpace-ArcLight-Workflow/indexNewEAD.sh "mss"

# Download new Hyrax uploads and create new ASpace digital objects
0 2 * * * source /nhome/user/.bashrc; pyenv activate processNewUploads && python /opt/lib/ArchivesSpace-ArcLight-Workflow/processNewUploads.py 1>> /media/SPE/indexing-logs/processNewUploads.log 2>&1 && pyenv deactivate
```

