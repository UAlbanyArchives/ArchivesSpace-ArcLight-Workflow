import os
import csv
import sys
import yaml
import json
import time
import uuid
import bagit
import shutil
import requests
import shortuuid
from bs4 import BeautifulSoup
from datetime import datetime
import asnake.logging as logging
from asnake.client import ASnakeClient
client = ASnakeClient()
client.authorize()

logging.setup_logging(stream=sys.stdout, level='DEBUG')
requests.packages.urllib3.disable_warnings()

__location__ = os.path.dirname(os.path.realpath(__file__))

class ArchivalInformationPackage:

    def __init__(self, colID, accession):
        aipPath= "/media/Masters/Archives/AIP"
        
        metadata = {\
        'Bag-Type': 'AIP', \
        'Bagging-Date': str(datetime.now().isoformat()), \
        'Posix-Date': str(time.time()), \
        'BagIt-Profile-Identifier': 'https://archives.albany.edu/static/bagitprofiles/aip-profile-v0.1.json', \
        }
        
        self.accession = accession
        if not os.path.isdir(os.path.join(aipPath, colID)):
            os.mkdir(os.path.join(aipPath, colID))
        self.bagDir = os.path.join(aipPath, colID, accession)
        os.mkdir(self.bagDir)
        metadata["Bag-Identifier"] = accession
        metadata["Collection-Identifier"] = colID
        
        self.bag = bagit.make_bag(self.bagDir, metadata)
        self.data = os.path.join(self.bagDir, "data")
        
    def addMetadata(self, hyraxData):
        headers = ["Type", "URIs", "File Paths", "Accession", "Collecting Area", "Collection Number", "Collection", \
        "ArchivesSpace ID", "Record Parents", "Title", "Description", "Date Created", "Resource Type", "License", \
        "Rights Statement", "Subjects", "Whole/Part", "Processing Activity", "Extent", "Language"]
        metadataPath = os.path.join(self.bagDir, "metadata")
        if not os.path.isdir(metadataPath):
            os.mkdir(metadataPath)
        metadataFile = os.path.join(metadataPath, accession + ".tsv")
        addHeaders = False
        if not os.path.isfile(metadataFile):
            addHeaders = True
        outfile = open(metadataFile, "a")
        writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
        if addHeaders == True:
            writer.writerow(headers)
        writer.writerow(hyraxData)
        outfile.close()
        
    def addFile(file):
        dataPath = os.path.join(self.bagDir, "data")
        if not os.path.isdir(metadataPath):
            os.mkdir(dataPath)
        shutil.copy2(file, dataPath)
        
def addASpaceDAO(refID, newURI, visibility):
    if visibility == "open":
        publish = True
    else:
        publish = False
        
    ref = client.get("repositories/2/find_by_id/archival_objects?ref_id[]=" + refID).json()
    item = client.get(ref["archival_objects"][0]["ref"]).json()
    existingDO = False
    existingRef = ""
    for instance in item["instances"]:
        if instance["instance_type"] == "digital_object":
            doRef = instance["digital_object"]["ref"]
            existingInstance = client.get(doRef).json()
            if existingInstance["file_versions"][0]["file_uri"] == newURI:
                existingDO = True
                existingRef = doRef        
    if existingDO == True:
        print ("\t\t\t\tFound Existing Digital Object " + existingRef)
    else:
        #make new digital object
        fileVersion = {"jsonmodel_type":"file_version", "publish": publish, "is_representative": True, "file_uri": newURI, \
                        "use_statement": "", "xlink_actuate_attribute":"none", "xlink_show_attribute":"embed"}
        daoUUID = str(uuid.uuid4())
        daoTitle = "Online Object Uploaded through Hyrax UI"
        daoObject = {"jsonmodel_type": "digital_object", "publish": publish, "external_ids": [], "subjects": [], "linked_events": [], \
                    "extents": [], "dates": [], "external_documents": [], "rights_statements": [], "linked_agents": [], \
                    "file_versions": [fileVersion], "restrictions": False, "notes": [], "linked_instances": [], "title": daoTitle, \
                    "language": "", "digital_object_id": daoUUID}

        #upload new digital object
        newDao = client.post("repositories/2/digital_objects", json=daoObject)
        daoURI = newDao.json()["uri"]
        print ("\t\t\t\tNew Digital Object " + daoURI + " --> " + str(newDao.status_code))
        
        #attach new digital object instance to archival object
        daoLink = {"jsonmodel_type": "instance", "digital_object": {"ref": daoURI}, "instance_type": "digital_object", \
                    "is_representative": False}                        
        item["instances"].append(daoLink)
        updateItem = client.post(item["uri"], json=item)
        if updateItem.status_code != 200:
            print ("\t\t\t\tFailed to attach Instance --> " + str(updateItem.status_code))
            print ("\t\t\t" + str(updateItem.text))
        else:
            print ("\t\t\t\tAttached Instance --> " + str(updateItem.status_code))
        
        #update resource
        resourceURI = item["resource"]["ref"]
        resource = client.get(resourceURI).json()
        resource.pop('system_mtime', None)
        resource.pop('user_mtime', None)
        update = client.post(resourceURI, json=resource)
        print ("\t\t\t\t" + str(update.status_code) + " --> Updated Resource for Export: " + resourceURI)
        

