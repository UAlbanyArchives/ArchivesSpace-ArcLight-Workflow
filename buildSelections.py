import os
import json
import requests


def buildSelections(colID, refID=None, filter=None, date=False, verbose=False):

    
    collection = []
    page = 1

    outDir = "/media/SPE/uploads"
    
    if refID:
        url = "https://archives.albany.edu/catalog?f[record_parent_sim][]=" + refID + "&format=json&per_page=100"
        outFile = os.path.join(outDir, refID + ".json")
        descriptionURL = "https://archives.albany.edu/description/catalog/" + colID.replace(".", "-") + "aspace_" + refID
        outDesc = os.path.join(outDir, "desc_" + refID + ".json")
    else:
        url = "https://archives.albany.edu/catalog?f[collection_number_sim][]=" + colID + "&format=json&per_page=100"
        outFile = os.path.join(outDir, colID.replace(".", "-") + ".json")
        descriptionURL = "https://archives.albany.edu/description/catalog/" + colID.replace(".", "-")
        outDesc = os.path.join(outDir, "desc_" + colID.replace(".", "-") + ".json")
    if filter:
        url = url + "&" + filter
    
    print (descriptionURL + "?format=json")
    r = requests.get(descriptionURL + "?format=json", verify=False)
    print (r.status_code)
    with open(outDesc, 'w', encoding='utf-8', newline='') as f:
        json.dump(r.json()["response"], f, ensure_ascii=True, indent=4)
        

    def getPage(page, collection, url):

        r = requests.get(url + "&page=" + str(page), verify=False)
        print (r.status_code)
        for item in r.json()["response"]["docs"]:

            obj = {}
            obj["title"] = item["title_tesim"][0]
            obj["date"] = item["date_created_tesim"][0]
            obj["thumb"] = "https://archives.albany.edu" + item["thumbnail_path_ss"]
            obj["url"] = "https://archives.albany.edu/concern/" + item["has_model_ssim"][0].lower() + "s/" + item["id"]
            
            if date:
                if not obj["date"].lower() == "undated":
                    if obj["date"].lower().startswith("ca."):
                        objDate = obj["date"].split(" ")[1]
                    else:
                        if "-" in obj["date"]:
                            objDate = obj["date"].split("-")[0]
                        else:
                            objDate = obj["date"].split(" ")[0]
                    print (objDate)
                    try:
                        if int(objDate) < int(date):
                            collection.append(obj)
                    except:
                        print ("Date Error: " + objDate)
            else:
                collection.append(obj)
        if r.json()["response"]["pages"]["last_page?"] == False:
            getPage(page + 1, collection, url)

    getPage(page, collection, url)
        
        
    #print (collection)
    sortedTitle = sorted(collection, key = lambda i: i['title'].split(" ")[0])
    sortedCollection = sorted(sortedTitle, key = lambda i: i['date'].split(" ")[0])
    print (len(sortedCollection))

    with open(outFile, 'w', encoding='utf-8', newline='') as f:
        json.dump(sortedCollection, f, ensure_ascii=True, indent=4)
        
# for running with command line args
if __name__ == '__main__':
    import argparse

    argParse = argparse.ArgumentParser()
    argParse.add_argument("colID", help="ID for a package in Processing directory.")
    argParse.add_argument("-id", help="Optional ref_id for components below the collection level.", default=None)
    argParse.add_argument("-f", "--filter", help="Hyrax filter to limit results, such as \"f[resource_type_sim][]=Periodical\"", default=None)
    argParse.add_argument("-d", "--date", help="Only return items prior to a certain year of creation.", default=None)
    #argParse.add_argument("-v", "--verbose", help="lists all files written.", default=False)
    args = argParse.parse_args()
    
    buildSelections(args.colID, args.id, args.filter, args.date, True)