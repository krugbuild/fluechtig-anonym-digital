#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
"""Fallimplementation zu usernetwork.py
@author:  Alexandra Krug
@license: CC BY 3.0 DE 
"""

from pyvis.network import Network
from datetime import datetime
from usernetwork import UserNetwork

# =============================================================================    
# Helper: Visualisierung über Pyvis, browserbasiert, physics
                
def create_pyvis_network(nodes, edges, highlight = ""):
    """
    Ruft die pyvis-Visualisierung für einen Übergebenen Datensatz auf.
    nodes:
        Liste mit Knotenpunkten.
    edges:
        Liste mit Relationen.
    highlight:
        Erwartet einen Language Key ("en") oder artikelnamen und färbt den entsprechenden Node rot. Default "".
    """
    ## Graph anlegen   
    netGraph = Network(height='750pt', width='100%', bgcolor="#ffffff", font_color="black")
    print("erzeuge Graph ..")
    # Daten in Graph eintragen                   
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

#### ===========================================================================
def case_1a():
    """ Fall 1a, Aufbereitung und Visualisierung """
    usrntwrk_case1 = UserNetwork()

    usrntwrk_case1.read_csv("_zh0_6577")
    usrntwrk_case1.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh0")
        
    usrntwrk_case1.read_csv("_en0_9452")
    usrntwrk_case1.modify_nodename("1989 Tiananmen Square protests", "en0")
    
    usrntwrk_case1.compute_language()
    usrntwrk_case1.delete_nodes_by_count(edgeCount = 10, user = False)
    usrntwrk_case1.condense_edges()
    usrntwrk_case1.write_csv("_Fall1a_en0_zh0")
    
    create_pyvis_network(usrntwrk_case1.nodes, usrntwrk_case1.edges, "zh")
    
    return (usrntwrk_case1)
##### ===========================================================================

#### ===========================================================================
def case_1b():
    """ Fall 1b, Aufbereitung und Visualisierung """
    usrntwrk_case1 = UserNetwork()

    usrntwrk_case1.read_csv("_zh0_6577_cont10")
    usrntwrk_case1.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh0")
        
    usrntwrk_case1.read_csv("_en0_9452_cont10")
    usrntwrk_case1.modify_nodename("1989 Tiananmen Square protests", "en0")
    
    usrntwrk_case1.compute_language()
    usrntwrk_case1.delete_nodes_by_count(edgeCount = 10, user = False)
    usrntwrk_case1.condense_edges()
    usrntwrk_case1.write_csv("_Fall1a_en0_zh0")
    usrntwrk_case1.create_language_network()
    
    create_pyvis_network(usrntwrk_case1.nodes, usrntwrk_case1.edges, "zh")
    
    return (usrntwrk_case1)
##### ===========================================================================

#### ===========================================================================
def case_2b():
    """ Fall 2b, Aufbereitung und Visualisierung """
    usrntwrk_zh1 = UserNetwork()
    usrntwrk_zh1.read_csv("_zh1_1300_cont10")
    usrntwrk_zh1.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1")
        
    usrntwrk_zh2 = UserNetwork()
    usrntwrk_zh2.read_csv("_zh2_1330_cont10")
    usrntwrk_zh2.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2")
    
    zh1 = usrntwrk_zh1.return_interval(datetime(2011, 3, 1), datetime(2014, 10, 31))
    zh2 = usrntwrk_zh2.return_interval(datetime(2015, 5, 1), datetime(2020, 8, 31))
    
    usrntwrk_case2 = UserNetwork()
    usrntwrk_case2.nodes = zh1[0]
    usrntwrk_case2.edges = zh1[1]
    usrntwrk_case2.nodes = zh2[0]
    usrntwrk_case2.edges = zh2[1]
    usrntwrk_case2.write_csv("_Fall2b_zh1_zh2")
    
    usrntwrk_case2.compute_language()
    usrntwrk_case2.delete_nodes_by_count(edgeCount = 10, user = False)
    usrntwrk_case2.condense_edges()
    usrntwrk_case2.create_language_network()
    
    create_pyvis_network(usrntwrk_case2.nodes, usrntwrk_case2.edges, "zh")
    
    return (usrntwrk_case2)
