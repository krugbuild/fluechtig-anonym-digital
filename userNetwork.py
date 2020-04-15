#!/usr/bin/env python3 
import os.path
import requests
import networkx as nx
import matplotlib.pyplot as plt
from lxml import etree
from urllib.parse import urlparse
from pyvis.network import Network
import csv

# =============================================================================
# Ruft eine Seite ab und transformiert diese nach XML.
#   url = parametrisierte URL der Artikelhistorie oder User contributions
#   stylesheet = xslt zur Transaformation der abzurufenden Daten
#   return: etree-Objekt mit XML

def getXMLdata(url, stylesheet):
    datadir = "data/"
    lang = urlparse(url).netloc.split(".")[0] + "_"
    # Dateiname wird aus Query-Teil der URL und Endung .xml gebildet
    if urlparse(url).query:
        file = urlparse(url).query + ".xml"
    # Falls kein Queryteil vorhanden, letzter Pfadteil +.xml
    else:
        file = str(urlparse(url).path.rsplit("/")[-1]) + ".xml"
    # vollständiger Pfad aus Verzeichnis/Sprachversion_Dateiname.xml
    file = datadir + lang + file
    # Wenn XML bereits vorhanden, die verwenden
    if os.path.exists(file):            
        xml = etree.parse(open(file, "r"))
    # HTML abrufen, mittels Schema transformieren und lokal speichern
    else:
        html = requests.get(url).content
        tree = etree.fromstring(html, parser = etree.XMLParser(recover=True))
        xml = etree.XSLT(etree.parse(stylesheet))(tree)
        with open(file, "w") as f:
            f.write(str(xml))
    return xml

# =============================================================================
# dictionary-def:
# nodes { name(title/user), lang, type(article/user) }
# edges { user, article, timestamp, id }
# =============================================================================
    
# Liest eine article history XML aus und trägt den Artikel und die verzeichneten
# User als nodes sowie die Versionen als edges ein
def addArticleData(nodes, edges, article):
    # article-node zusammenstellen
    article_node = {"name": article.xpath('/article/title')[0].text.rsplit(": ", 1)[0]
                    , "lang": article.xpath('/article/language')[0].text
                    , "type": "article"}
    # article hinzufügen, sofern neu
    if article_node not in nodes:
        nodes.append(article_node)
        print("article added: " + str(article_node))
    # user als nodes, versions als edges hinzufügen
    for version in article.xpath('/article/versions/version'):
        # user-node zusammenstellen
        user_node = {"name": version.xpath('./user')[0].text
                     , "lang": article_node["lang"] # bessere quelle haben wir aktuell nicht
                     , "type": "user"}
        # user hinzufügen, sofern neu
        if user_node not in nodes:
            nodes.append(user_node)
            print("user added: " + str(user_node))
        # version als edge hinzufügen
        version_edge = {"user": user_node["name"]
                        , "article": article_node["name"]
                        , "timestamp": version.xpath('./timestamp')[0].text
                        , "id": version.xpath('./id')[0].text}
        if version_edge not in edges:
            edges.append(version_edge)
    
# =============================================================================
    
def addUserData(nodes, edges, user):
    # user-node zusammenstellen
    user_node = {"name": user.xpath('/user/name')[0].text
                 , "lang": user.xpath('/user/language')[0].text
                 , "type": "user"}
    # user hinzufügen, sofern neu
    if user_node not in nodes:
        nodes.append(user_node)
        print("user added: " + str(user_node))
    # articles als nodes, versions als edges hinzufügen
    if user.xpath('/user/versions/version') is not None:
        for version in user.xpath('/user/versions/version'):
            # article-node zusammenstellen
            article_node = {"name": version.xpath('./title')[0].text
                            , "lang": user_node["lang"] # bessere quelle haben wir aktuell nicht
                            , "type": "article"}
            # article hinzufügen, sofern neu
            if article_node not in nodes:
                nodes.append(article_node)
                print("article added: " + str(article_node))
            # version als edge hinzufügen
            version_edge = {"user": user_node["name"]
                            , "article": article_node["name"]
                            , "timestamp": version.xpath('./timestamp')[0].text
                            , "id": version.xpath('./id')[0].text}
            if version_edge not in edges:
                edges.append(version_edge)
        
# =============================================================================    
# Visualisierung über Pyvis, browserbasiert, physics
                
