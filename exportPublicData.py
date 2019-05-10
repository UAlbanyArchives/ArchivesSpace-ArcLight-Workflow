# -*- coding: utf-8 -*-
import os
import sys
import dacs
import time
import csv
import shutil
from subprocess import Popen, PIPE, STDOUT
import asnake.logging as logging
from asnake.client import ASnakeClient
#from asnake.aspace import ASpace

client = ASnakeClient()
client.authorize()
logging.setup_logging(stream=sys.stdout, level='INFO')

#repo = ASpace().repositories(2)

__location__ = os.path.dirname(os.path.realpath(__file__))

try:
    timePath = os.path.join(__location__, "lastExport.txt")
    with open(timePath, 'r') as timeFile:
        startTime = int(timeFile.read().replace('\n', ''))
        timeFile.close()
except:
    startTime = 0
    
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

print ("Checking for collections updated since last export...")
modifiedList = client.get("repositories/2/resources?all_ids=true&modified_since=" + str(startTime)).json()
for colID in modifiedList:
    collection = client.get("repositories/2/resources/" + str(colID)).json()
    if collection["publish"] == True: 
    
        try:
            normalName = collection["finding_aid_title"]
        except:
            print ("error with " + collection["id_0"])
            normalName = collection["finding_aid_title"]
        
        checkAbstract = False
        checkAccessRestrict = False
        checkDACS = [False, False, False, False, False, False]
        accessRestrict = ""
        
        for note in collection["notes"]:
            if "type" in note.keys():
                if note["type"] == "abstract":
                    checkAbstract = True
                    abstract = note["content"][0].replace("\n", "&#13;&#10;")
                if note["type"] == "accessrestrict":
                    checkAccessRestrict = True
                    for subnote in note["subnotes"]:
                        accessRestrict = "&#13;&#10;" + subnote["content"].replace("\n", "&#13;&#10;")
                    accessRestrict = accessRestrict.strip()
                if note["type"] == "acqinfo":
                    checkDACS[0] = True
                if note["type"] == "bioghist":
                    checkDACS[1] = True
                if note["type"] == "scopecontent":
                    checkDACS[2] = True
                if note["type"] == "arrangement":
                    checkDACS[3] = True
                    
                    
        for agent in collection["linked_agents"]:
            if agent["role"] == "creator":
                checkDACS[4] = True
        
        if "ead_id" in collection.keys():
            checkDACS[5] = True
                
        if checkAbstract == True:
            print ("exporting " + collection["title"])
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
                    existingCollection[1] = all(checkDACS)
                    existingCollection[2] = normalName
                    existingCollection[3] = date
                    existingCollection[4] = extent
                    existingCollection[5] = abstract
                    existingCollection[6] = collection["restrictions"]
                    existingCollection[7] = accessRestrict
                    checkCollection = True
            if checkCollection == False:
                collectionData.append([ID, all(checkDACS), normalName, date, extent, abstract, collection["restrictions"], accessRestrict])

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


            if all(checkDACS) == True:
                resourceID = collection["uri"].split("/resources/")[1]
                eadFile = client.get("repositories/2/resource_descriptions/" + resourceID + ".xml")
                
                try:
                    pdfFile = client.get("repositories/2/resource_descriptions/" + resourceID + ".pdf")
                    pdfFile = AS.exportPDF(session, repo, collection, pdf_path, loginData)
                    print ("    " + ID + " exported successfully.")
                except:
                    errorNote = "Error converting collection: " + ID
                    print (errorNote)
                    file = open(os.path.join(__location__, "collectionErrors.log"), "a")
                    file.write(errorNote)
                    file.close()
                apapDir = os.path.join(output_path, "apap")
                ndpaDir = os.path.join(output_path, "ndpa")
                mssDir = os.path.join(output_path, "mss")
                gerDir = os.path.join(output_path, "ger")
                uaDir = os.path.join(output_path, "ua")
                if not os.path.isdir(apapDir):
                    os.mkdir(apapDir)
                if not os.path.isdir(ndpaDir):
                    os.mkdir(ndpaDir)
                if not os.path.isdir(mssDir):
                    os.mkdir(mssDir)
                if not os.path.isdir(gerDir):
                    os.mkdir(gerDir)
                if not os.path.isdir(uaDir):
                    os.mkdir(uaDir)
                for newEAD in os.listdir(output_path):
                    if newEAD.endswith(".xml"):
                        newEadFile = os.path.join(output_path, newEAD)
                        if newEAD.startswith("ger"):
                            shutil.copy2(newEadFile, gerDir)
                        if newEAD.startswith("ua"):
                            shutil.copy2(newEadFile, uaDir)
                        if newEAD.startswith("mss"):
                            shutil.copy2(newEadFile, mssDir)
                        if newEAD.startswith("apap"):
                            if newEAD.split(".")[0] in ndpaList:
                                shutil.copy2(newEadFile, ndpaDir)
                            else:
                                shutil.copy2(newEadFile, apapDir)
                        if os.path.isfile(newEadFile):
                            os.remove(newEadFile)
            else:
                print ("Collection incomplete:")
                if checkDACS[0] == False:
                    print ("    missing: acqinfo")
                if checkDACS[1] == False:
                    print ("    missing: bioghist")
                if checkDACS[2] == False:
                    print ("    missing: scopecontent")
                if checkDACS[3] == False:
                    print ("    missing: arrangement")
                if checkDACS[4] == False:
                    print ("    missing: creator")
                if checkDACS[5] == False:
                    print ("    missing: ead_id")


#commit changes to git repo
print ("Commiting changes...")
addCmd = ["git", "-C", output_path, "add", "."]
gitAdd = Popen(addCmd, stdin=PIPE)
gitAdd.communicate()
commitCmd = ["git", "-C", output_path, "commit", "-m", "modified collections exported from ArchivesSpace"]
gitCommit = Popen(commitCmd, stdin=PIPE)
gitCommit.communicate()
pushCmd = ["git", "-C", output_path, "push", "origin", "master"]
gitPush = Popen(pushCmd, stdout=PIPE, stderr=PIPE)
gitPush.communicate()

                
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

timePath = os.path.join(__location__, "lastExport.txt")
with open(timePath, 'w') as timeFile:
    timeFile.write(str(time.time()).split(".")[0])
    timeFile.close()

    

msg = "Calling script to generate static pages..."
print (msg)

staticPages = os.path.join(__location__, "staticPages.py")

#build command list
staticCmd = ["python", "staticPages.py"]
makeStatic = Popen(staticCmd, stdout=PIPE, stderr=PIPE)
stdout, stderr = makeStatic.communicate()
if len(stdout) > 0:
    #print (stdout)
    pass
if len(stderr) > 0:
    print ("ERROR: staticPages.py failed. " + str(stderr))
else:
    print ("Export Complete")