##### ===========================================================================

#### ===========================================================================
def case_2c():
    """ Fall 2c, Aufbereitung und Visualisierung """
    usrntwrk_zh1a = UserNetwork()
    usrntwrk_zh1a.read_csv("_zh1_1300_cont10")
    usrntwrk_zh1a.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1a")
        
    usrntwrk_zh1b = UserNetwork()
    usrntwrk_zh1b.read_csv("_zh1_1300_cont10")
    usrntwrk_zh1b.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1b")
    
    zh1a = usrntwrk_zh1a.return_interval(datetime(2011, 3, 1), datetime(2012, 12, 31))
    zh1b = usrntwrk_zh1b.return_interval(datetime(2013, 1, 1), datetime(2014, 10, 31))
    
    usrntwrk_case2 = UserNetwork()
    usrntwrk_case2.nodes = zh1a[0]
    usrntwrk_case2.edges = zh1a[1]
    usrntwrk_case2.nodes = zh1b[0]
    usrntwrk_case2.edges = zh1b[1]
    usrntwrk_case2.write_csv("_Fall2c_zh1a_zh1b")
    
    usrntwrk_case2.compute_language()
    usrntwrk_case2.delete_nodes_by_count(edgeCount = 10, user = False)
    usrntwrk_case2.condense_edges()
    usrntwrk_case2.create_language_network()
    
    create_pyvis_network(usrntwrk_case2.nodes, usrntwrk_case2.edges, "zh")
    
    return (usrntwrk_case2)
#### ===========================================================================

#### ===========================================================================
def case_2d():
    """ Fall 2d, Aufbereitung und Visualisierung """
#    usrntwrk_zh2a = UserNetwork()
#    usrntwrk_zh2a.read_csv("_zh2_1330_cont10")
#    usrntwrk_zh2a.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2a")
#        
#    usrntwrk_zh2b = UserNetwork()
#    usrntwrk_zh2b.read_csv("_zh2_1330_cont10")
#    usrntwrk_zh2b.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2b")
#    
#    zh2a = usrntwrk_zh2a.return_interval(datetime(2015, 5, 1), datetime(2017, 12, 31))
#    zh2b = usrntwrk_zh2b.return_interval(datetime(2018, 1, 1), datetime(2020, 8, 31))
    
    usrntwrk_case2 = UserNetwork()
#    usrntwrk_case2.nodes = zh2a[0]
#    usrntwrk_case2.edges = zh2a[1]
#    usrntwrk_case2.nodes = zh2b[0]
#    usrntwrk_case2.edges = zh2b[1]
    usrntwrk_case2.read_csv("_Fall2d_zh2a_zh2b")
    
    usrntwrk_case2.compute_language()
    usrntwrk_case2.delete_nodes_by_count(edgeCount = 10, user = False)
    usrntwrk_case2.condense_edges()
    usrntwrk_case2.create_language_network()
    
    create_pyvis_network(usrntwrk_case2.nodes, usrntwrk_case2.edges, "zh")
    
    return (usrntwrk_case2)
#### ===========================================================================

