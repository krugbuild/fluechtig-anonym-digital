# netWikiAnalysis

## Wege der Internetzensur: Akteursanalysen in der Wikipedia als Bestandteil einer digitalen Quellenkritik

Repositorium zum Abschlussprojekt. Status: in Arbeit.

---

Quellcodedokumentation, Stand: 2020-05-05

``` Python 3.6.9
class UserNetwork(builtins.object)
 |  Klasse zur Datenerhebung- und -verarbeitung von Usernetzwerken in 
 |  Wikipedia. Dient als Grundlage für Netzwerkanalysen.
 |  
 |  Exemplarischer Aufruf:
 |      
 |      Initialisierung und Abruf der letzten 500 Versionen einer Artikelhistorie:
 |          
 |      >>> usrntwrk = UserNetwork()
 |      >>> usrntwrk.add_article_data("https://en.wikipedia.org/w/index.php?
 |      title=Coronavirus_disease_2019&offset=&limit=500&action=history")
 |      
 |      Abruf der letzten 50 Edits für jeden User der abgerufenen Historie
 |      in allen definierten Sprachen (self.cont_languages). Zuordnung von
 |      Sprachen zu Nutzern und Erweiterung des Netzwerkes um Sprachknoten.
 |      
 |      >>> usrntwrk.add_usercontributions("50")
 |      >>> usrntwrk.compute_language()
 |      >>> usrntwrk.create_language_network()
 |      
 |      Entfernen aller Artikel mit weniger als 5 referenzierten Usern.
 |      Zusammenfassen von gleichartigen Edges (selbe Relation).
 |      
 |      >>> usrntwrk.delete_articles_by_count(userCount = 5)
 |      >>> usrntwrk.condense_edges()
 |  
 |  Methods defined here:
 |  
 |  __init__(self)
 |      List definition:
 |      
 |      - nodes [[ name(title/user), lang{}, type(article/user/language) ]]
 |      
 |      - edges [[ user, article, timestamp, id ]]
 |      
 |      - languages { kürzel (z.B. en) : contributions-url}
 |              
 |          -> contribution-URLs müssen dem Schema {Kennzeichen Sprache}.wikipedia.org/w/index.php?title={Spezialseite:Beiträge nach Sprache} entsprechen
 |          
 |          -> z.B. {"en" : "https://en.wikipedia.org/w/index.php?title=Special:Contributions"}
 |      
 |          -> Auswahl entspricht TOP 8 Sprachen gem. Useraktivität auf Wikipedia
 |  
 |  add_article_data(self, url)
 |      Lädt eine via URL definierte Artikelhistorie der Wikipedia herunter
 |      oder lädt ein lokales Abbild und trägt den Artikel sowie die
 |      zugehörigen Benutzer in nodes[] und edges[] ein.
 |      
 |      url:
 |          Parametrisierte URL der Artikelhistorie in der Form: https://en.wikipedia.org/w/index.php?title=TITLE&limit=LIMIT&action=history
 |  
 |  add_user_data(self, url)
 |      Lädt die via URL definierte Usercontribution der Wikipedia herunter
 |      oder lädt ein lokales Abbild und trägt den User sowie die
 |      aufgeführten Artikel in nodes[] und edges[] ein.
 |      
 |      url:
 |          Parametrisierte URL der Usercontribution in der Form: https://en.wikipedia.org/w/index.php?title=Special:Contributions&limit={LIMIT}&target={USER}
 |          NB: &target=USER muss unbedingt als letztes Element notiert werden!
 |  
 |  add_usercontributions(self, depth='100', users=None)
 |      Fügt für alle User des aktuellen Netzwerkes für alle definierten 
 |      Sprachen (self.cont_languages) die User-Contributions als Nodes 
 |      hinzu und verknüpft diese mit dem User.
 |      Dient der Ermittlung der User-Sprachen über die Contributions und
 |      zur Sichtbarmachung eventueller Contributionnetzwerke.
 |      
 |      depth:
 |          Int. Default = 100. Anzahl an Einträgen je Contribution die geladen 
 |          werden soll.
 |          
 |      users:
 |          List. Default = None. Ermittelt die Contributions für die direkt
 |          als Liste übergebenen User. Die lokale nodes[] wird hierbei ignoriert.
 |  
 |  compute_language(self)
 |      Ermittelt über die User Contributions die Sprachen und deren
 |      absolute Häufigkeit je User.
 |      
 |      potentieller Parameter: unique 
 |          -> nur unteschiedl. Artikel zählen
 |  
 |  condense_edges(self)
 |      Ermittelt edges mit gleicher Relation und fügt diese zusammen.
 |      Prüft das Ziel der Edges und entfernt Edges ohne passenden Artikel.
 |      
 |      Aus edge[user, article, timestamp, id] wird [user, article, [timestamps], [ids]].
 |      
 |      NB: NACH delete_articles_by_count() ausführen.
 |  
 |  create_language_network(self, artcl_also=False)
 |      Erzeugt Nodes für alle definierten Sprachen (self.languages) und
 |      verknüpft diese mit Usern und ggf. mit Artiklen.
 |      
 |      Das Feld ID wird mit der Häufigkeit befüllt, timestamp bleibt leer.
 |      
 |      artcl_aslo
 |          Auch Artikel mit Sprachen verknüpfen. Default False.
 |      
 |      NB: Nach compute_language() ausführen, um ein besseres Ergebnis zu erhalten.
 |  
 |  delete_articles_by_count(self, versionCount=2, userCount=2)
 |      Entfernt sämtliche Artikel-Nodes mit weniger als n Versionen gesamt
 |      (versionCount) oder mit weniger als n zugeordneten Benutzern (userCount)
 |      
 |      versionCount
 |          Anzahl an Versionen (edges) unter der ein Artikel gelöscht wird.
 |          Optional, default = 2
 |      
 |      userCount
 |          Anzahl an Usern, die einem Artikel zugeordnet sein müssen.
 |          Unterschreitung -> Löschung. Optional, default = 2
 |          
 |      NB: Vor condenseEdges ausführen!
 |  
 |  edges_append(self, user, article, timestamp, versionid, language)
 |      Erweitert edges[] um ein Element mit dem übergebenen Werten.
 |      Gewährleistet die Typsicherheit. Gibt die eingefügte edge[] zurück.
 |      Es findet eine Duplikatsprüfung statt. Timestamps werden normalisiert.
 |      
 |      user:
 |          Str. Eindeutiger Bezeichner eines Users. Eventuelle
 |          Codierungen (z.B. %20 für Leerzeichen) werden aufgelöst.
 |          
 |      article:
 |          Str. Eindeutiger Bezeichner eines Artikels oder eines Sprach-Nodes.
 |          Eventuelle Codierungen (z.B. %20 für Leerzeichen) werden aufgelöst.
 |          
 |      timestamp:
 |          Str. Datetime im Format YYYYMMDDHHMM oder sprachabhängigem Format.
 |          
 |      versionid:
 |          Str. Id zur Identifikation einzelner Artikelversionen.
 |          
 |      language:
 |          Str. Sprachkennzeichen (zweistellig, z.B. "de").
 |  
 |  nodes_append(self, name, nodetype, langcode, langcount=1)
 |      Erweitert nodes[] um ein Element mit dem übergebenen Werten.
 |      Gewährleistet die Typsicherheit. Gibt den eingefügten Node[] zurück.
 |      Es findet eine Duplikatsprüfung statt.
 |      
 |      name:
 |          Str. Eindeutiger Bezeichner eines Artikels oder Users. Eventuelle
 |          Codierungen (z.B. %20 für Leerzeichen) werden aufgelöst, da Name
 |          als Identifikator benutzt wird. Sprachen werden ggf. ebenfalls als 
 |          Nodes gespeichert.
 |          
 |      nodetype:
 |          Str. Identifiziert die Art des Nodes. Muss ('article', 'user', 
 |          'language') entsprechen.
 |          
 |      langcode:
 |          Str. Sprachcode (z.B. "en"). Muss aus zwei Zeichen bestehen, sonst
 |          wird ein Leerstring als Platzhalter eingetragen.
 |          
 |      langcount:
 |          Int. Default = 1. Vorkommen einer Sprache: Dient der Berechnung
 |          von Sprahverteilungen auf Node-Ebene. Wird langcode nicht korrekt
 |          übergeben, wird langcount ignoriert.
 |          
 |      langcode und langcount werden zu einem dict-Eintrag zusammengefasst: {"en" : 1}
 |  
 |  read_csv(self, file_suffix='')
 |      Liest die Inhalte von nodes[] und edges[] aus einer CSV.
 |      NB: condensed Edges werden nicht übernommen. Nach dem Einlesen muss
 |      condense_edges ggf. erneut ausgeführt werden.
 |      
 |      file_suffix:
 |          Str. Default "". Kennzeichen zur identifikation von Dateien. Wird
 |          im Dateinamen zwischen nodes/edges und .csv eingefügt.
 |  
 |  return_interval(self, begin, end)
 |      Vergleicht die Timestamps in edges[] mit den übergebenen Grenzwerten
 |      und gibt ein (nodes[], edges[]) tuple für den gegebenen Zeitraum zurück.
 |      Relationen zu den nachträglich erzeugten Sprach-Nodes werden immer
 |      übernommen, sind also interval-unabhängig.
 |      
 |      begin:
 |          Datetime. <= Intervall.
 |      end:
 |          Datetime. >= Intervall.
 |          
 |      Parametersignatur:
 |          datetime(YYYY, M, D, h, m)
 |          
 |      returns:
 |          tuple(nodes[], edges[])
 |  
 |  write_csv(self, file_suffix='')
 |      Speichert die Inhalte von nodes[] und edges[] als CSV.
 |      NB: Condensed edges werden dabei aufgelöst.
 |      
 |      file_suffix:
 |          Str. Default "". Kennzeichen zur identifikation von Dateien.
 |          Entspricht dem Bereich zwischen nodes/edges und .csv im Dateinamen.
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |  
 |  __dict__
 |      dictionary for instance variables (if defined)
 |  
 |  __weakref__
 |      list of weak references to the object (if defined)
 |  
 |  edges
 |      edges [[ user, article, timestamp, id ]]
 |  
 |  nodes
 |      nodes [[ name(title/user), lang{}, type(article/user/language) ]]
```

---

[![Creative Commons Lizenzvertrag](https://i.creativecommons.org/l/by-sa/3.0/de/88x31.png)](http://creativecommons.org/licenses/by-sa/3.0/de/) Sofern in den einzelnen Dateien nicht anders angegeben, ist dieses Werk lizenziert unter einer [Creative Commons Namensnennung - Weitergabe unter gleichen Bedingungen 3.0 Deutschland Lizenz](http://creativecommons.org/licenses/by-sa/3.0/de/). Der Autor folgt hierbei der CC BY-SA-Lizenzierung der Wikipediaartikel, welche die Quellenbasis des Projektes bilden.