# ArchivesSpace, ArcLight, and Hyrax Workflow
This repo contains documentation and scripts for how the [M.E. Grenander Department of Special Collections & Archives](library.albany.edu/archive/) connects [ArchivesSpace](https://github.com/archivesspace/archivesspace), [ArcLight](https://github.com/sul-dlss/arclight), and [Hyrax](https://github.com/samvera/hyrax) and keeps everything synced together. It contains:

* Documentation for uploading digital object in Hyrax using existing 
* Overnight exporting and indexing scripts that update data between each service



Updated documentation for this repo is on our documentation site:

* [Overnight Export and Indexing Scripts](https://wiki.albany.edu/display/SCA/Overnight+Export+and+Indexing+Scripts)

* [Reading Overnight Export Logs](https://wiki.albany.edu/display/SCA/Reading+Overnight+Export+Logs)



## Uploading Digital Objects to Hyrax with Existing Description

Uploading Digital Objects to Hyrax

1. Go to Hyrax and login, or create an account and request uploading access
   * Let Greg know when you create an account and return when you have upload permissions.

2. Once you have upload permissions, go to Arclight, find the file that represents the digital object you want to upload. From the URI, copy the long string of letters and numbers right after the “aspace_”. This is the unique ArchivesSpace ID for that record.
   * Notice the collection ID is in the URI as well.

![Screenshot of getting ID from ArcLight URL](/img/screen1.png)

3. In your Dashboard, select “Works” on the left side menu

![Screenshot of adding a new work in Hyrax](/img/screen2.png)

4. Select the “Add new work” button on the right side

![Screenshot of adding a new work in Hyrax](/img/screen3.png)

5. For most cases, select “Digital Archival Objects” and then the “Create Work” button.

![Screenshot of adding a new DAO in Hyrax](/img/screen4.png)

6. In the “Descriptions” tab, enter only the ArchivesSpace ID, and the Collection number

![Screenshot of Pasting a ASpace ID while creating a new DAO in Hyrax](/img/screen5.png)

7. Select the “Load Record” button to pull additional metadata from Arclight ([JavaScript file](https://github.com/UAlbanyArchives/hyrax-UAlbany/blob/master/app/assets/javascripts/arclightFindRecord.js))

![Screenshot of automating import of metadata from ArcLight.](/img/screen6.png)

8. Add additional Metadata, Resource Type and Rights Statement is required, while “Additional fields”
     are not

![Screenshot of selecting a resource type.](/img/screen7.png)

9. In the “Files” tab, browse and upload any files represented by the Arclight record. These can be PDFs, Office documents (doc, docx, ppt, xlsx, etc.), or any image file.

![Screenshot of uploading a binary file to Hyrax](/img/screen8.png)

10. Select the Visibility of the work on the right side, and Save the work.

![Screenshot of selecting the visibility and saving a new work in Hyrax.](/img/screen9.png)



## Overnight Export and Indexing Scripts

### High-Level Overview

![Diagram of how these script work to keep different services interconnected.](/img/overnightScripts.png)

### What Each Script Does

#### [exportPublicData.py](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/exportPublicData.py)

* Each night, `exportPublicData.py` uses [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake) to query ArchivesSpace for resources updated since the last run.
* For collections with the complete set of [DACS-minimum](https://github.com/saa-ts-dacs/dacs/blob/70f2edb35eae2085dfbe66a89642421dcf25de52/part_I/chapter_1.md#requirements-for-single-level-descriptions) elements it exports EAD 2002 files and for collections with only abstracts and extents it saves them to Pipe-delimited CSVs.
* It also builds a [CSV of local subjects](https://github.com/UAlbanyArchives/collections/blob/master/staticData/subjects.csv) and collection IDs. 
* All this data is pushed to [Github](https://github.com/UAlbanyArchives/collections). 

#### [staticPages.py](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/staticPages.py)

* `exportPublicData.py` runs `staticPages.py` when its finished, which builds static browse pages for all collections, including a [complete A-Z list](https://archives.albany.edu/browse/alpha.html), [alpha lists](https://archives.albany.edu/browse/apap.html#G) for each [collecting area](https://archives.albany.edu/browse/91.html), and [pages for each local subject](https://archives.albany.edu/browse/subjects.html).

#### Indexing Shell Scripts

* Later, collection data is updated with `git pull` and [`indexNewEAD.sh`](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/indexNewEAD.sh) indexes EAD files updated in the past day with `find -mtime -1` into the ArcLight Solr instance.
* There are also additional indexing shell scripts for ad hoc updates. 
  * [`indexAllEAD.sh`](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/indexAllEAD.sh) reindexes all EAD files
  * [`indexOneEAD.sh`](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/indexOneEAD.sh) indexes only one EAD by collection ID (`./indexOneEAD.sh apap101`)
  * [`indexOneNDPA.sh`](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/indexOneNDPA.sh) indexes one NDPA EAD file, necessary because they have the same collection ID prefixes
  * [`indexNewNoLog.sh`](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/indexNewNoLog.sh) indexes one EAD file, but logs to the stdout instead of a log file
  * [`indexOneURL.sh`](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/indexOneURL.sh) indexes via a URL instead of from disk (not actively used)

#### [processNewUploads.py](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/processNewUploads.py)

* Finally, `processNewUploads.py` queries the Hyrax Solr index for new uploads that are connected to ArchivesSpace ref_ids, but do not have accession numbers. 
* It downloads the new binaries and metadata and creates basic Archival Information Packages (AIPs) using [bagit-python](https://github.com/LibraryOfCongress/bagit-python) 
* It then uses [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake) to add a new Digital Object Record in ArchivesSpace that links to the object in Hyrax
* Last, it adds a new accession ID in Hyrax
* (Also check out [Noah Huffman's talk](https://archivesspace.atlassian.net/wiki/spaces/ADC/pages/802127927/ArchivesSpace+Online+Forum+2019) that probably does this better [[Direct Link](https://archivesspace.atlassian.net/wiki/download/attachments/802127927/HuffmanIntegrations.pdf?version=1&modificationDate=1552665228540&cacheVersion=1&api=v2)].)

#### [dacs.py](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/dacs.py)

* A simple library that converts Posix timestamps and ISO 8601 Dates to [DACS-compliant display dates](https://github.com/saa-ts-dacs/dacs/blob/master/part_I/chapter_2/4_date.md).
* `exportPublicData.py` uses this to make dates for the static browse pages.

#### [image_a_day.py](https://github.com/UAlbanyArchives/ArchivesSpace-ArcLight-Workflow/blob/master/image_a_day.py)

* Queries the [Bing background image API](http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8) each night to display new background images for ArchivesSpace and [Find-It](https://github.com/UAlbanyArchives/find-it) just for fun.

  

### Example crontab

```
# get new image from Bing
0 2 * * * source /home/user/.bashrc; pyenv activate aspaceExport && python /opt/lib/ArchivesSpace-ArcLight-Workflow/image_a_day.py 1>> /media/SPE/indexing-logs/image_a_day.log 2>&1 && pyenv deactivate

# export data from ASpace
0 0 * * * source /home/user/.bashrc; pyenv activate aspaceExport && python /opt/lib/ArchivesSpace-ArcLight-Workflow/exportPublicData.py 1>> /media/SPE/indexing-logs/export.log 2>&1 && pyenv deactivate

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
0 2 * * * source /home/user/.bashrc; pyenv activate processNewUploads && python /opt/lib/ArchivesSpace-ArcLight-Workflow/processNewUploads.py 1>> /media/SPE/indexing-logs/processNewUploads.log 2>&1 && pyenv deactivate
```

