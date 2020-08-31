#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
"""Visualisiert Daten aus usernetwork.py
@author:  Stefan Krug
@license: CC BY 3.0 DE 
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from pyvis.network import Network
from datetime import datetime
from usernetwork import UserNetwork

# =============================================================================    
# Visualisierung über Pyvis, browserbasiert, physics
                
def create_pyvis_network(nodes, edges, highlight = ""):
    """
    
    highlight:
        Erwartet einen Language Key ("en") und färbt den entsprechenden Node rot. Default "".
    """
    ## Graph anlegen   
    netGraph = Network(height='750pt', width='100%', bgcolor="#ffffff", font_color="black")
    print("erzeuge Graph ..")
    # Daten in Graph eintragen                   
    #netGraph.add_nodes([name for [name, lang, type] in nodes if type == "user"])
    for node in nodes:
        if node[2] == "user":
            netGraph.add_node(node[0], shape="dot", size=75)#, color = langColor(node[1]))
        elif node[2] == "article":
            if node[0] == highlight:
                netGraph.add_node(node[0], shape="star", size=100, title = node[0], color ="red")
            else:
                netGraph.add_node(node[0], shape="star", size=100, title = node[0])#, color = langColor(node[1]))
        elif node[2] == "language":
            if node[0] == highlight:
                netGraph.add_node(node[0], shape="square", size=100, mass=30, title = node[0], color ="red")
            else:
                netGraph.add_node(node[0], shape="square", size=100, mass=30, title = node[0])
    print('füge edges hinzu ..')
    for edge in edges:
        # die Anzahl der Versionen dient als Indikator für die Stärke der edge    
        if edge[3] is not None:
            netGraph.add_edge(edge[0], edge[1], value=2*len(edge[3]))
        else:            
            netGraph.add_edge(edge[0], edge[1], value=1)
    netGraph.barnes_hut()
    netGraph.show('networkmap.html')        

# =============================================================================  
# Visualisierung über Networkx, minimalistisch
    
def create_netx_network(nodes, edges):  
    graph = nx.Graph()
    plt.rcParams["figure.figsize"] = (19, 15)
    print('erzeuge Graph ..')
    graph.add_nodes_from([name for [name, lang, type] in nodes])
    for edge in edges:        
        graph.add_edge(edge[0], edge[1], weight=2*(len(edge[3])))

    #nx.draw_circular(graph)
    nx.draw_kamada_kawai(graph, with_labels=True, node_size=300)
    #nx.draw_networkx(graph)
    
    plt.savefig("graph.png")
    plt.show()

# =============================================================================
# Visualisierung Zeitserie nach Sprachgruppen

def plot_stuff():
    # https://www.youtube.com/watch?v=nKxLfUrkLE8
    zh = [21, 19, 20, 18, 30, 35, 19, 20]
    en = [30, 32, 31, 33, 21, 16, 32, 31]
    version = [1, 2, 3, 4, 5, 6, 7, 8]
    
    #width = 0.3
    
    #lang_indexes = np.arrange(len( ))
    
    plt.bar(version, zh, color="yellow", label="zh")
    plt.bar(version, en, color='blue', label="en")
    plt.legend()
    plt.title("Sprachverteilung nach Version")
    plt.xlabel("Versionsnummer")
    plt.ylabel("Sprachhäufigkeit")
    
# =============================================================================

#plot_stuff()

#usrntwrk_zh1 = UserNetwork()
#usrntwrk_zh2 = UserNetwork()
##usrntwrk = UserNetwork()
##usrntwrk.add_usercontributions(depth="500", users = ['Robertiki', 'Rayukk'])
#
## tiananmen massaker
#usrntwrk_zh.add_article_data("https://zh.wikipedia.org/w/index.php?title=六四事件&action=history&limit=6577")
#usrntwrk_en.add_article_data("https://en.wikipedia.org/w/index.php?title=1989_Tiananmen_Square_protests&action=history&limit=9452")
#
#usrntwrk_zh.add_usercontributions("10")
#usrntwrk_en.add_usercontributions("10")

#usrntwrk_zh.write_csv("_zh0_6576_cont10")

usrntwrk_zh1 = UserNetwork()
usrntwrk_zh2 = UserNetwork()
usrntwrk_case2 = UserNetwork()
usrntwrk_zh1.add_article_data("https://zh.wikipedia.org/w/index.php?title=六四事件&action=history&limit=6577")
usrntwrk_zh1.add_usercontributions("10000")
usrntwrk_zh1.write_csv("_zh0_6577_cont10k")
#usrntwrk_zh2.read_csv("_zh0_6577_cont10k")
#usrntwrk_zh1.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1")
#usrntwrk_zh2.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2")
#zh1 = usrntwrk_zh1.return_interval(datetime(2011, 3, 1), datetime(2014, 10, 31))
#zh2 = usrntwrk_zh2.return_interval(datetime(2015, 5, 1), datetime(2020, 8, 31))
#usrntwrk_case2.nodes = zh1[0]
#usrntwrk_case2.edges = zh1[1]
#usrntwrk_case2.nodes = zh2[0]
#usrntwrk_case2.edges = zh2[1]
#usrntwrk_case2.write_csv("_Fall2b_zh1_zh2")
#create_pyvis_network(usrntwrk_case2.nodes, usrntwrk_case2.edges, "zh1")

#usrntwrk_zh1.read_csv("_zh0_6576")
#usrntwrk_zh2.read_csv("_zh0_6576")

#usrntwrk_zh1.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1")
#usrntwrk_zh2.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2")

#2010-2014
#zh1 = usrntwrk_zh.return_interval(datetime(2010, 1, 1), datetime(2014,12,31))
#2016-2020


#usrntwrk_en.write_csv("_en0_9452_cont10")
#usrntwrk_en.read_csv("_zh0_6576")

#interval = usrntwrk_tiananmen.return_interval(datetime(2010,1,1), datetime(2015,1,1))

#usrntwrk_combined = UserNetwork()

#usrntwrk_combined.nodes = usrntwrk_zh.nodes

#usrntwrk_combined.edges = usrntwrk_zh.edges

#usrntwrk_combined.delete_nodes_by_count(edgeCount = 2, user = False)
#usrntwrk_combined.condense_edges()
#usrntwrk_combined.compute_language()
#usrntwrk_combined.create_language_network()


#
#usrntwrk_combined.write_csv("_Fall2_zh1_zh2_16028_cont2")
#usrntwrk_combined.read_csv("_Fall1b_en0_zh0_16028_cont10")
#usrntwrk_combined.delete_nodes_by_count(edgeCount = 10, user = False)
#usrntwrk_combined.condense_edges()
#usrntwrk_combined.compute_language()
#usrntwrk_combined.create_language_network()
#
#create_pyvis_network(usrntwrk_combined.nodes, usrntwrk_combined.edges, "zh")

#create_pyvis_network(usrntwrk.nodes, usrntwrk.edges)

#create_netx_network(usrntwrk.nodes, usrntwrk.edges)










