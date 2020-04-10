#!/usr/bin/env python3 
import os.path
import requests
from lxml import etree
from urllib.parse import urlparse
from pyvis.network import Network

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
#def addHistoryData(graph, history):
#    # als Title wird der Teil vor dem : ermittelt und als node übernommen
#    title = history.xpath('/article/title')[0].text.rsplit(": ", 1)[0]
#    # farbe je nach Sprachversion
#    if history.xpath('/article/language')[0].text == 'zh':
#        graph.add_node(title, color = "red", value = 100)
#    elif history.xpath('/article/language')[0].text == 'en':
#        graph.add_node(title, color = "blue", value = 100)
#    # User als nodes hinzufügen
#    for user in history.xpath('/article/versions/version/user'):
#        graph.add_node(user.text, value = 10)
#    # Versionen als edges hinzufügen
#    for version in history.xpath('/article/versions/version'):
#        
#        graph.add_edge(title, version.xpath('./user')[0].text, timestamp=version.xpath('./timestamp')[0].text)
#        #graph.edges.index(['from',title])
# =============================================================================
    
def addHistoryData_list(nodes, edges, history):
    title = history.xpath('/article/title')[0].text.rsplit(": ", 1)[0]
    # Artikel hinzufügen
    nodes.append({"id": title, "language": history.xpath('/article/language')[0].text})
    # User hinzufügen
    for user in history.xpath('/article/versions/version/user'):
        nodes.append({"id": user.text, "language": ""})
    # Versionen als edges hinzufügen
    for version in history.xpath('/article/versions/version'):
        edges.append({"from": version.xpath('./user')[0].text, "timestamp": version.xpath('./timestamp')[0].text, "to":title})

# =============================================================================
    
def countOccurences(nodes, edges):
    temp_list = list()
    for node in nodes:
        if {"id": node["id"], "language": node["language"], "occ": nodes.count(node)} not in temp_list:
            temp_list.append({"id": node["id"], "language": node["language"], "occ": nodes.count(node)})    
    nodes.clear()
    nodes += temp_list
    temp_list.clear()
    # edges haben timestamps -.-
    
nodes = list()
edges = list()


addHistoryData_list(nodes, edges, getHistoryXML('https://en.wikipedia.org/w/index.php?title=1989_Tiananmen_Square_protests&action=history&limit=1000'))
addHistoryData_list(nodes, edges, getHistoryXML('https://en.wikipedia.org/w/index.php?title=Taiwan&action=history&limit=1000'))

countOccurences(nodes, edges)

#for node in nodes:
#    if {"id": node["id"], "language": node["language"], "occ": nodes.count(node)} not in nodes_unique:
#        nodes_unique.append({"id": node["id"], "language": node["language"], "occ": nodes.count(node)})

netGraph = Network(height='750pt', width='100%', bgcolor="#222222", font_color="white")        

for node in nodes:                   
    netGraph.add_node(node["id"], size=node["occ"])
for edge in edges:
    netGraph.add_edge(edge["from"], edge["to"])

netGraph.show_buttons()                   
#                   
#addHistoryData(netGraph, getHistoryXML('https://en.wikipedia.org/w/index.php?title=1989_Tiananmen_Square_protests&action=history&limit=1000'))
#addHistoryData(netGraph, getHistoryXML('https://en.wikipedia.org/w/index.php?title=Taiwan&action=history&limit=1000'))
#addHistoryData(netGraph, getHistoryXML('https://en.wikipedia.org/w/index.php?title=Hong_Kong&action=history&limit=1000'))
## taiwan
#addHistoryData(netGraph, getHistoryXML('https://zh.wikipedia.org/w/index.php?title=%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B&action=history&limit=1000'))
## tiananmen
#addHistoryData(netGraph, getHistoryXML('https://zh.wikipedia.org/w/index.php?title=%E5%85%AD%E5%9B%9B%E4%BA%8B%E4%BB%B6&action=history&limit=1000'))
## hong kong
#addHistoryData(netGraph, getHistoryXML('https://zh.wikipedia.org/w/index.php?title=%E9%A6%99%E6%B8%AF&action=history&limit=1000'))
#
netGraph.show('networkmap.html')
























