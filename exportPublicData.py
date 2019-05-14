# -*- coding: utf-8 -*-
import os
import sys
import dacs
import time
import csv
import shutil
from git import Repo
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import asnake.logging as logging
from asnake.client import ASnakeClient
#from asnake.aspace import ASpace

print (str(datetime.now()) + " Exporting Records from ArchivesSpace")

print ("\tConnecting to ArchivesSpace")
client = ASnakeClient()
client.authorize()
logging.setup_logging(stream=sys.stdout, level='INFO')

#repo = ASpace().repositories(2)

__location__ = os.path.dirname(os.path.realpath(__file__))

lastExportTime = time.time()
try:
    timePath = os.path.join(__location__, "lastExport.txt")
    with open(timePath, 'r') as timeFile:
        startTime = int(timeFile.read().replace('\n', ''))
        timeFile.close()
except:
    startTime = 0
humanTime = datetime.utcfromtimestamp(startTime).strftime('%Y-%m-%d %H:%M:%S')
print ("\tChecking for collections updated since " + humanTime)
    
output_path = "/media/SPE/collections"
pdf_path = "/media/server/browse/pdf"
staticData = os.path.join(output_path, "staticData")

#Get list of NDPA IDs
ndpaListPath = os.path.join(output_path, "ndpaList.txt")
ndpaListFile = open(ndpaListPath, "r")
ndpaList = ndpaListFile.readlines()
ndpaListFile.close()

#read existing exported collection data
collectionData = []
collectionFile = open(os.path.join(staticData, "collections.csv"), "r", encoding='utf-8')
for line in csv.reader(collectionFile, delimiter="|"):
    collectionData.append(line)
collectionFile.close()

#read existing exported subject data
subjectData = []
subjectFile = open(os.path.join(staticData, "subjects.csv"), "r", encoding='utf-8')
for line in csv.reader(subjectFile, delimiter="|"):
    subjectData.append(line)
subjectFile.close

print ("\tQuerying ArchivesSpace...")
modifiedList = client.get("repositories/2/resources?all_ids=true&modified_since=" + str(startTime)).json()
if len(modifiedList) > 0:
    print ("\tFound " + str(len(modifiedList)) + " new records!")
    print ("\tArchivesSpace URIs: " + str(modifiedList))
else:
    print ("\tFound no new records.")