### ===========================================================================
def case_3a():
    """ Fall 3a, Aufbereitung und Visualisierung """    
    usrntwrk_zh1b = UserNetwork()
    usrntwrk_zh1b.read_csv("_zh1_1300_cont10")
    usrntwrk_zh1b.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1b")
    
    zh1b = usrntwrk_zh1b.return_interval(datetime(2013, 1, 1), datetime(2014, 10, 31))
    
    usrntwrk_case3 = UserNetwork()
    usrntwrk_case3.nodes = zh1b[0]
    usrntwrk_case3.edges = zh1b[1]
    
    usrntwrk_case3.compute_language()
    usrntwrk_case3.delete_nodes_by_count(edgeCount = 10, user = False)
    usrntwrk_case3.condense_edges()
    usrntwrk_case3.create_language_network()
    usrntwrk_case3.write_csv("_Fall3a_zh1")
    
    create_pyvis_network(usrntwrk_case3.nodes, usrntwrk_case3.edges, "zh")
    
    return (usrntwrk_case3)
### ===========================================================================

#### ===========================================================================
def case_3b():
    """ Fall 3b, Aufbereitung und Visualisierung """    
#    usrntwrk = UserNetwork()
    
#    usrntwrk.add_usercontributions(depth="500", offset="20141101000000",
#                                   users = ['Daveduv',
#                                            'Howard61313',
#                                            'Sameboat',
#                                            'Hvn0413',
#                                            'Joradalien',
#                                            'Veritas-iustitia-libertas',
#                                            'Sinopitt',
#                                            'Gabhksw',
#                                            'Jarodalien',
#                                            'Frysun',
#                                            'Makecat',
#                                            'AddisWang',
#                                            'Iflwlou',
#                                            'Whhalbert',
#                                            'Marxistfounder',
#                                            'Huandy618',
#                                            'Whisper of the heart',
#                                            'Prosperity Horizons',
#                                            'BBCCN',
#                                            'Mys 721tx',
#                                            'MacArthur1945',
#                                            'Wildcursive',
#                                            'Dirrival',
#                                            'Bxxiaolin',
#                                            'Sinopitt',
#                                            'Sgsg',
#                                            'HYH.124',
#                                            'Cscen',
#                                            'Bencmq',
#                                            'AH829'])
#    
#    zh1b_u = usrntwrk.return_interval(datetime(2013, 1, 1), datetime(2014, 10, 31))
#    
    usrntwrk_case3 = UserNetwork()
#    usrntwrk_case3.nodes = zh1b_u[0]
#    usrntwrk_case3.edges = zh1b_u[1]
#    usrntwrk_case3.write_csv("_Fall3b_zh1b_user_500")
    usrntwrk_case3.read_csv("_Fall3b_zh1b_user_500")
    
    usrntwrk_case3.compute_language()
    usrntwrk_case3.delete_nodes_by_count(edgeCount = 4, user = False)
    usrntwrk_case3.condense_edges()
    usrntwrk_case3.create_language_network()
    
    create_pyvis_network(usrntwrk_case3.nodes, usrntwrk_case3.edges, "zh")
    
    return (usrntwrk_case3)
#### ===========================================================================

