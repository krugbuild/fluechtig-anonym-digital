#!/usr/bin/env python3 
import os.path
import ast
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
    article_node = [article.xpath('/article/title')[0].text.rsplit(": ", 1)[0] # name
                    , {article.xpath('/article/language')[0].text : 1} # language
                    , 'article'] # type
    # article hinzufügen, sofern neu
    if article_node not in nodes:
        nodes.append(article_node)
        print('article added: ' + str(article_node))
    # user als nodes, versions als edges hinzufügen
    for version in article.xpath('/article/versions/version'):
        # user-node zusammenstellen
        user_node = [version.xpath('./user')[0].text # name
                     , {} # language
                     , 'user'] # type
        # user hinzufügen, sofern neu
        if user_node not in nodes:
            nodes.append(user_node)
            print('user added: ' + str(user_node))
        # version als edge hinzufügen
        version_edge = [user_node[0] # user
                        , article_node[0] #article
                        , version.xpath('./timestamp')[0].text # timestamp
                        , version.xpath('./id')[0].text] # version id
        if version_edge not in edges:
            edges.append(version_edge)
    
# =============================================================================
    
def addUserData(nodes, edges, user):
    # user-node zusammenstellen
    user_node = [user.xpath('/user/name')[0].text #name
                 , {} #language
                 , 'user'] #type
    # user hinzufügen, sofern neu
    if user_node not in nodes:
        nodes.append(user_node)
        print('user added: ' + str(user_node))
    # articles als nodes, versions als edges hinzufügen
    if user.xpath('/user/versions/version') is not None:
        for version in user.xpath('/user/versions/version'):
            # article-node zusammenstellen
            article_node = [version.xpath('./title')[0].text #name
                            , {user.xpath('/user/language')[0].text : 1} # lang: bessere quelle haben wir aktuell nicht
                            , 'article'] # type
            # article hinzufügen, sofern neu
            if article_node not in nodes:
                nodes.append(article_node)
                print('article added: ' + str(article_node))
            # version als edge hinzufügen
            version_edge = [user_node[0] # user 
                            , article_node[0] # article
                            , version.xpath('./timestamp')[0].text #timestamp
                            , version.xpath('./id')[0].text] #version id
            if version_edge not in edges:
                edges.append(version_edge)
        
# =============================================================================    
# Visualisierung über Pyvis, browserbasiert, physics
                
def createPyvisNetwork(nodes, edges):
    ## Graph anlegen        
    netGraph = Network(height='750pt', width='100%', bgcolor="#222222", font_color="white")
    print("erzeuge Graph ..")
    # Daten in Graph eintragen                   
    #netGraph.add_nodes([name for [name, lang, type] in nodes if type == "user"])
    for node in nodes:
        if node[2] == "user":
            netGraph.add_node(node[0], shape="dot", color = langColor(node[1]))
        elif node[2] == "article":
            netGraph.add_node(node[0], shape="star", title = node[0], color = langColor(node[1]))
    print('füge edges hinzu ..')
    for edge in edges:
        # die Anzahl der Versionen dient als Indikator für die Stärke der edge
        netGraph.add_edge(edge[0], edge[1], value=len(edge[3]))
    netGraph.barnes_hut()
    netGraph.show('networkmap.html')        

# =============================================================================  
# Visualisierung über Networkx, minimalistisch
    
def createNetxNetwork(nodes, edges):  
    graph = nx.Graph()
    plt.rcParams["figure.figsize"] = (25, 15)
    print('erzeuge Graph ..')
    graph.add_nodes_from([name for [name, lang, type] in nodes])
    for edge in edges:        
        graph.add_edge(edge[0], edge[1], weight=len(edge[3]))

    #nx.draw_circular(graph)
    nx.draw_kamada_kawai(graph, with_labels=False, node_size=300)
    #nx.draw_networkx(graph)
    
    plt.savefig("graph.png")
    plt.show()

# =============================================================================    
# schreibt die Inhalte aus nodes[] und edges[] in per suffix definierte CSV        
# condensed Edges werden autom. befüllt geschrieben, gleichen also uncondensed Edges
        
def writeDataCSV(data, path, header):
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        print("schreibe .. " + csvfile.name)
        writer.writerow(header)
        for line in data:
            writer.writerow(line)
            
# =============================================================================    
# liest gegebene CSV ein und gibt data[] zurück
# bei großen Datenmengen viel performanter, als die XML erneut zu parsen

