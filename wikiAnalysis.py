#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
"""Visualisiert Daten aus userNetwork.py
@author:  Stefan Krug
@license: CC BY 3.0 DE 
"""

import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network

from usernetwork import UserNetwork

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
            netGraph.add_node(node[0], shape="dot", size=80)#, color = langColor(node[1]))
        elif node[2] == "article":
            netGraph.add_node(node[0], shape="star", size=100, title = node[0])#, color = langColor(node[1]))
        elif node[2] == "language":
            netGraph.add_node(node[0], shape="triangle", size=100, mass=200, title = node[0])
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
            
#def langColor(langdict):
#    langvalue = langdict.get('en', 0) / (langdict.get('en', 0) + langdict.get('zh', 0))
#    if langvalue > 0.66:
#        return "blue"
#    elif langvalue <= 0.66 and langvalue > 0.33:
#        return "yellow"
#    elif langvalue <= 0.33:
#        return "red"
#    else:
#        return "white"
#    

# =============================================================================  

nodes = list()
edges = list()

network = UserNetwork()
network.add_article_data("https://en.wikipedia.org/w/index.php?title=Coronavirus_disease_2019&offset=&limit=500&action=history")

#
#nodes = un.readDataCSV("nodes_covid_500.csv")
#edges = un.readDataCSV("edges_covid_500.csv")
#
#un.computeLanguage(nodes, edges)
#un.createLanguageEdges(nodes, edges)
#
#nodes_reduced = un.deleteArticlesByCount(nodes, edges, 1, 100)
#edges_condensed = un.condenseEdges(nodes_reduced, edges)
#
#un.writeDataCSV(nodes, "nodes_covid_500_gephi.csv", ["id", "lang", "type"])
#un.writeDataCSV(edges, "edges_covid_500_gephi.csv", ["source", "target", "timestamp", "id"])
#
##createPyvisNetwork(nodes_reduced, edges_condensed)
#
















# Articles Abrufen und als XML speichern. NB Limit anpassen
## en article
#addArticleData(nodes, edges, getXMLdata('https://en.wikipedia.org/w/index.php?title=Coronavirus_disease_2019&offset=&limit=500&action=history', 'history.xsl'))
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
#

#addUserContributions(nodes, edges)
#
#writeDataCSV(nodes, "nodes_covid_500.csv", ["id", "lang", "type"])
#writeDataCSV(edges, "edges_covid_500.csv", ["source", "target", "timestamp", "id"])
#
###)
##
#writeDataCSV(nodes_reduced, "nodes_red_covid_500.csv", ["id", "lang", "type"])
#writeDataCSV(edges_condensed, "edges_red_covid_500.csv", ["source", "target", "timestamp", "id"])
#

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




