for colID in modifiedList:
    collection = client.get("repositories/2/resources/" + str(colID)).json()
    if collection["publish"] != True: 
        print ("\t\tSkipping " + collection["title"] + " because it is unpublished")
    else:
        print ("\t\tExporting " + collection["title"] + " " + "(" + collection["id_0"] + ")")
    
        try:
            normalName = collection["finding_aid_title"]
        except:
            print ("\t\tError: incorrect Finding Aid Title (sort title)")
            normalName = collection["finding_aid_title"]
        
        #DACS notes/fields to check before exporting
        dacsNotes = ["ead_id", "abstract", "acqinfo", "bioghist", "scopecontent", "arrangement", "creator"]
        checkDACS = {}
        for dacsNote in dacsNotes:
            checkDACS[dacsNote] = False
        checkAccessRestrict = False
        abstract = ""
        accessRestrict = ""
        
        if "ead_id" in collection.keys():
            checkDACS["ead_id"] = True
            
        for note in collection["notes"]:
            if "type" in note.keys():
                if note["type"] == "abstract":
                    checkDACS["abstract"] = True
                    abstract = note["content"][0].replace("\n", "&#13;&#10;")
                if note["type"] == "accessrestrict":
                    checkAccessRestrict = True
                    for subnote in note["subnotes"]:
                        accessRestrict = "&#13;&#10;" + subnote["content"].replace("\n", "&#13;&#10;")
                    accessRestrict = accessRestrict.strip()
                if note["type"] == "acqinfo":
                    checkDACS["acqinfo"] = True
                if note["type"] == "bioghist":
                    checkDACS["bioghist"] = True
                if note["type"] == "scopecontent":
                    checkDACS["scopecontent"] = True
                if note["type"] == "arrangement":
                    checkDACS["arrangement"] = True
                    
                    
        for agent in collection["linked_agents"]:
            if agent["role"] == "creator":
                checkDACS["creator"] = True
        
        checkExport = all(value == True for value in checkDACS.values())
        if checkDACS["abstract"] != True:
            print ("\t\tFailed to update browse pages: Collection has no abstract.")
            print ("\t\tFailed to export collection: Collection has no abstract.")
        else:
            date = ""
            for dateData in collection["dates"]:
                if "expression" in dateData.keys():
                    date = dateData["expression"]
                else:
                    if "end" in dateData.keys():
                        normalDate = dateData["begin"] + "/" + dateData["end"]
                    else:
                        normalDate = dateData["begin"]
                    date = dacs.iso2DACS(normalDate)
            extent = ""
            for extentData in collection["extents"]:
                extent = extentData["number"] + " " + extentData["extent_type"]

            ID = collection["id_0"].lower().strip()
            checkCollection = False
            for existingCollection in collectionData:
                if existingCollection[0] == ID:
                    existingCollection[0] = ID
                    existingCollection[1] = checkExport
                    existingCollection[2] = normalName
                    existingCollection[3] = date
                    existingCollection[4] = extent
                    existingCollection[5] = abstract
                    existingCollection[6] = collection["restrictions"]
                    existingCollection[7] = accessRestrict
                    checkCollection = True
            if checkCollection == False:
                collectionData.append([ID, checkExport, normalName, date, extent, abstract, collection["restrictions"], accessRestrict])

            for subjectRef in collection["subjects"]:
                subject = client.get(subjectRef["ref"]).json()
                if subject["source"] == "meg":
                    if subject["terms"][0]["term_type"] == "topical":
                        checkSubject = False
                        for existingSubject in subjectData:
                            if existingSubject[0] == subject["title"]:
                                if not ID in existingSubject:
                                    existingSubject.append(ID)
                                checkSubject = True
                        if checkSubject == False:
                            subjectData.append([subject["title"], subjectRef["ref"], ID])    
            if checkExport != True:
                print ("\t\tFailed to export collection: ")
                for checkNote in checkDACS.keys():
                    if checkDACS[checkNote] == False:
                        print ("\t\t\t" + checkNote + " is missing")
            else:

                #sorting collection
                if ID.startswith("ger"):
                    eadDir = os.path.join(output_path, "ger")
                if ID.startswith("ua"):
                    eadDir = os.path.join(output_path, "ua")
                if ID.startswith("mss"):
                    eadDir = os.path.join(output_path, "mss")
                if ID.startswith("apap"):
                    if ID.split(".")[0] in ndpaList:
                        eadDir = os.path.join(output_path, "ndpa")
                    else:
                        eadDir = os.path.join(output_path, "apap")
                if not os.path.isdir(eadDir):
                    os.mkdir(eadDir)            
            
                resourceID = collection["uri"].split("/resources/")[1]
                print ("\t\t\tExporting EAD")
                eadResponse = client.get("repositories/2/resource_descriptions/" + resourceID + ".xml")
                eadFile = os.path.join(eadDir, ID + ".xml")
                f = open(eadFile, 'w', encoding='utf-8')
                f.write(eadResponse.text)
                f.close()
                print ("\t\t\tSuccess!")
                
                print ("\t\t\tExporting PDF")
                pdfResponse = client.get("repositories/2/resource_descriptions/" + resourceID + ".pdf")
                pdfFile = os.path.join(pdf_path, ID + ".pdf")
                f = open(pdfFile, 'wb')
                f.write(pdfResponse.content)
                f.close()
                print ("\t\t\tSuccess!")


#commit changes to git repo
print ("\tCommiting changes to Github...")
repo = Repo(output_path)
repo.git.add(update=True)
repo.git.commit("-m", "modified collections exported from ArchivesSpace")
repo.git.push('origin', 'master')


print ("\tWriting static data back to files.")
#write new collection data back to file
collectionFile = open(os.path.join(staticData, "collections.csv"), "w", newline='', encoding='utf-8')
writer = csv.writer(collectionFile, delimiter='|')
writer.writerows(collectionData)
collectionFile.close()

#write new subjects data back to file
subjectFile = open(os.path.join(staticData, "subjects.csv"), "w", newline='', encoding='utf-8')
writer = csv.writer(subjectFile, delimiter='|')
writer.writerows(subjectData)
subjectFile.close()



print ("\tCalling script to generate static pages...")
staticPages = os.path.join(__location__, "staticPages.py")

#build command list
staticCmd = ["python", staticPages]
makeStatic = Popen(staticCmd, stdout=PIPE, stderr=PIPE)
stdout, stderr = makeStatic.communicate()
if len(stdout) > 0:
    #print (stdout)
    pass
if len(stderr) > 0:
    print ("ERROR: staticPages.py failed. " + str(stderr))
else:
    print ("\tStatic browse pages generate successfully!")
    

endTimeHuman = datetime.utcfromtimestamp(lastExportTime).strftime('%Y-%m-%d %H:%M:%S')
print ("\tFinished! Last Export time is " + endTimeHuman)
timePath = os.path.join(__location__, "lastExport.txt")
with open(timePath, 'w') as timeFile:
    timeFile.write(str(lastExportTime).split(".")[0])
    timeFile.close()