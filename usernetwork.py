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

class UserNetwork:
    """ Klasse zur Datenerhebung- und -verarbeitung von Usernetzwerken in 
        Wikipedia. Dient als Grundlage für Netzwerkanalysen.
    """
    
    def __init__(self):
        """ Dictionary definition:
        nodes { name(title/user), lang, type(article/user) }
        edges { user, article, timestamp, id }
        languages { kürzel (z.B. en) : contributions-url}
        -> URLs müssen dem Schema {wiki & sprache}/w/index.php?title={Spezialseite:Beiträge nach Sprache} entsprechen
        -> Auswahl entspricht TOP 10 Sprachen nach aktivsten Usern auf Wikipedia
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
        # article-node zusammenstellen
        article_node = [article.xpath('/article/title')[0].text.rsplit(": ", 1)[0] # name
                        , {article.xpath('/article/language')[0].text : 1} # language
                        , 'article'] # type
        # article hinzufügen, sofern neu
        if article_node not in self.nodes:
            self.nodes.append(article_node)
            print('article added: ' + str(article_node))
        # user als nodes, versions als edges hinzufügen
        for version in article.xpath('/article/versions/version'):
            # user-node zusammenstellen
            user_node = [version.xpath('./user')[0].text # name
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
        user_node = [user.xpath('/user/name')[0].text #name
                     , {} #language
                     , 'user'] #type
        # user hinzufügen, sofern neu
        if user_node not in self.nodes:
            self.nodes.append(user_node)
            print('user added: ' + str(user_node))
        # articles als nodes, versions als edges hinzufügen
        if user.xpath('/user/versions/version') is not None:
            for version in user.xpath('/user/versions/version'):
                # article-node zusammenstellen
                article_node = [version.xpath('./title')[0].text #name
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

    def condense_edges(self):
        """ NB: NACH delete_articles_by_count() ausführen
            Ermittelt edges mit gleicher Relation und fügt diese zusammen
            Prüft das Ziel der Edges und entfernt Edges ohne passenden Artikel
            edges { user, article, timestamp, id } zu [user, article, [timestamps], [ids]]
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
        
        
    def delete_articles_by_count(self, versionCount = 2, userCount = 2):
        """ Entfernt sämtliche Artikel-Nodes mit weniger als n Versionen gesamt
            (versionCount) oder mit weniger als n zugeordneten Benutzern (userCount)
            NB: Vor condenseEdges ausführen!
            versionCount = Anzahl an Versionen (edges) unter der ein Artikel
                gelöscht wird. Optional, default = 2
            userCount = Anzahl an Usern, die einem Artikel zugeordnet sein 
                müssen. Unterschreitung -> Löschung. Optional, default = 2
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
    
    #TODO
    
    def computeLanguage(self):
        """ Ermittelt über die User Contributions die Sprachen und deren
            absolute Häufigkeit je User
        """
        
        for item in self.cont_languages.keys():
            print(item)
        
        # alle artikel mit zugehöriger Sprache ermitteln
        articles = [[name, lang] for [name, lang, type] in self.nodes if type == 'article']
        for node in self.nodes:
            if node[2] == 'user':
                # alle article des aktuellen users ermitteln
                edits = [article for [user, article, timestamp, id] in self.edges if user == node[0]]
                # alle Sprachen der articles ermitteln
                languages = [lang for [name, lang] in articles if name in edits]
                # Sprachen des aktuellen Users ermitteln            
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!morgen            
                en = node[1].get('en', 0)
                fr = node[1].get('fr', 0)
                de = node[1].get('de', 0)
                es = node[1].get('es', 0)
                ja = node[1].get('ja', 0)
                ru = node[1].get('ru', 0)
                it = node[1].get('it', 0)
                zh = node[1].get('zh', 0)
                fa = node[1].get('fa', 0)
                ar = node[1].get('ar', 0)
                # und mit den Sprachen aus den articles aufsummieren
                for item in languages:
                    en += item.get('en', 0)
                    fr += item.get('fr', 0)
                    de += item.get('de', 0)
                    es += item.get('es', 0)
                    ja += item.get('ja', 0)
                    ru += item.get('ru', 0)
                    it += item.get('it', 0)
                    zh += item.get('zh', 0)
                    fa += item.get('fa', 0)
                    ar += item.get('ar', 0)
                # neue Sprachsummen setzen
                node[1] = {'en': en, 'fr' : fr, 'de' : de, 'es' : es, 'ja' : ja
                    , 'ru' : ru, 'it' : it, 'zh': zh, 'fa' : fa, 'ar' : ar}
                
    # =============================================================================
                
    def create_language_network(self, artcl_also = False):
        """ Erzeugt Nodes für alle definierten Sprachen (self.languages) und
            verknüpft diese mit Usern und bei artlc_also=True auch mit Artiklen.
            Das Feld ID wird mit der Häufigkeit befüllt, timestamp bleibt leer.
            artcl_aslo = Auch Artikel mit Sprachen verknäpfen. Default False.
        """
        languages = ['en', 'fr', 'de', 'es', 'ja', 'ru', 'it', 'zh', 'fa', 'ar']
        # language Nodes anlegen
        for lang in languages:
            print("füge Sprache hinzu: " + lang)
            self.nodes.append([lang, {}, 'language']) # name, languages, type 
        # edges je User anlegen
        for node in self.nodes:
            if node[2] == "user":
                for lang in node[1].items():
                    if int(lang[1]) > 0:
                        # id wird als Indikator für Häufigkeit genommen, dabei zählt die Länge des []
                        self.edges.append([node[0], lang[0], '', lang[1]*[1]])
                     
    # =============================================================================
    # Ermittelt für eine Liste an Usern 
    
   
        
    # =============================================================================
    
    
    
