#!/usr/bin/env python3 
import requests
from lxml import etree
from bs4 import BeautifulSoup as bs

URL = 'https://en.wikipedia.org/w/index.php?title=1989_Tiananmen_Square_protests&action=history'

page = requests.get(URL)

html = page.content

### oder doch einfach HTML ziehen und dann per XML parsen?
tree = etree.fromstring(html, parser = etree.XMLParser())       # behandeln als XML

xslt = etree.parse("history.xsl")

#transform = etree.XSLT(xslt)
newTree = etree.XSLT(xslt)(tree)

# save this shit localy - dafür brauchen wir das als string 
newTreeOut = str(newTree)
    
with open("hist.xml", "w") as f:
    f.write(newTreeOut)
    
# now lets get all the users listed  via bs 
#soup = bs(newTreeOut, "html5lib")
#
#users = soup.find_all('user')
#
#for user in users:
#        print(user)
        
    
# how to iterate via xpath
r = newTree.xpath('/article/versions/version/user')
for user in r:
    print(user.text)
    