def checkObject(object, key):
    value = ""
    if key + "_tesim" in object.keys():
        value = "|".join(object[key + "_tesim"])
    return value


####################################################################################################################    
#START        
####################################################################################################################


print (datetime.now())
print ("Checking for New Hyrax Objects")

lastRun = time.time()
try:
	timePath = os.path.join(__location__, "lastCheckedUploads.txt")
	with open(timePath, 'r') as timeFile:
		startTime = int(timeFile.read().replace('\n', ''))
		timeFile.close()
except:
	startTime = 0

solrTime = datetime.utcfromtimestamp(startTime).strftime('%Y-%m-%dT%H:%M:%SZ')
solrTime = "2019-04-16T02:00:10Z"
print ("\tChecking for object created since " + str(solrTime))
query = "https://solr.library.albany.edu:8984/solr/hyrax/select?q=human_readable_type_sim:Dao&fq=system_modified_dtsi:[" + str(solrTime) + "%20TO%20NOW]"

#Hyrax Update CSV Path
hyraxCSV = "/media/Library/ESPYderivatives/processNewUploads/newHyraxAccessions.tsv"
   
#get Hyrax login data
configFile = os.path.join(os.path.expanduser("~"), ".hyrax.yml")
with open(configFile, 'r') as stream:
    try:
        config = yaml.load(stream, Loader=yaml.Loader)
        print ("\tRead Config Data")
    except yaml.YAMLError as exc:
        print(exc)

session = requests.Session()
loginPage = session.get(config["baseurl"], verify=False)
if loginPage.status_code != 200:
    print ("\tERROR: Unable to read login page " + config["baseurl"])
    print ("\t" + str(loginPage.text))
loginSoup = BeautifulSoup(loginPage.text, 'html.parser')
token = loginSoup.find("meta",  {"name": "csrf-token"})["content"]
loginData = {"user[email]": config["username"], "user[password]": config["password"], "authenticity_token" : token}
signin = session.post(config["baseurl"], data=loginData, verify=False)
if signin.status_code != 200:
    print ("\tERROR: Failed to login to Hyrax.")
    print ("\t" + str(signin.text))
