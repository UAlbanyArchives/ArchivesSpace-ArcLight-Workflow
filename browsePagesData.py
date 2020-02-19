import os
import json
import datetime
from asnake.aspace import ASpace

repo = ASpace().repositories(2)

outDir = "/media/Library/SPEwww/spe_website/_data"

collectionsFile = os.path.join(outDir, "collections.json")
subjectsFile = os.path.join(outDir, "subjects.json")

with open(collectionsFile, 'r', encoding='utf-8', newline='') as f:
    collections = json.load(collectionsFile)
with open(subjectsFile, 'r', encoding='utf-8', newline='') as f:
    subjects = json.load(subjectsFile)
    
timestamp = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()).strftime('%Y-%m-%dT%H:%M:%S+00:00')

for resource in repo.resources:
    #resource = repo.resources(102)
    if resource.publish == True:
        print (resource.title)
        
        collection = {}
        collection["id"] = resource.id_0
        collection["title"] = resource.title
        collection["modified"] = timestamp
        if "finding_aid_title" in dir(resource):
            collection["filing_title"] = resource.finding_aid_title
        else:
            collection["filing_title"] = resource.finding_aid_title
        collection["subjects"] = []
        for note in resource.notes:
            if "type" in dir(note):
                if note.type == "abstract":
                        collection["abstract"] = " ".join(note.content)

        for subjectURI in resource.subjects:
            subject = subjectURI.reify()
            if subject.source == "meg":
                collection["subjects"].append(subject.title)
                if not subject.title in subjects:
                    subjects.append(subject.title)
                
        for date in resource.dates:
            if date.date_type == "inclusive":
                collection["date"] = date.begin
                if "end" in dir(date):
                    collection["date"] = collection["date"] + "-" + date.end
        collection["extent"] = []
        for extent in resource.extents:
            collection["extent"].append(extent.number + " " + extent.extent_type)
        
        collection["dacs"] = True
        if not "ead_id" in dir(resource):
            collection["dacs"] = False
        checkNotes = ["abstract", "accessrestrict", "acqinfo", "bioghist", "scopecontent", "arrangement"]
        for noteName in checkNotes:
            found = False
            for note in resource.notes:
                if "type" in dir(note):
                    if note.type == noteName:
                        found = True
            if found == False:
                collection["dacs"] = False
        creator = False
        for agent in resource.linked_agents:
            if agent.role == "creator":
                creator = True
        if creator == False:
            collection["dacs"] = False
        
        previous = False
        for oldCollection in collections:
            if oldCollection["id"] = if collection["id"]:
                previous= True
                oldCollection = collection
        if previous == False:
            collections.append(collection)

with open(collectionsFile, 'w', encoding='utf-8', newline='') as f:
        json.dump(collections, f, indent=4)
with open(subjectsFile, 'w', encoding='utf-8', newline='') as f:
        json.dump(subjects, f, indent=4)