#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
"""Klasse zur Datenerhebung- und -verarbeitung von Usernetzwerken in Wikipedia
@author:  Stefan Krug
@license: CC BY 3.0 DE 
"""

import os.path
import csv
import ast
import requests

from lxml import etree
from urllib.parse import urlparse
from urllib.parse import unquote

class UserNetwork:
    """ Klasse zur Datenerhebung- und -verarbeitung von Usernetzwerken in 
        Wikipedia. Dient als Grundlage für Netzwerkanalysen.
        
        Exemplarischer Aufruf:
            
            Initialisierung und Abruf der letzten 500 Versionen einer Artikelhistorie:
                
            >>> usrntwrk = UserNetwork()
            >>> usrntwrk.add_article_data("https://en.wikipedia.org/w/index.php?
            title=Coronavirus_disease_2019&offset=&limit=500&action=history")
            
            Abruf der letzten 50 Edits für jeden User der abgerufenen Historie
            in allen definierten Sprachen (self.cont_languages). Zuordnung von
            Sprachen zu Nutzern und Erweiterung des Netzwerkes um Sprachknoten.
            
            >>> usrntwrk.add_usercontributions("50")
            >>> usrntwrk.compute_language()
            >>> usrntwrk.create_language_network()
            
            Entfernen aller Artikel mit weniger als 5 referenzierten Usern.
            Zusammenfassen von gleichartigen Edges (selbe Relation).
            
            >>> usrntwrk.delete_articles_by_count(userCount = 5)
            >>> usrntwrk.condense_edges()
                        
    """
    
    def __init__(self):
        """ List definition:
            
            - nodes [[ name(title/user), lang{}, type(article/user/language) ]]
            
            - edges [[ user, article, timestamp, id ]]
            
            - languages { kürzel (z.B. en) : contributions-url}
                    
                -> contribution-URLs müssen dem Schema {Kennzeichen Sprache}.wikipedia.org/w/index.php?title={Spezialseite:Beiträge nach Sprache} entsprechen
                
                -> z.B. {"en" : "https://en.wikipedia.org/w/index.php?title=Special:Contributions"}
            
                -> Auswahl entspricht TOP 10 Sprachen gem. Useraktivität auf Wikipedia
        """
        self.nodes = list()
        self.edges = list()
        self.cont_languages = { "en" : "https://en.wikipedia.org/w/index.php?title=Special:Contributions"
                               , "fr" : "https://fr.wikipedia.org/w/index.php?title=Sp%C3%A9cial:Contributions"
                               , "de" : "https://de.wikipedia.org/w/index.php?title=Spezial:Beitr%C3%A4ge"
                               , "es" : "https://es.wikipedia.org/w/index.php?title=Especial:Contribuciones"
                               , "ja" : "https://ja.wikipedia.org/w/index.php?title=特別:投稿記録"
                               , "ru" : "https://ru.wikipedia.org/w/index.php?title=Служебная%3AВклад"
                               , "it" : "https://it.wikipedia.org/w/index.php?title=Speciale:Contributi"
                               , "zh" : "https://zh.wikipedia.org/w/index.php?title=Special:用户贡献"
                               , "fa" : "https://fa.wikipedia.org/w/index.php?title=ویژه%3Aمشارکت%E2%80%8Cها"
                               , "ar" : "https://ar.wikipedia.org/w/index.php?title=خاص%3Aمساهمات"}

