# -*- coding: utf-8 -*-

import json
import requests
import urllib.request

asBG = "/media/Library/SPEwww/browse/img/aspaceBG.jpg"
descFile = "/media/Library/SPEwww/browse/js/bgDesc.json"


r = requests.get('https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8')

imageData = r.json()["images"][0]
url = "https://www.bing.com" + imageData["url"]
desc = imageData["copyright"]
title = imageData["title"]
if "(" in desc:
	desc = desc.split("(")[0].strip()
moreDetails = imageData["copyrightlink"]

urllib.request.urlretrieve(url, asBG)

data = {"description": desc, "link": moreDetails, "title": title}
with open(descFile, 'w') as outfile:
    json.dump(data, outfile)
