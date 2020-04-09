#!/usr/bin/env python3 
import os.path
import requests
import networkx as nx
import matplotlib.pyplot as plt
from lxml import etree
from urllib.parse import urlparse

# =============================================================================
# Ruft eine Artikelhistorie ab und transformiert diese nach XML.
#   url = parametrisierte URL der Artikelhistorie
#   return: etree-Objekt mit XML
def getHistoryXML(url):
    # Dateiname wird aus Query-Teil der URL und Endung .xml gebildet
    file = urlparse(url).query+".xml"
    # Wenn XML vorhanden, die verwenden
    if os.path.exists(file):            
        xml = etree.parse(open(file, "r"))
    # HTML abrufen, mittels Schema transformieren und lokale speichern
    else:
        html = requests.get(url).content
        tree = etree.fromstring(html, parser = etree.XMLParser())
        xml = etree.XSLT(etree.parse("history.xsl"))(tree)
        with open(file, "w") as f:
            f.write(str(xml))
    return xml
# =============================================================================

# =============================================================================
# Fügt einem networkx Graphen die Elemente eines history-Objektes hinzu.
#   graph   = zu bearbeitender nx.Graph() oder verwandte Objekte
#   history = etree-Objekt mit XML einer Artikelhistorie 
def addHistoryData(graph, history):
    # als Title wird der Teil vor dem : ermittelt und als node übernommen
    title = history.xpath('/article/title')[0].text.rsplit(": ", 1)[0]
    graph.add_node(title)
    # User als nodes hinzufügen
    for user in history.xpath('/article/versions/version/user'):
        graph.add_node(user.text)
    # Versionen als edges hinzufügen
    for version in history.xpath('/article/versions/version'):
        graph.add_edge(title, version.xpath('./user')[0].text, timestamp=version.xpath('./user')[0].text)
# =============================================================================
 
    
# now lets get all the users listed  via bs 
#soup = bs(newTreeOut, "html5lib")
#
#users = soup.find_all('user')
#
#for user in users:
#        print(user)
        
    
G = nx.Graph()
plt.rcParams["figure.figsize"] = (25, 30)

addHistoryData(G, getHistoryXML('https://en.wikipedia.org/w/index.php?title=1989_Tiananmen_Square_protests&action=history&limit=500'))
addHistoryData(G, getHistoryXML('https://en.wikipedia.org/w/index.php?title=Taiwan&action=history&limit=500'))
addHistoryData(G, getHistoryXML('https://en.wikipedia.org/w/index.php?title=Hong_Kong&action=history&limit=500'))


#nx.draw_kamada_kawai(G, with_labels=True, node_size=300)
nx.draw_networkx(G)


plt.savefig("graph.png")
plt.show()