# =============================================================================
# HTML request & XML       
# =============================================================================
    def _get_xml_data(self, url, stylesheet):
        """ Ruft eine Seite ab und transformiert diese nach XML.
            url = parametrisierte URL der Artikelhistorie oder User contributions
            stylesheet = xslt zur Transformation der abzurufenden Daten
            return: etree-Objekt mit XML
        """
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
# CSV: read & write
# =============================================================================                
    def _write_data_csv(self, data, path, header):
        """ Schreibt die Inhalte aus data in eine CSV mit definiertem header.
            NB: Condensed Edges werden autom. aufgespalten geschrieben, gleichen
            also uncondensed Edges.
        """
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            print("schreibe .. " + csvfile.name)
            writer.writerow(header)
            for line in data:
                writer.writerow(line)
                
                
    def _read_data_csv(self, path):
        """ Liest gegebene CSV ein und gibt data[] zurück. Bei großen
            Datenmengen viel performanter, als die XML erneut zu parsen.
        """
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


    def write_csv(self, file_suffix = ""):
        """ Speichert die Inhalte von nodes[] und edges[] als CSV.
            NB: condensed Edges werden dabei aufgelöst.
            file_suffix = Kennzeichen, das den Dateinamen angehangen werden
                kann. Optional, default "". 
        """
        self._write_data_csv(self.nodes, "nodes" + file_suffix + ".csv", 
                             ["id", "lang", "type"])
        self._write_data_csv(self.edges, "edges" + file_suffix + ".csv", 
                             ["source", "target", "timestamp", "id"])
                
        
    def read_csv(self, file_suffix = ""):
        """ Liest die Inhalte von nodes[] und edges[] aus einer CSV.
            NB: condensed Edges werden nicht übernommen.
            file_suffix = Kennzeichen, zur identifikation von besonderen
            Dateien. Optional, default "". 
        """
        self.nodes = self._read_data_csv("nodes" + file_suffix + ".csv")
        self.edges = self._read_data_csv("edges" + file_suffix + ".csv")
            
# =============================================================================
# Nodes & Edges: Datenbezug        
# =============================================================================
        
    def add_article_data(self, url):
        """ Lädt eine via URL definierte Artikelhistorie der Wikipedia herunter
            oder lädt ein lokales Abbild und trägt den Artikel sowie die
            zugehörigen Benutzer in nodes[] und edges[] ein.
            
            url = Parametrisierte URL der Artikelhistorie in der Form:
                https://en.wikipedia.org/w/index.php?title=TITLE&limit=LIMIT&action=history
        """
        # article beziehen bzw. lokale Kopie laden
        article = self._get_xml_data(url, "history.xsl")
        # article-node zusammenstellen (name wird decodiert um keine %-encodings zu haben)
        article_name = unquote(article.xpath('/article/title')[0].text.rsplit(": ", 1)[0])
        article_node = [article_name # name
                        , {article.xpath('/article/language')[0].text : 1} # language
                        , 'article'] # type
        # article hinzufügen, sofern neu
        if article_node not in self.nodes:
            self.nodes.append(article_node)
            print('article added: ' + str(article_node))
        # user als nodes, versions als edges hinzufügen
        for version in article.xpath('/article/versions/version'):
            # user-node zusammenstellen (name wird decodiert um keine %-encodings zu haben)
            user_node = [unquote(version.xpath('./user')[0].text) # name
                         , {} # language
                         , 'user'] # type
            # user hinzufügen, sofern neu
            if user_node not in self.nodes:
                self.nodes.append(user_node)
                print('user added: ' + str(user_node))
            # version als edge hinzufügen
            version_edge = [user_node[0] # user
                            , article_node[0] #article
                            , version.xpath('./timestamp')[0].text # timestamp
                            , version.xpath('./id')[0].text] # version id
            if version_edge not in self.edges:
                self.edges.append(version_edge)
                
                
    def add_user_data(self, url):
        """ Lädt die via URL definierte Usercontribution der Wikipedia herunter
            oder lädt ein lokales Abbild und trägt den User sowie die
            aufgeführten Artikel in nodes[] und edges[] ein.
            
            url = Parametrisierte URL der Usercontribution in der Form:
                https://en.wikipedia.org/w/index.php?title=Special:Contributions&limit={LIMIT}&target={USER}
            
                NB: &target=USER muss unbedingt als letztes Element notiert werden!
        """
        # article beziehen bzw. lokale Kopie laden
        user = self._get_xml_data(url, "user.xsl")
        # user-node zusammenstellen
        user_node = [unquote(user.xpath('/user/name')[0].text) #name
                     , {} #language
                     , 'user'] #type
        # user hinzufügen, sofern neu
        if user_node not in self.nodes:
            self.nodes.append(user_node)
            print('user added: ' + str(user_node))
        # articles als nodes, versions als edges hinzufügen
        if user.xpath('/user/versions/version') is not None:
            for version in user.xpath('/user/versions/version'):
                # article-node zusammenstellen (name wird decodiert -> Einheitlichkeit)
                article_node = [unquote(version.xpath('./title')[0].text) #name
                                , {user.xpath('/user/language')[0].text : 1} # lang: bessere quelle haben wir aktuell nicht
                                , 'article'] # type
                # article hinzufügen, sofern neu
                if article_node not in self.nodes:
                    self.nodes.append(article_node)
                    print('article added: ' + str(article_node))
                # version als edge hinzufügen
                version_edge = [user_node[0] # user 
                                , article_node[0] # article
                                , version.xpath('./timestamp')[0].text #timestamp
                                , version.xpath('./id')[0].text] #version id
                if version_edge not in self.edges:
                    self.edges.append(version_edge)
    
    
    def add_usercontributions(self, depth = "100"):
        """ Fügt für alle User des aktuellen Netzwerkes für alle definierten 
            Sprachen (self.cont_languages) die User-Contributions als Nodes 
            hinzu und verknüpft diese mit dem User.
            Dient der Ermittlung der User-Sprachen über die Contributions und
            zur Sichtbarmachung eventueller Contributionnetzwerke.
            depth = Anzahl an Einträgen je Contribution die geladen werden soll.
                default = 100
        """
        for node in self.nodes:
            if node[2] == "user":
                print("ermittle Artikel für User " + node[0] + " ..")
                for cont in self.cont_languages.items():
                    # Aufruf je Sprachversion, NB &target=USERNAME muss als letztes 
                    # .. Element notiert sein (sonst liefert das Schema nichts)
                    self.add_user_data(cont[1] + '&limit=' + depth + '&target=' + node[0])
    
