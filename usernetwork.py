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
from datetime import datetime
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
            
            - edges [[ user, article, timestamp, versionid, language ]]
            
            - languages { kürzel (z.B. en) : contributions-url}
                    
                -> contribution-URLs müssen dem Schema {Kennzeichen Sprache}.wikipedia.org/w/index.php?title={Spezialseite:Beiträge nach Sprache} entsprechen
                
                -> z.B. {"en" : "https://en.wikipedia.org/w/index.php?title=Special:Contributions"}
            
                -> Auswahl entspricht TOP 8 Sprachen gem. Useraktivität auf Wikipedia
        """
        self._nodes = list()
        self._edges = list()
        self._cont_languages = { "en" : "https://en.wikipedia.org/w/index.php?title=Special:Contributions"
                               , "fr" : "https://fr.wikipedia.org/w/index.php?title=Spécial:Contributions"
                               , "de" : "https://de.wikipedia.org/w/index.php?title=Spezial:Beitr%C3%A4ge"
                               , "es" : "https://es.wikipedia.org/w/index.php?title=Especial:Contribuciones"
                               , "ja" : "https://ja.wikipedia.org/w/index.php?title=特別:投稿記録"
                               , "ru" : "https://ru.wikipedia.org/w/index.php?title=Служебная%3AВклад"
                               , "it" : "https://it.wikipedia.org/w/index.php?title=Speciale:Contributi"
                               , "zh" : "https://zh.wikipedia.org/w/index.php?title=Special:用户贡献"}

# =============================================================================
# getter & setter
# =============================================================================

    @property
    def nodes(self):
        """ nodes [[ name(title/user), lang{}, type(article/user/language) ]] """
        return self._nodes
    
    @nodes.setter
    def nodes(self, value):
        """ Fügt eine nodes[] der lokalen nodes[] hinzu. Führt eine
            Duplikatsprüfung durch.
            
            value:
                Liste mit nodes.
        """
        try:
            for node in value:
                if node not in self.nodes:
                    self.nodes.append(node)
                    print("Node hinzugefügt: " + node[0])
        except ValueError:
            print("Erwartet eine Liste mit nodes.")
        

    def nodes_append(self, name, nodetype, langcode, langcount = 1):
        """ Erweitert nodes[] um ein Element mit dem übergebenen Werten.
            Gewährleistet die Typsicherheit. Gibt den eingefügten Node[] zurück.
            Es findet eine Duplikatsprüfung statt.
            
            name:
                Str. Eindeutiger Bezeichner eines Artikels oder Users. Eventuelle
                Codierungen (z.B. %20 für Leerzeichen) werden aufgelöst, da Name
                als Identifikator benutzt wird. Sprachen werden ggf. ebenfalls als 
                Nodes gespeichert.
                
            nodetype:
                Str. Identifiziert die Art des Nodes. Muss ('article', 'user', 
                'language') entsprechen.
                
            langcode:
                Str. Sprachcode (z.B. "en"). Muss aus zwei Zeichen bestehen, sonst
                wird ein Leerstring als Platzhalter eingetragen.
                
            langcount:
                Int. Default = 1. Vorkommen einer Sprache: Dient der Berechnung
                von Sprahverteilungen auf Node-Ebene. Wird langcode nicht korrekt
                übergeben, wird langcount ignoriert.
                
            langcode und langcount werden zu einem dict-Eintrag zusammengefasst: {"en" : 1}
        """
        language = {}
        # Parameter prüfen
        if isinstance(name, str) and isinstance(nodetype, str) and nodetype in ('article', 'user', 'language'):
            # Auflösung von codierten Zeichen zur Gewährleistung der Eindeutigkeit
            name = unquote(name, encoding='utf-8')
            
            # bei validem langcode dict Eintrag - sonst Leereintrag
            if len(langcode) == 2:
                language = {langcode : langcount}
            node = [name, language, nodetype]
            if node not in self._nodes:
                self._nodes.append(node)
                print("Node hinzugefügt: " + name)
            return node
        else:
            print("nodes[name] erwartet einen String als Bezeichner. nodes[nodetype] muss ('article', 'user', 'language') entsprechen. Vorgang abgebrochen.")
        
        
    @property
    def edges(self):
        """ edges [[ user, article, timestamp, id ]] """
        return self._edges
    
    @edges.setter
    def edges(self, value):
        """ Fügt eine edges[] der lokalen edges[] hinzu. Führt eine
            Duplikatsprüfung durch.
            
            value:
                Liste mit edges.
        """
        try:
            for edge in value:
                if edge not in self.edges:
                    self.edges.append(edge)
                    print("Edge hinzugefügt: " + edge[0] + " - " + edge[1])
        except ValueError:
            print("Erwartet eine Liste mit edges.")
        
        
    def edges_append(self, user, article, timestamp, versionid, language):
        """ Erweitert edges[] um ein Element mit dem übergebenen Werten.
            Gewährleistet die Typsicherheit. Gibt die eingefügte edge[] zurück.
            Es findet eine Duplikatsprüfung statt. Timestamps werden normalisiert.
            
            user:
                Str. Eindeutiger Bezeichner eines Users. Eventuelle
                Codierungen (z.B. %20 für Leerzeichen) werden aufgelöst.
                
            article:
                Str. Eindeutiger Bezeichner eines Artikels oder eines Sprach-Nodes.
                Eventuelle Codierungen (z.B. %20 für Leerzeichen) werden aufgelöst.
                
            timestamp:
                Str. Datetime im Format YYYYMMDDHHMM oder sprachabhängigem Format.
                
            versionid:
                Str. Id zur Identifikation einzelner Artikelversionen.
                
            language:
                Str. Sprachkennzeichen (zweistellig, z.B. "de").
        """
        # Parameter prüfen
        if isinstance(user, str) and isinstance(article, str):
            # Auflösung von codierten Zeichen zur Gewährleistung der Eindeutigkeit
            user = unquote(user, encoding='utf-8')
            article = unquote(article, encoding='utf-8')
            
            # datetime parsen sofern kein dt(), ggf. sprachspezifisch
            if not isinstance(timestamp, datetime):
                timestamp = self._parse_datetime(timestamp, language)
            
            edge = [user, article, timestamp, versionid, language]
            if edge not in self._edges:
                self._edges.append(edge)
                print("\tEdge hinzugefügt: " + user + " - " + article)
            return edge
        else:
            print("edge[user, article] erwarten Strings als Werte. Vorgang abgebrochen.")        
   
# =============================================================================
# parser
# =============================================================================     
        
    def _parse_datetime(self, value, lang):
        """ Parser für Datetime-Formate der verschiedenen Sprachversionen. Gibt
            ein datetime() zurück. Explizite Auflösung ist für folgende Sprachen
            implementiert:
                fr, ja, it, es, ru (en und zh werden schon via Schema vereinheitlicht)
            
            value:
                Str. Datetime im Format YYYYMMDDHHMM sofern nicht explizit behandelt.
                
            lang:
                Str. Sprachkennzeichen (zweistellig, z.B. 'de') zur eindeutigen
                Identifikation des Datumsformats. Ausnahme 'csv' zum Einlesen
                von zuvor schon formatierten Datumsangaben.
                
            Gibt Leerstring nach fehlgeschlagenem Versuch zurück.
        """        
        month = {# en:
                    "January" : "01", "February" : "02", "March" : "03", 
                    "April" : "04", "May" : "05", "June" : "06", "July" : "07",
                    "August" : "08", "September" : "09", "October" : "10",
                    "November" : "11", "December" : "12",
                # fr:
                    "janvier" : "01", "février" : "02", "mars" : "03", "avril" : "04", 
                     "mai" : "05", "juin" : "06", "juillet" : "07", "août" : "08",
                     "septembre" : "09", "octobre" : "10", "novembre" : "11", 
                     "décembre" : "12",
                 # it:
                     "gen" : "01", "feb" : "02", "mar" : "03", "apr" : "04",
                     "mag" : "05", "giu" : "06", "lug"	 : "07", "ago" : "08",
                     "set" : "09", "ott" : "10", "nov" : "11",
                     "dic" : "12",
                 # es (nur div)
                     "ene" : "01", "abr" : "04", "may" : "05", "jun" : "06",
                     "jul" : "07", "sep" : "09", "oct" : "10",
                 # de 
                     "Jan." : "01", "Feb." : "02", "Mär." : "03", "Apr." : "04",
                     "Mai" : "05", "Jun." : "06", "Jul." : "07", "Aug." : "08",
                     "Sep." : "09", "Okt." : "10", "Nov." : "11", "Dez." : "12",
                 # ru
                     "января" : "01", "февраля" : "02", "март" : "03", "марта" : "03",
                     "апреля" : "04",  "мая" : "05", "июня" : "06", "июля" : "07",
                     "августа" : "08", "сентября" : "09", "октября" : "10",
                     "ноября" : "11", "декабря" : "12"}
        
        # Relationen zu Sprachen haben kein Datum (tritt beim Einlesen von CSV auf)
        if value == None or value == "":
            #print("\tLeerer Timestamp.")
            return value
        
        try:
            if lang == 'en' or lang == 'it' or lang == 'ru':
                # en z.B. 07:41, 4 May 2020
                # it z.B. 17:23, 15 mar 2017
                # ru z.B. 09:22, 4 марта 2012
                m = value.split(" ")[2]
                value = value.replace(m, month[m])
                value = datetime.strptime(value, '%H:%M, %d %m %Y')
            elif lang == 'fr':
                # z.B. 25 avril 2020 à 10:57
                m = value.split(" ")[1]
                value = value.replace(m, month[m])
                value = datetime.strptime(value, '%d %m %Y à %H:%M')
            elif lang == 'ja' or lang == 'zh':
                # z.B. 2018年1月1日 (水) 00:36
                # str wird auf digits reduziert
                value = ''.join(e for e in value if e.isdigit())
                # für Eindeutigkeit zwischen date und time ein . eingefügt
                value = "".join((value[:-4], '.', value[-4:]))
                value = datetime.strptime(value, '%Y%m%d.%H%M')                
            elif lang == 'es':
                # z.B. 08:25 2 feb 2013
                m = value.split(" ")[2]
                value = value.replace(m, month[m])
                value = datetime.strptime(value, '%H:%M %d %m %Y')
            elif lang == 'de':
                # z.B. 17:47, 25. Aug. 2018
                m = value.split(" ")[2]
                value = value.replace(m, month[m])
                value = datetime.strptime(value, '%H:%M, %d. %m %Y')
            elif lang == 'csv':
                # z.B. 2020-05-03 16:25:00
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            else:
                # Sonstige in YYYYMMDDhhmm
                value = datetime.strptime(value, '%Y%m%d%H%M')
        except ValueError:
            print("Value Error. Language: " + lang)
            return value
        finally:
            return value
         
                
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
            
            data:
                List. Zu schreibende Liste.
            
            path:
                Str. Pfadangabe zur .csv
                
            header:
                List[Str]. Liste mit Strings zur Identifikation der Spalten. 
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
            Datumsangaben werden in datetime() umgewandelt.
            
            path:
                Str. Pfadangabe zur .csv
        """
        with open(path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            print(header)
            print("lese .. " + csvfile.name + " - header: " + str(header))
            data = list()
            if header[1] == 'lang':
                # Für Nodes mit Lang-Dict: user, {dict language via ast}, type
                data = [[row[0], # user/article
                         ast.literal_eval(row[1]), # {dict language}
                         row[2]] for row in reader] # type
            elif header[2] == 'timestamp':
                # Für Edges mit formatiertem datetime
                data = [[row[0], # source 
                         row[1], # target
                         self._parse_datetime(row[2], 'csv'), # timestamp
                         row[3], # vid
                         row[4]] for row in reader] # lang
            else:
                data = [row for row in reader]
            return data


    def write_csv(self, file_suffix = ""):
        """ Speichert die Inhalte von nodes[] und edges[] als CSV.
            NB: Condensed edges werden dabei aufgelöst.
            
            file_suffix:
                Str. Default "". Kennzeichen zur identifikation von Dateien.
                Entspricht dem Bereich zwischen nodes/edges und .csv im Dateinamen.
        """
        self._write_data_csv(self.nodes, "nodes" + file_suffix + ".csv", 
                             ["id", "lang", "type"])
        self._write_data_csv(self.edges, "edges" + file_suffix + ".csv", 
                             ["source", "target", "timestamp", "id", "lang"])
                
        
    def read_csv(self, file_suffix = ""):
        """ Liest die Inhalte von nodes[] und edges[] aus einer CSV.
            NB: condensed Edges werden nicht übernommen. Nach dem Einlesen muss
            condense_edges ggf. erneut ausgeführt werden.
            
            file_suffix:
                Str. Default "". Kennzeichen zur identifikation von Dateien. Wird
                im Dateinamen zwischen nodes/edges und .csv eingefügt.
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
            
            url:
                Parametrisierte URL der Artikelhistorie in der Form: https://en.wikipedia.org/w/index.php?title=TITLE&limit=LIMIT&action=history
        """
        # article XML beziehen bzw. lokale Kopie laden
        article = self._get_xml_data(url, "history.xsl")
        # article Sprache ermitteln
        article_lang = article.xpath('/article/language')[0].text
        # article-node zusammenstellen
        article_node = self.nodes_append(article.xpath('/article/title')[0].text.rsplit(": ", 1)[0], 
                                         'article', 
                                         article_lang, 1)

        for version in article.xpath('/article/versions/version'):
            user_node = self.nodes_append(version.xpath('./user')[0].text, 'user', '')
            
            # version als edge hinzufügen
            self.edges_append(user_node[0],
                              article_node[0],
                              version.xpath('./timestamp')[0].text,
                              version.xpath('./id',)[0].text,
                              article_lang)
                
                
    def add_user_data(self, url):
        """ Lädt die via URL definierte Usercontribution der Wikipedia herunter
            oder lädt ein lokales Abbild und trägt den User sowie die
            aufgeführten Artikel in nodes[] und edges[] ein.
            
            url:
                Parametrisierte URL der Usercontribution in der Form: https://en.wikipedia.org/w/index.php?title=Special:Contributions&limit={LIMIT}&target={USER}
                NB: &target=USER muss unbedingt als letztes Element notiert werden!
        """
        # article beziehen bzw. lokale Kopie laden
        user = self._get_xml_data(url, "user.xsl")
        # article Sprache ermitteln
        article_lang = user.xpath('/user/language')[0].text
        # user-node zusammenstellen
        user_node = self.nodes_append(user.xpath('/user/name')[0].text, 'user', '')
        
        # articles als nodes, versions als edges hinzufügen
        if user.xpath('/user/versions/version') is not None:
            for version in user.xpath('/user/versions/version'):
                
                # article-node zusammenstellen
                article_node = self.nodes_append(version.xpath('./title')[0].text, 
                                         'article', 
                                         article_lang, 1)
                
                # version als edge hinzufügen
                self.edges_append(user_node[0],
                                  article_node[0],
                                  version.xpath('./timestamp')[0].text,
                                  version.xpath('./id')[0].text,
                                  article_lang)
    
 
    def add_usercontributions(self, depth = "100", users = None):
        """ Fügt für alle User des aktuellen Netzwerkes für alle definierten 
            Sprachen (self._cont_languages) die User-Contributions als Nodes 
            hinzu und verknüpft diese mit dem User.
            Dient der Ermittlung der User-Sprachen über die Contributions und
            zur Sichtbarmachung eventueller Contributionnetzwerke.
            
            depth:
                Int. Default = 100. Anzahl an Einträgen je Contribution die geladen 
                werden soll.
                
            users:
                List. Default = None. Ermittelt die Contributions für die direkt
                als Liste übergebenen User. Die lokale nodes[] wird hierbei ignoriert.
        """
        # wenn Users nicht gesetzt ist -> vorhandene User ermitteln
        if users is None or len(users) == 0:
            users = [name for [name, lang, nodetype] in self._nodes if nodetype == "user"]
         
        # (falsche) Stringeingaben abfangen und in Liste umwandeln
        if isinstance(users, str) and len(users) > 0:
            users = [users]
            
        for user in users:
            print("ermittle Artikel für User " + user + " ..")
            for cont in self._cont_languages.items():
                # Aufruf je Sprachversion, NB &target=USERNAME muss als letztes 
                # .. Element notiert sein (sonst liefert das Schema nichts)
                self.add_user_data(cont[1] + '&limit=' + str(depth) + '&target=' + user)
    
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
                edits = [article for [user, article, timestamp, vid, lang] in self.edges if user == node[0]]
                # für die ermittelten Artikel die Sprache{} ermitteln
                # languages ist also: [{},]
                languages = [lang for [name, lang] in articles if name in edits]
                # node[1] = Sprachen, sollte bei einem User ein leeres dict sein
                if type(node[1]) != type(dict()):
                    node[1] = dict()
                # für jedes {} in languages wird dessen wert 
                for item in languages:
                    # je item wird jeder bekannte Sprachkey geprüft
                    for lang in self._cont_languages.keys():
                        # je Sprachkey wird der Wert aus item abgerufen und im node aufaddiert
                        if lang in node[1].keys():
                            node[1][lang] += item.get(lang, 0)
                        else:
                            node[1].update({lang: item.get(lang, 0)})
                                    
                            
    def _check_integrity(self, force = False):
        """ Überprüft die Integrität der Daten auf zusammenpassende Edge und 
            Nodes Listen. 
            
            force:
                Entfernt 
        """
        edges_reduced = self._edges.copy()
        
        users = [name for [name, lang, ntype] in self._nodes 
                    if ntype == 'user']
        articles = [name for [name, lang, ntype] in self._nodes 
                    if ntype == 'article']
        
        for edge in self._edges:
            if edge[0] not in users or edge[1] not in articles:
                print("not in list: " + str(edge))
                if force:
                    edges_reduced.remove(edge)
                    print("\tremoved")
        self._edges = edges_reduced.copy()
        
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
        # language Nodes anlegen
        for lang in self._cont_languages.keys():
            print("füge Sprache hinzu: " + lang)
            self.nodes.append([lang, {}, 'language']) # name, languages, type 
        # edges je User anlegen
        for node in self.nodes:
            if node[2] == "user" or (node[2] == "article" and artcl_also == True):
                for lang in node[1].items():
                    if int(lang[1]) > 0:
                        # id wird als Indikator für Häufigkeit genommen, dabei zählt die Länge des []
                        self.edges_append(node[0], lang[0], '', lang[1]*[1], lang[0])
                    
                    
    def delete_nodes_by_count(self, edgeCount = 2, user = False):
        """ Entfernt sämtliche Article-Nodes mit weniger als n Versionen gesamt
            (versionCount) oder mit weniger als n zugeordneten Benutzern (userCount).
            Optional werden auch Usernodes entfernt (user).
            
            versionCount:
                Anzahl an Versionen (edges) unter der ein Artikel gelöscht wird.
                Optional, default = 2
            
            userCount:
                Anzahl an Usern, die einem Artikel zugeordnet sein müssen.
                Unterschreitung -> Löschung. Optional, default = 2
            
            user:
                Bool. Default = False. Wenn gesetzt, werden User analog zu Artikeln
                entfernt.
                
            NB: Vor condenseEdges ausführen!
        """
        # lokale Kopie zur Manipulation
        nodes_reduced = self.nodes.copy()
        for item in self.nodes:
            mentions = None
            if user and item[2] == 'user':
                # Referenzen für User ermitteln
                mentions = [article for [user, article, timestamp, vid, lang] in 
                            self.edges if user == item[0]]
            elif item[2] == 'article':
                # Referenzen für Artikel ermitteln
                mentions = [user for [user, article, timestamp, vid, lang] in 
                            self.edges if article == item[0]]
            # Wenn Referenzen < Parameter, Item löschen
            if mentions is not None and len(set(mentions)) < edgeCount:
                nodes_reduced.remove(item)
        # reduzierte Liste übergeben (an private, da setter appended)
        self._nodes = nodes_reduced.copy()
                    
        
    def condense_edges(self):
        """ Ermittelt edges mit gleicher Relation und fügt diese zusammen.
            Prüft das Ziel der Edges und entfernt Edges ohne passenden Artikel.
            
            Aus edge[user, article, timestamp, id, lang] wird [user, article, [timestamps], [ids], lang].
            
            NB: NACH delete_articles_by_count() ausführen.
        """
        edges_condensed = list()
        print('fasse parallele edges zusammen ..')
        articles = [name for [name, lang, type] in self.nodes 
                    if type == 'article' or type == 'language']
        for edge in self._edges:
            if edge[1] in articles:
                # Duplikate via user-article-Relation ermitteln
                duplicates = [[user, article, timestamp, nodeid, lang] for 
                              [user, article, timestamp, nodeid, lang] in 
                              self._edges if user == edge[0] and article == edge[1]]    
                # alle Timestamps aus Duplikaten ermitteln
                # NB Timestamp und ID werden unzusammenhängend ausgelesen -> da Listen aber sortiert sind, ist das kein Problem
                timestamps = [timestamp for 
                              [user, article, timestamp, nodeid, lang] in duplicates]
                # alle IDs aus Duplikat ermitteln
                ids = [nodeid for [user, article, timestamp, nodeid, lang] in duplicates]
                # condensed sind urspr. User und Artikel, sowie Timestamp und ID als []
                condensed = [duplicates[0][0], duplicates[0][1], timestamps, ids, duplicates[0][4]]
                # Duplikatsprüfung vor append
                if condensed not in edges_condensed:
                    edges_condensed.append(condensed)
        self._edges = edges_condensed.copy()
        self._check_integrity(True)
        
        
    def return_interval(self, begin, end):
        """ Vergleicht die Timestamps in edges[] mit den übergebenen Grenzwerten
            und gibt ein (nodes[], edges[]) tuple für den gegebenen Zeitraum zurück.
            Relationen zu den nachträglich erzeugten Sprach-Nodes werden immer
            übernommen, sind also interval-unabhängig.
        
            begin:
                Datetime. <= Intervall.
            end:
                Datetime. >= Intervall.
                
            Parametersignatur:
                datetime(YYYY, M, D, h, m)
                
            returns:
                tuple(nodes[], edges[])
        """
        
        nodes_slice = list()
        edges_slice = list()
        
        # Edges der Sprachrelationen ermitteln -> die haben keine Timestamps
        lang_edges = [[user, language, timestamp, vid, lang] 
                        for [user, language, timestamp, vid, lang] 
                        in self._edges if language in self._cont_languages.keys()]
        # Edges über timestamp ermitteln. Edges: [user, article, timestamp, id, lang]
        # oder condensed: [user, article, [timestamp], [id], lang]
        
        for edge in self._edges:
            # Sprach-Relationen haben kein Timestamp und müssen gesondert behandelt werden
            if edge not in lang_edges:
                try: 
                    # liste -> also condensed -> also auf Listeneinträge prüfen
                    if type(edge[2]) == type(list()):
                        # todo nur timestamps & ids einfügen, die der Einschränkung entsprechen    
                        timestamps = [timestamp for timestamp in edge[2] if timestamp >= begin and timestamp <= end]
                        if len(timestamps) > 0:
                            # add this edge
                            edges_slice.append(edge)
                    # keine Liste -> nicht condensed -> datetime()
                    else:
                        if edge[2] >= begin and edge[2] <= end:
                            edges_slice.append(edge)
                except TypeError:
                    print("Wrong timestamp type: " + str(edge))
                        
        # alle adressierten Nodes (user & article) ermitteln und unnötige Duplikate entfernen
        users_in_edges = set([user for [user, article, timestamp, vid, lang] in edges_slice])
        articles_in_edges = set([article for [user, article, timestamp, vid, lang] in edges_slice]    )

        # Sprachrelationen für User hinzufügen
        edges_slice += [[user, language, timestamp, vid, lang] 
                        for [user, language, timestamp, vid, lang] 
                        in lang_edges if user in users_in_edges]
        
        # alle Nodes übernehmen, die in edges_slice oder _cont_languages referenziert werden
        nodes_slice = [[name, lang, ntype] 
                        for [name, lang, ntype] 
                        in self._nodes 
                        if name in users_in_edges
                        or name in articles_in_edges 
                        or name in self._cont_languages.keys()]

        return (nodes_slice, edges_slice)


        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    