def readDataCSV(path):
    with open(path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        print("lese .. " + csvfile.name + " - header: " + str(header))
        data = list()
        if header[1] == 'lang':
            # Zeile: user, {dict language via ast}, type
            data = [[row[0], ast.literal_eval(row[1]), row[2]] for row in reader]
        else:
            data = [row for row in reader]
        return data

# =============================================================================    
# NB: NACH deleteSingleArticle ausführen
# Ermittelt edges mit gleicher Relation und fügt diese zusammen
# Prüft das Ziel der Edges und entfernt Edges ohne passenden Artikel
# edges { user, article, timestamp, id } zu [user, article, [timestamps], [ids]]
                
def condenseEdges(nodes, edges):
    edges_condensed = list()
    print('fasse parallele edges zusammen ..')
    articles = [name for [name, lang, type] in nodes if type == 'article']
    for edge in edges:
        if edge[1] in articles:
            # Duplikate via user-article-Relation ermitteln
            duplicates = [[user, article, timestamp, nodeid] for 
                          [user, article, timestamp, nodeid] in 
                          edges if user == edge[0] and article == edge[1]]    
            # alle Timestamps aus Duplikaten ermitteln
                # NB Timestamp und ID werden unzusammenhängend ausgelesen -> da Listen aber sortiert sind, ist das kein Problem
            timestamps = [timestamp for 
                          [user, article, timestamp, nodeid] in duplicates]
            # alle IDs aus Duplikat ermitteln
            ids = [nodeid for [user, article, timestamp, nodeid] in duplicates]
            # condensed sind urspr. User und Artikel, sowie Timestamp und ID als []
            condensed = [duplicates[0][0], duplicates[0][1], timestamps, ids]
            # Duplikatsprüfung vor append
            if condensed not in edges_condensed:
                edges_condensed.append(condensed)
    return edges_condensed
    
# =============================================================================    
# NB: Vor condenseEdges ausführen
# 
    
def deleteArticlesByCount(nodes, edges, versionCount = 1, userCount = 1):
    nodes_reduced = nodes.copy()
    # articles aus nodes ermitteln (vollständiges item ist nötig zum entfernen)
    articles = [[name, lang, type] for [name, lang, type] in nodes if type == 'article']
    print('article mit <= ' + str(versionCount) + ' Referenzen und <= ' + str(userCount) + ' beteiligten Usern werden entfernt ..')
    # für jeden article die Referenzen in edges prüfen
    for item in articles:
        mentions = [user for [user, article, timestamp, id] in edges if article == item[0]]
        # Zahl mentions prüfen, Zahl unique (weil Set) mentions prüfen
        if len(mentions) <= versionCount or len(set(mentions)) <= userCount:        
            nodes_reduced.remove(item)
    return nodes_reduced

# =============================================================================

def computeLanguage(nodes, edges):
    # alle artikel mit zugehöriger Sprache ermitteln
    articles = [[name, lang] for [name, lang, type] in nodes if type == 'article']
    for node in nodes:
        if node[2] == 'user':
            # alle article des aktuellen users ermitteln
            edits = [article for [user, article, timestamp, id] in edges if user == node[0]]
            # alle Sprachen der articles ermitteln
            languages = [lang for [name, lang] in articles if name in edits]
            # Sprachen des aktuellen Users ermitteln            
            en = node[1].get('en', 0)
            zh = node[1].get('zh', 0)
            # und mit den Sprachen aus den articles aufsummieren
            for item in languages:
                en += item.get('en', 0)
                zh += item.get('zh', 0)
            # neue Sprachsummen setzen
            node[1] = {'en': en, 'zh': zh}
            
# =============================================================================
            
def langColor(langdict):
    langvalue = langdict.get('en', 0) / (langdict.get('en', 0) + langdict.get('zh', 0))
    if langvalue > 0.66:
        return "blue"
    elif langvalue <= 0.66 and langvalue > 0.33:
        return "yellow"
    elif langvalue <= 0.33:
        return "red"
    else:
        return "white"
    
# =============================================================================
    
nodes = list()
edges = list()

# Articles Abrufen und als XML speichern. NB Limit anpassen
## en article
#addArticleData(nodes, edges, getXMLdata('https://en.wikipedia.org/w/index.php?title=1989_Tiananmen_Square_protests&action=history&limit=500', 'history.xsl'))
#addArticleData(nodes, edges, getXMLdata('https://en.wikipedia.org/w/index.php?title=Hong_Kong&action=history&limit=500', 'history.xsl'))
### zh article
#addArticleData(nodes, edges, getXMLdata('https://zh.wikipedia.org/w/index.php?title=%E5%85%AD%E5%9B%9B%E4%BA%8B%E4%BB%B6&action=history&limit=500', 'history.xsl'))
#addArticleData(nodes, edges, getXMLdata('https://zh.wikipedia.org/w/index.php?title=%E9%A6%99%E6%B8%AF&action=history&limit=500', 'history.xsl'))
##
### zugehörige user-netzwerke ermitteln
#for node in nodes:
#    if node[2] == "user":
#        # Aufruf je Sprachversion, NB &target=USERNAME muss als letztes Element notiert sein (sonst liefert das Schema nichts)
#        addUserData(nodes, edges, getXMLdata('https://en.wikipedia.org/w/index.php?title=Special:Contributions&limit=100&target=' + node[0], 'user.xsl'))
#        addUserData(nodes, edges, getXMLdata('https://zh.wikipedia.org/w/index.php?title=Special:用户贡献&limit=100&target=' + node[0], 'user.xsl'))

nodes = readDataCSV("nodes_4-500-100.csv")
edges = readDataCSV("edges_4-500-100.csv")

computeLanguage(nodes, edges)
nodes_reduced = deleteArticlesByCount(nodes, edges)
edges_condensed = condenseEdges(nodes_reduced, edges)

#writeDataCSV(nodes, "nodes_4-500-100.csv", ["name", "lang", "type"])
#writeDataCSV(edges, "edges_4-500-100.csv", ["user", "article", "timestamp", "id"])

#createNetxNetwork(nodes_reduced, edges_condensed)
createPyvisNetwork(nodes_reduced, edges_condensed)


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