# =============================================================================    
# Nodes & Edges: Datenmanipulation         
# =============================================================================          
            
    def compute_language(self):
        """ Ermittelt über die User Contributions die Sprachen und deren
            absolute Häufigkeit je User.
            
            potentieller Parameter: unique 
                -> nur unteschiedl. Artikel zählen
        """
        # aus nodes[] _alle_ Artikel und deren Sprache (z.B. {"en":1}) auflisten
        articles = [[name, lang] for [name, lang, type] in self.nodes if type == 'article']
        for node in self.nodes:
            if node[2] == 'user':
                # alle Artikel-User-Relationen für den aktuellen User aus edges[] auslesen
                edits = [article for [user, article, timestamp, id] in self.edges if user == node[0]]
                # für die ermittelten Artikel die Sprache{} ermitteln
                # languages ist also: [{},]
                languages = [lang for [name, lang] in articles if name in edits]
                # node[1] = Sprachen, sollte bei einem User ein leeres dict sein
                if type(node[1]) != type(dict()):
                    node[1] = dict()
                # für jedes {} in languages wird dessen wert 
                for item in languages:
                    # je item wird jeder bekannte Sprachkey geprüft
                    for lang in self.cont_languages.keys():
                        # je Sprachkey wird der Wert aus item abgerufen und im node aufaddiert
                        if lang in node[1].keys():
                            node[1][lang] += item.get(lang, 0)
                        else:
                            node[1].update({lang: item.get(lang, 0)})
                                    