def createPyvisNetwork(nodes, edges):    
    ## Graph anlegen        
    netGraph = Network(height='750pt', width='100%', bgcolor="#222222", font_color="white")        
    # Daten in Graph eintragen                   
    for node in nodes:
        if node["type"] == "user":
            netGraph.add_node(node["name"], shape="dot")
        elif node["type"] == "article":
            if node["lang"] == "zh":
                netGraph.add_node(node["name"], shape="star", title = "https://"+node["lang"]+".wikipedia.org/"+node["name"], color = "red")
            else:
                netGraph.add_node(node["name"], shape="star", title = "https://"+node["lang"]+".wikipedia.org/"+node["name"], color = "blue")
    for edge in edges:
        netGraph.add_edge(edge["user"], edge["article"])
    #netGraph.barnes_hut()
    netGraph.show('networkmap.html')        

# =============================================================================  
# Visualisierung über Networkx, minimalistisch
    
def createNetxNetwork(nodes, edges):  
    graph = nx.Graph()
    plt.rcParams["figure.figsize"] = (30, 30)
    
    for node in nodes:
        graph.add_node(node["name"])
    for edge in edges:
        graph.add_edge(edge["user"], edge["article"])
#    
#    # User als nodes hinzufügen
#    for user in history.xpath('/article/versions/version/user'):
#        graph.add_node(user.text)
#    # Versionen als edges hinzufügen
#    for version in history.xpath('/article/versions/version'):
#        graph.add_edge(title, version.xpath('./user')[0].text, timestamp=version.xpath('./user')[0].text)
#    
    nx.draw_kamada_kawai(graph, with_labels=True, node_size=300)
    nx.draw_networkx(graph)
    
    
    plt.savefig("graph.png")
    plt.show()

# =============================================================================    
        
def createGephiExport(nodes, edges):
    with open('nodes.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'lang', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(nodes)
    with open('edges.csv', 'w', newline='') as csvfile:
        fieldnames = ['user', 'article', 'timestamp', 'id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(edges)

# =============================================================================    

nodes = list()
edges = list()

# Articles Abrufen und als XML speichern. NB Limit anpassen
# en article
addArticleData(nodes, edges, getXMLdata('https://en.wikipedia.org/w/index.php?title=1989_Tiananmen_Square_protests&action=history&limit=500', 'history.xsl'))
addArticleData(nodes, edges, getXMLdata('https://en.wikipedia.org/w/index.php?title=Hong_Kong&action=history&limit=500', 'history.xsl'))
# zh article
addArticleData(nodes, edges, getXMLdata('https://zh.wikipedia.org/w/index.php?title=%E5%85%AD%E5%9B%9B%E4%BA%8B%E4%BB%B6&action=history&limit=500', 'history.xsl'))
addArticleData(nodes, edges, getXMLdata('https://zh.wikipedia.org/w/index.php?title=%E9%A6%99%E6%B8%AF&action=history&limit=500', 'history.xsl'))

# zugehörige user-netzwerke ermitteln
for node in nodes:
    if node["type"] == "user":
        # Aufruf je Sprachversion, NB &target=USERNAME muss als letztes Element notiert sein (sonst liefert das Schema nichts)
        addUserData(nodes, edges, getXMLdata('https://en.wikipedia.org/w/index.php?title=Special:Contributions&limit=100&target=' + node["name"], 'user.xsl'))
        addUserData(nodes, edges, getXMLdata('https://zh.wikipedia.org/w/index.php?title=Special:用户贡献&limit=100&target=' + node["name"], 'user.xsl'))
        
#createNetxNetwork(nodes, edges)
#createGephiExport(nodes, edges)
createPyvisNetwork(nodes, edges)


# ================== Stuff ================================


#addHistoryData_list(nodes, edges, getHistoryXML('https://en.wikipedia.org/w/index.php?title=Taiwan&action=history&limit=1000'))


#countOccurences(nodes, edges)

#for node in nodes:
#    if {"id": node["id"], "language": node["language"], "occ": nodes.count(node)} not in nodes_unique:
#        nodes_unique.append({"id": node["id"], "language": node["language"], "occ": nodes.count(node)})

#netGraph = Network(height='750pt', width='100%', bgcolor="#222222", font_color="white")        
#
#for node in nodes:                   
#    #netGraph.add_node(node["id"], size=node["occ"])
#    netGraph.add_node(node["name"])
#for edge in edges:
#    netGraph.add_edge(edge["user"], edge["article"])

#netGraph.show_buttons()                   
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
#netGraph.show('networkmap.html')







#def countOccurences(nodes, edges):
#    temp_list = list()
#    for node in nodes:
#        if {"id": node["id"], "language": node["language"], "occ": nodes.count(node)} not in temp_list:
#            temp_list.append({"id": node["id"], "language": node["language"], "occ": nodes.count(node)})    
#    nodes.clear()
#    nodes += temp_list
#    temp_list.clear()
#    # edges haben timestamps -.-