else:
    print ("\tLogged in to Hyrax")
    
    r = requests.get(query)
    if r.status_code != 200:
        print ("\tERROR: Quering Solr " + str(r.status_code))
        print ("\tURL: " + query)
        print ("\t" + str(r.text))
    else:
        numFound = r.json()["response"]["numFound"]
        print ("\tFound " + str(numFound) + " new objects")
        allQuery = query + "&rows=" + str(numFound)
        response = requests.get(allQuery)
        if response.status_code != 200:
            print ("\tERROR: Quering Solr " + str(response.status_code))
            print ("\tURL: " + allQuery)
            print ("\t" + str(response.text))
        else:
        
            newObjects = response.json()["response"]["docs"]
            
            #build list of collections
            collectionList = []
            count = 0
            for object in newObjects:
                if "accession_tesim" in object.keys():
                    count += 1
                    print ("\tObject " + str(count) + " of " + str(numFound) + " already has an accession ID.")
                else:
                    if "workflow_state_name_ssim" in object.keys():
                        if not object["workflow_state_name_ssim"][0] == "deposited":
                            count += 1
                            print ("\tObject " + str(count) + " of " + str(numFound) + " is still under review.")
                        else:
                            colID = object["collection_number_tesim"][0]
                            if not colID in collectionList:            
                                collectionList.append(colID)
                    else:
                        colID = object["collection_number_tesim"][0]
                        if not colID in collectionList:            
                            collectionList.append(colID)
            
            count = 0
            for colID in collectionList:
                accession = colID + "_" + str(shortuuid.uuid())
                print ("\tBuilding AIP for " + accession)
                AIP = ArchivalInformationPackage(colID, accession)
                
                for object in newObjects:
                    if "accession_tesim" in object.keys():
                        count += 1
                        print ("\t\tObject " + str(count) + " of " + str(numFound) + " already has an accession ID.")
                    elif object["collection_number_tesim"][0] == colID:
                        count += 1
                        checkUnderReview = True
                        if "workflow_state_name_ssim" in object.keys():
                            if object["workflow_state_name_ssim"][0] == "deposited":
                                checkUnderReview = False
                        else:
                            checkUnderReview = False
                        
                        if checkUnderReview == False:
                            model = object["has_model_ssim"][0]
                            uri = model.lower() + "s/" + object["id"]
                            print ("\t\tReading https://archives.albany.edu/concern/" + uri + "?format=json")
                            print ("\t\tObject " + str(count) + " of " + str(numFound))
                            
                            aspaceID = object["archivesspace_record_tesim"][0]
                            recordParents = checkObject(object, "record_parent")
                            description = checkObject(object, "description")
                            dateCreated = checkObject(object, "date_created")
                            license = checkObject(object, "license")
                            rightsStmt = checkObject(object, "rights_statement")                   
                            subjects = checkObject(object, "subjects")                   
                            coverage = checkObject(object, "coverage")                
                            processing = checkObject(object, "processing")                
                            extent = checkObject(object, "extent")                
                            language = checkObject(object, "language")
                            filePaths = []

                            filesQuery = "https://archives.albany.edu/concern/" + uri + "?format=jsonld"
                            filesResponse = session.get(filesQuery, verify=False)
                            if filesResponse.status_code != 200:
                                print ("\t\tERROR: Quering JSONLD " + str(filesResponse.status_code))
                                print ("\t\tURL: " + filesQuery)
                                print ("\t\t" + str(filesResponse.text))
                            else:
                                #check if permission
                                for fileObject in filesResponse.json()["@graph"]:
                                    if "ore:proxyFor" in fileObject.keys():
                                        fileSetID = fileObject["ore:proxyFor"]["@id"].split("archives.albany.edu/catalog/")[1]
                                        fileURL = "https://archives.albany.edu/downloads/" + fileSetID
                                        print ("\t\t\tDownloading " + fileURL)
                                        fileSet = session.get("https://archives.albany.edu/concern/file_sets/" + fileSetID + "?format=json", verify=False)
                                        if fileSet.status_code != 200:
                                            print ("\t\t\tERROR: Reading FileSet " + str(fileSet.status_code))
                                            print ("\t\t\tURL: https://archives.albany.edu/concern/file_sets/" + fileSetID + "?format=json")
                                            print (str(fileSet.text))
                                        else:
                                            fileName = fileSet.json()["label"]
                                            download = session.get(fileURL, verify=False)
                                            if download.status_code != 200:
                                                print ("\t\t\tERROR: Downloading File " + str(download.status_code))
                                                print ("\t\t\tURL: " + fileURL)
                                                print (str(download.text))
                                            else:
                                                outPath = os.path.join(AIP.data, fileName)
                                                file = open(outPath, "wb")
                                                file.write(download.content)
                                                file.close()                                    
                                            filePaths.append(fileName)
                            
                            hyraxData = [model, uri, "|".join(filePaths), accession, object["collecting_area_tesim"][0], colID, \
                            object["collection_tesim"][0], aspaceID, recordParents, object["title_tesim"][0],\
                            description, dateCreated, object["resource_type_tesim"][0], license, rightsStmt, subjects, coverage, \
                            processing, extent, language]                       
                                 
                            AIP.addMetadata(hyraxData)
                            #Write to CSV to add Accession Number in Hyrax
                            hyraxAccession = [uri, object["id"], accession]
                            hyraxFile = open(hyraxCSV, "a")
                            writer = csv.writer(hyraxFile, delimiter='\t', lineterminator='\n')
                            writer.writerow(hyraxAccession)
                            hyraxFile.close()
                                                        
                            #update ASpace
                            print ("\t\t\tAdding New Digital object to http://libstaff/find-it#" + aspaceID)
                            addASpaceDAO(aspaceID, "https://archives.albany.edu/concern/" + uri, object["visibility_ssi"])
                                
                print ("\tWriting checksums...")
                AIP.bag.save(manifests=True)
                print ("\tAIP Saved!")


timePath = os.path.join(__location__, "lastCheckedUploads.txt")
with open(timePath, 'w') as timeFile:
	timeFile.write(str(lastRun).split(".")[0])
	timeFile.close()