# =============================================================================    
# Nodes & Edges: Netzwerkmanipulation       
# =============================================================================
                    
    def create_language_network(self, artcl_also = False):
        """ Erzeugt Nodes für alle definierten Sprachen (self.languages) und
            verknüpft diese mit Usern und ggf. mit Artiklen.
            
            Das Feld ID wird mit der Häufigkeit befüllt, timestamp bleibt leer.
            
            artcl_aslo
                Auch Artikel mit Sprachen verknüpfen. Default False.
            
            NB: Nach compute_language() ausführen, um ein besseres Ergebnis zu erhalten.
        """
        #languages = ['en', 'fr', 'de', 'es', 'ja', 'ru', 'it', 'zh', 'fa', 'ar']
        # language Nodes anlegen
        for lang in self.cont_languages.keys():
            print("füge Sprache hinzu: " + lang)
            self.nodes.append([lang, {}, 'language']) # name, languages, type 
        # edges je User anlegen
        for node in self.nodes:
            if node[2] == "user" or (node[2] == "article" and artcl_also == True):
                for lang in node[1].items():
                    if int(lang[1]) > 0:
                        # id wird als Indikator für Häufigkeit genommen, dabei zählt die Länge des []
                        self.edges.append([node[0], lang[0], '', lang[1]*[1]])
                    
                    
    def delete_articles_by_count(self, versionCount = 2, userCount = 2):
        """ Entfernt sämtliche Artikel-Nodes mit weniger als n Versionen gesamt
            (versionCount) oder mit weniger als n zugeordneten Benutzern (userCount)
            
            versionCount
                Anzahl an Versionen (edges) unter der ein Artikel gelöscht wird.
                Optional, default = 2
            
            userCount
                Anzahl an Usern, die einem Artikel zugeordnet sein müssen.
                Unterschreitung -> Löschung. Optional, default = 2
                
            NB: Vor condenseEdges ausführen!
        """
        nodes_reduced = self.nodes.copy()
        # articles aus nodes ermitteln (vollständiges item ist nötig zum entfernen)
        articles = [[name, lang, type] for [name, lang, type] in 
                    self.nodes if type == 'article']
        print('article mit < ' + str(versionCount) + ' Referenzen und < ' + str(userCount) + ' beteiligten Usern werden entfernt ..')
        # für jeden article die Referenzen in edges prüfen
        for item in articles:
            mentions = [user for [user, article, timestamp, id] in 
                        self.edges if article == item[0]]
            # Zahl mentions prüfen, Zahl unique (weil Set) mentions prüfen
            if len(mentions) < versionCount or len(set(mentions)) < userCount:        
                nodes_reduced.remove(item)
        self.nodes = nodes_reduced.copy()
        #return nodes_reduced
                    
        
    def condense_edges(self):
        """ Ermittelt edges mit gleicher Relation und fügt diese zusammen.
            Prüft das Ziel der Edges und entfernt Edges ohne passenden Artikel.
            
            Aus edge[user, article, timestamp, id] wird [user, article, [timestamps], [ids]].
            
            NB: NACH delete_articles_by_count() ausführen.
        """
        edges_condensed = list()
        print('fasse parallele edges zusammen ..')
        articles = [name for [name, lang, type] in self.nodes 
                    if type == 'article' or type == 'language']
        for edge in self.edges:
            if edge[1] in articles:
                # Duplikate via user-article-Relation ermitteln
                duplicates = [[user, article, timestamp, nodeid] for 
                              [user, article, timestamp, nodeid] in 
                              self.edges if user == edge[0] and article == edge[1]]    
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
        self.edges = edges_condensed.copy()
        #return edges_condensed  
                         
        
    def return_interval(self, begin, end):
        """ Vergleicht die Timestamps in edges[] mit den übergebenen Grenzwerten
            und gibt ein (nodes[], edges[]) tuple für den gegebenen Zeitraum zurück.
            Relationen zu nachträglich erzeugten Sprach-Nodes werden immer übernommen.
        
            begin:
                Datetime in YYYYMMDDHHMM (ISO 8601) <= Intervall.
            end:
                Datetime in YYYYMMDDHHMM (ISO 8601) >= Intervall.
        """
        
        nodes_slice = list()
        edges_slice = list()
        lang_edges = [[user, article, timestamp, id] for [user, article, timestamp, id] in self.edges if article in self.cont_languages.keys()]
        # Edges über timestamp ermitteln
        # { user, article, timestamp, id } oder { user, article, [timestamp], [id] }
        for edge in self.edges:
            # Sprach-Relationen haben kein Timestamp und müssen gesondert behandelt werden
            if edge not in lang_edges:
                # liste -> also condensed -> also auf Listeneinträge prüfen
                if type(edge[2]) == type(list()):
                    # todo nur timestamps & ids einfügen, die der Einschränkung entsprechen    
                    timestamps = [timestamp for timestamp in edge[2] if int(timestamp) >= begin and int(timestamp) <= end]
                    if len(timestamps) > 0:
                        # add this edge
                        edges_slice.append(edge)
                # keine Liste -> nicht condensed
                else:                    
                    if int(edge[2]) >= begin and int(edge[2]) <= end:
                        edges_slice.append(edge)
        # alle Nodes übernehmen, die in edges_slice referenziert werden
        # nodes { name(title/user), lang{}, type(article/user/language) }
#        nodes_slice = [[name, lang, type] from [name, lang, type] in self.nodes if name in edges_slice[0] or name in edges_slice[1]]    
        nodes_in_edges = [user for [user, article, timestamp, id ] in edges_slice]
        nodes_in_edges += [article for [user, article, timestamp, id ] in edges_slice]
#        return((nodes_slice, edges_slice))
        nodes_in_edges = set(nodes_in_edges)
        return(nodes_in_edges)    
    
    
    
    