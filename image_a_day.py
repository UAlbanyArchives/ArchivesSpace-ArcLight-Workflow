# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as Soup
import urllib.request

def update(htmlPath):
	f = open(htmlPath,"r", encoding="utf-8")
	htmlString = f.read()
	f.close()

	soup = Soup(htmlString, "html.parser")
	soup.find('body')['style'] = "background-image: url(" + url + ")"
	div = soup.find('div', {"id": "photo-info"})
	soup.find('p', {"id": "photo-desc"}).extract()
	div.append(Soup('<p id="photo-desc">' + desc + '. <a href="' + moreDetails + '">More</a></p>', 'html.parser'))

	outString = str(soup)

	f = open(htmlPath, "wb")
	f.write(outString.encode('utf8'))
	f.close()

findDoc = "\\\\libstaff\\wwwroot\\find-it\\index.html"
boxDoc = "\\\\libstaff\\wwwroot\\find-it\\boxes.html"
asBG = "\\\\romeo\\wwwroot\\eresources\\static\\img\\aspaceBG.jpg"

r = requests.get('http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8')

imageData = r.json()["images"][0]
url = "http://www.bing.com" + imageData["url"]
desc = imageData["copyright"]
if "(" in desc:
	desc = desc.split("(")[0].strip()
moreDetails = imageData["copyrightlink"]

urllib.request.urlretrieve(url, asBG)

update(findDoc)
update(boxDoc)