#### ===========================================================================
def case_4a():
    """ Fall 4a, Aufbereitung und Visualisierung """
    usrntwrk_en1 = UserNetwork()
    usrntwrk_en1.read_csv("_en1_300_cont10")
    usrntwrk_en1.modify_nodename("1989 Tiananmen Square protests", "en1")
    
    usrntwrk_en2 = UserNetwork()
    usrntwrk_en2.read_csv("_en2_200_cont10")
    usrntwrk_en2.modify_nodename("1989 Tiananmen Square protests", "en2")
    
    usrntwrk_en3 = UserNetwork()
    usrntwrk_en3.read_csv("_en3_80_cont10")
    usrntwrk_en3.modify_nodename("1989 Tiananmen Square protests", "en3")
        
    usrntwrk_zh1 = UserNetwork()
    usrntwrk_zh1.read_csv("_zh1_1300_cont10")
    usrntwrk_zh1.delete_nodes_by_count(edgeCount = 200)
    usrntwrk_zh1.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh1")
    
    usrntwrk_zh2 = UserNetwork()
    usrntwrk_zh2.read_csv("_zh2_1330_cont10")
    usrntwrk_zh2.delete_nodes_by_count(edgeCount = 200)
    usrntwrk_zh2.modify_nodename("“六四事件”的版本历史 - 维基百科，自由的百科全书", "zh2")
    
    en1 = usrntwrk_en1.return_interval(datetime(2009, 5, 21), datetime(2009, 6, 18))
    en2 = usrntwrk_en2.return_interval(datetime(2019, 5, 21), datetime(2019, 6, 18))
    en3 = usrntwrk_en3.return_interval(datetime(2020, 5, 21), datetime(2020, 6, 18))
    zh1 = usrntwrk_zh1.return_interval(datetime(2011, 3, 1), datetime(2014, 10, 31))
    zh2 = usrntwrk_zh2.return_interval(datetime(2015, 5, 1), datetime(2020, 8, 31))
    
    usrntwrk_case4 = UserNetwork()
    usrntwrk_case4.nodes = en1[0]
    usrntwrk_case4.edges = en1[1]
    usrntwrk_case4.nodes = en2[0]
    usrntwrk_case4.edges = en2[1]
    usrntwrk_case4.nodes = en3[0]
    usrntwrk_case4.edges = en3[1]
    usrntwrk_case4.nodes = zh1[0]
    usrntwrk_case4.edges = zh1[1]
    usrntwrk_case4.nodes = zh2[0]
    usrntwrk_case4.edges = zh2[1]
    usrntwrk_case4.write_csv("_Fall4a_zh_en")
    
    usrntwrk_case4.compute_language()
    usrntwrk_case4.delete_nodes_by_count(edgeCount = 10, user = False)
    usrntwrk_case4.condense_edges()
    usrntwrk_case4._check_integrity(True)
    
    create_pyvis_network(usrntwrk_case4.nodes, usrntwrk_case4.edges, "zh")
    
    return (usrntwrk_case4)
#### ===========================================================================

#### ===========================================================================
def case_4b():
    """ Fall 4b, Aufbereitung und Visualisierung """
    usrntwrk_en1 = UserNetwork()
    usrntwrk_en1.read_csv("_en1_300_cont10")
    usrntwrk_en1.modify_nodename("1989 Tiananmen Square protests", "en1")
    
    usrntwrk_en2 = UserNetwork()
    usrntwrk_en2.read_csv("_en2_200_cont10")
    usrntwrk_en2.modify_nodename("1989 Tiananmen Square protests", "en2")
    
    usrntwrk_en3 = UserNetwork()
    usrntwrk_en3.read_csv("_en3_80_cont10")
    usrntwrk_en3.modify_nodename("1989 Tiananmen Square protests", "en3")
    
    en1 = usrntwrk_en1.return_interval(datetime(2009, 5, 21), datetime(2009, 6, 18))
    en2 = usrntwrk_en2.return_interval(datetime(2019, 5, 21), datetime(2019, 6, 18))
    en3 = usrntwrk_en3.return_interval(datetime(2020, 5, 21), datetime(2020, 6, 18))
    
    usrntwrk_case4 = UserNetwork()
    usrntwrk_case4.nodes = en1[0]
    usrntwrk_case4.edges = en1[1]
    usrntwrk_case4.nodes = en2[0]
    usrntwrk_case4.edges = en2[1]
    usrntwrk_case4.nodes = en3[0]
    usrntwrk_case4.edges = en3[1]
    usrntwrk_case4.write_csv("_Fall4b_en1_en2_en3")
    
    usrntwrk_case4.add_usercontributions("100")
    
    usrntwrk_case4.compute_language()
    usrntwrk_case4.delete_nodes_by_count(edgeCount = 10, user = False)
    usrntwrk_case4.condense_edges()
    usrntwrk_case4._check_integrity(True)
    usrntwrk_case4.create_language_network()
    
    create_pyvis_network(usrntwrk_case4.nodes, usrntwrk_case4.edges, "zh")
    
    return (usrntwrk_case4)
#### ===========================================================================
