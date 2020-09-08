#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
"""Visualisiert Daten aus usernetwork.py
@author:  Stefan Krug
@license: CC BY 3.0 DE 
"""

#import matplotlib.pyplot as plt
#import networkx as nx
#import numpy as np

from pyvis.network import Network
from datetime import datetime
from usernetwork import UserNetwork

# =============================================================================    
# Visualisierung über Pyvis, browserbasiert, physics
                
def create_pyvis_network(nodes, edges, highlight = ""):
    """
    
    highlight:
        Erwartet einen Language Key ("en") oder artikelnamen und färbt den entsprechenden Node rot. Default "".
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
                netGraph.add_node(node[0], shape="square", size=100, mass=20, title = node[0], color ="red")
            else:
                netGraph.add_node(node[0], shape="square", size=100, mass=20, title = node[0])
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
    
#def create_netx_network(nodes, edges):  
#    graph = nx.Graph()
#    plt.rcParams["figure.figsize"] = (19, 15)
#    print('erzeuge Graph ..')
#    graph.add_nodes_from([name for [name, lang, type] in nodes])
#    for edge in edges:        
#        graph.add_edge(edge[0], edge[1], weight=2*(len(edge[3])))
#
#    #nx.draw_circular(graph)
#    nx.draw_kamada_kawai(graph, with_labels=True, node_size=300)
#    #nx.draw_networkx(graph)
#    
#    plt.savefig("graph.png")
#    plt.show()

# =============================================================================
# Visualisierung Zeitserie nach Sprachgruppen

#def plot_stuff():
#    # https://www.youtube.com/watch?v=nKxLfUrkLE8
#    zh = [21, 19, 20, 18, 30, 35, 19, 20]
#    en = [30, 32, 31, 33, 21, 16, 32, 31]
#    version = [1, 2, 3, 4, 5, 6, 7, 8]
#    
#    #width = 0.3
#    
#    #lang_indexes = np.arrange(len( ))
#    
#    plt.bar(version, zh, color="yellow", label="zh")
#    plt.bar(version, en, color='blue', label="en")
#    plt.legend()
#    plt.title("Sprachverteilung nach Version")
#    plt.xlabel("Versionsnummer")
#    plt.ylabel("Sprachhäufigkeit")
    
# =============================================================================

#plot_stuff()

#usrntwrk_en1 = UserNetwork()
#usrntwrk_en2 = UserNetwork()
###usrntwrk.add_usercontributions(depth="500", users = ['Robertiki', 'Rayukk'])
##
### tiananmen massaker
##usrntwrk_zh.add_article_data("https://zh.wikipedia.org/w/index.php?title=六四事件&action=history&limit=6577")
#usrntwrk_en1.add_article_data("https://en.wikipedia.org/w/index.php?title=1989_Tiananmen_Square_protests&action=history&offset=20090619000000limit=300")
#usrntwrk_en1.add_usercontributions("10", "20090619000000")
#usrntwrk_en1.write_csv("_en1_300_cont10")
#
#usrntwrk_en2.add_article_data("https://en.wikipedia.org/w/index.php?title=1989_Tiananmen_Square_protests&action=history&offset=20190619000000limit=200")
#usrntwrk_en2.add_usercontributions("10", "20190619000000")
#usrntwrk_en2.write_csv("_en2_200_cont10")
#
##
#usrntwrk_zh.add_usercontributions("10")
#usrntwrk_en.add_usercontributions("10")

#usrntwrk_zh.write_csv("_zh0_6576_cont10")

#usrntwrk_zh2 = UserNetwork()
#usrntwrk_case2 = UserNetwork()
#usrntwrk_zh1.add_article_data("https://zh.wikipedia.org/w/index.php?title=六四事件&action=history&limit=6577")
#usrntwrk_zh1.add_usercontributions("10000")
#usrntwrk_zh1.write_csv("_zh0_6577_cont10k")

#### ===========================================================================
#""" Fall 2b, Aufbereitung und Visualisierung """
#usrntwrk_zh1 = UserNetwork()
#usrntwrk_zh1.read_csv("_zh1_1300_cont10")
#usrntwrk_zh1.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1a")
#    
#usrntwrk_zh2 = UserNetwork()
#usrntwrk_zh2.read_csv("_zh2_1330_cont10")
#usrntwrk_zh2.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2")
#
    #obacht
#zh1 = usrntwrk_zh1.return_interval(datetime(2011, 3, 1), datetime(2012, 12, 31))
#zh2 = usrntwrk_zh2.return_interval(datetime(2015, 5, 1), datetime(2020, 8, 31))
#
#usrntwrk_case2 = UserNetwork()
#usrntwrk_case2.nodes = zh1[0]
#usrntwrk_case2.edges = zh1[1]
#usrntwrk_case2.nodes = zh2[0]
#usrntwrk_case2.edges = zh2[1]
#usrntwrk_case2.write_csv("_Fall2b_zh1_zh2")
#
#usrntwrk_case2.compute_language()
#usrntwrk_case2.delete_nodes_by_count(edgeCount = 10, user = False)
#usrntwrk_case2.condense_edges()
#usrntwrk_case2.create_language_network()
#
#create_pyvis_network(usrntwrk_case2.nodes, usrntwrk_case2.edges, "zh")
#### ===========================================================================

#### ===========================================================================
#""" Fall 2c, Aufbereitung und Visualisierung """
#usrntwrk_zh1a = UserNetwork()
#usrntwrk_zh1a.read_csv("_zh1_1300_cont10")
#usrntwrk_zh1a.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1a")
#    
#usrntwrk_zh1b = UserNetwork()
#usrntwrk_zh1b.read_csv("_zh1_1300_cont10")
#usrntwrk_zh1b.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1b")
#
#zh1a = usrntwrk_zh1a.return_interval(datetime(2011, 3, 1), datetime(2012, 12, 31))
#zh1b = usrntwrk_zh1b.return_interval(datetime(2013, 1, 1), datetime(2014, 10, 31))
#
#usrntwrk_case2 = UserNetwork()
#usrntwrk_case2.nodes = zh1a[0]
#usrntwrk_case2.edges = zh1a[1]
#usrntwrk_case2.nodes = zh1b[0]
#usrntwrk_case2.edges = zh1b[1]
#usrntwrk_case2.write_csv("_Fall2c_zh1a_zh1b")
#
#usrntwrk_case2.compute_language()
#usrntwrk_case2.delete_nodes_by_count(edgeCount = 10, user = False)
#usrntwrk_case2.condense_edges()
#usrntwrk_case2.create_language_network()
#
#create_pyvis_network(usrntwrk_case2.nodes, usrntwrk_case2.edges, "zh")
#### ===========================================================================

#### ===========================================================================
#""" Fall 2d, Aufbereitung und Visualisierung """
#usrntwrk_zh2a = UserNetwork()
#usrntwrk_zh2a.read_csv("_zh2_1330_cont10")
#usrntwrk_zh2a.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2a")
#    
#usrntwrk_zh2b = UserNetwork()
#usrntwrk_zh2b.read_csv("_zh2_1330_cont10")
#usrntwrk_zh2b.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2b")
#
#zh2a = usrntwrk_zh2a.return_interval(datetime(2015, 5, 1), datetime(2017, 12, 31))
#zh2b = usrntwrk_zh2b.return_interval(datetime(2018, 1, 1), datetime(2020, 8, 31))
#
#usrntwrk_case2 = UserNetwork()
#usrntwrk_case2.nodes = zh2a[0]
#usrntwrk_case2.edges = zh2a[1]
#usrntwrk_case2.nodes = zh2b[0]
#usrntwrk_case2.edges = zh2b[1]
#usrntwrk_case2.write_csv("_Fall2d_zh2a_zh2b")
#
#usrntwrk_case2.compute_language()
#usrntwrk_case2.delete_nodes_by_count(edgeCount = 10, user = False)
#usrntwrk_case2.condense_edges()
#usrntwrk_case2.create_language_network()
#
#create_pyvis_network(usrntwrk_case2.nodes, usrntwrk_case2.edges, "zh")
#### ===========================================================================

#### ===========================================================================
#""" Fall 3a, Aufbereitung und Visualisierung """
#usrntwrk_en1 = UserNetwork()
#usrntwrk_en1.read_csv("_en1_300_cont10")
#usrntwrk_en1.modify_nodename("1989 Tiananmen Square protests", "en1")
#
#usrntwrk_en2 = UserNetwork()
#usrntwrk_en2.read_csv("_en2_200_cont10")
#usrntwrk_en2.modify_nodename("1989 Tiananmen Square protests", "en2")
#    
#usrntwrk_zh1 = UserNetwork()
#usrntwrk_zh1.read_csv("_zh1_1300_cont10")
#usrntwrk_zh1.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1")
#
#en1 = usrntwrk_en1.return_interval(datetime(2009, 5, 21), datetime(2009, 6, 18))
#en2 = usrntwrk_en2.return_interval(datetime(2019, 5, 21), datetime(2019, 6, 18))
#zh1 = usrntwrk_zh1.return_interval(datetime(2011, 3, 1), datetime(2014, 10, 31))
#
#usrntwrk_case3 = UserNetwork()
#usrntwrk_case3.nodes = en1[0]
#usrntwrk_case3.edges = en1[1]
#usrntwrk_case3.nodes = en2[0]
#usrntwrk_case3.edges = en2[1]
#usrntwrk_case3.nodes = zh1[0]
#usrntwrk_case3.edges = zh1[1]
#usrntwrk_case3.write_csv("_Fall3a_zh1_en1_en2")
#
#usrntwrk_case3.compute_language()
#usrntwrk_case3.delete_nodes_by_count(edgeCount = 10, user = False)
#usrntwrk_case3.condense_edges()
#usrntwrk_case3._check_integrity(True)
##usrntwrk_case3.create_language_network()
#
#create_pyvis_network(usrntwrk_case3.nodes, usrntwrk_case3.edges, "zh")
#### ===========================================================================

#### ===========================================================================
#""" Fall 3b, Aufbereitung und Visualisierung """
usrntwrk_en1 = UserNetwork()
usrntwrk_en1.read_csv("_en1_300_cont10")
usrntwrk_en1.modify_nodename("1989 Tiananmen Square protests", "en1")

usrntwrk_en2 = UserNetwork()
usrntwrk_en2.read_csv("_en2_200_cont10")
usrntwrk_en2.modify_nodename("1989 Tiananmen Square protests", "en2")
    
usrntwrk_zh2 = UserNetwork()
usrntwrk_zh2.read_csv("_zh2_1330_cont10")
usrntwrk_zh2.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2")

en1 = usrntwrk_en1.return_interval(datetime(2009, 5, 21), datetime(2009, 6, 18))
en2 = usrntwrk_en2.return_interval(datetime(2019, 5, 21), datetime(2019, 6, 18))
zh2 = usrntwrk_zh2.return_interval(datetime(2015, 5, 1), datetime(2020, 8, 31))

usrntwrk_case3 = UserNetwork()
usrntwrk_case3.nodes = en1[0]
usrntwrk_case3.edges = en1[1]
usrntwrk_case3.nodes = en2[0]
usrntwrk_case3.edges = en2[1]
usrntwrk_case3.nodes = zh2[0]
usrntwrk_case3.edges = zh2[1]
usrntwrk_case3.write_csv("_Fall3b_zh2_en1_en2")

usrntwrk_case3.compute_language()
usrntwrk_case3.delete_nodes_by_count(edgeCount = 10, user = False)
usrntwrk_case3.condense_edges()
usrntwrk_case3._check_integrity(True)
#usrntwrk_case3.create_language_network()

create_pyvis_network(usrntwrk_case3.nodes, usrntwrk_case3.edges, "zh")
#### ===========================================================================

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




#create_pyvis_network(usrntwrk.nodes, usrntwrk.edges)

#create_netx_network(usrntwrk.nodes, usrntwrk.edges)










