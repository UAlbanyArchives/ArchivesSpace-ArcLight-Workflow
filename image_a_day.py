# -*- coding: utf-8 -*-

import json
import requests
import urllib.request

asBG = "/media/server/browse/img/aspaceBG.jpg"
descFile = "/media/server/browse/js/bgDesc.json"


r = requests.get('http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8')

imageData = r.json()["images"][0]
url = "http://www.bing.com" + imageData["url"]
desc = imageData["copyright"]
if "(" in desc:
	desc = desc.split("(")[0].strip()
moreDetails = imageData["copyrightlink"]

urllib.request.urlretrieve(url, asBG)

data = {"description": desc, "link": moreDetails}
with open(descFile, 'w') as outfile:
    json.dump(data, outfile)