# Quelltext

## Python Skripte

Im Folgenden werden Auszüge des für diese Untersuchungen geschriebenen Quelltextes aufgelistet. Die Auswahl beschränkt sich dabei auf zentrale Bestandteile der Funktionslogik. Ausschließlich unterstützende Teile wie Konstruktoren oder getter und setter werden nicht aufgeführt. Der vollständige Quelltext liegt liegt als usernetwork.py der Arbeit bei. Der Quelltext wurde in Python 3.6 unter Verwendung von Spyder 3.2.6 geschrieben.

### class UserNetwork 

Klasse zur Datenerhebung- und -verarbeitung von Usernetzwerken in der Wikipedia. Dient als Grundlage für Netzwerkvisualisierungen und -analysen.

``` python
# Exemplarischer Aufruf:
# Initialisierung und Abruf der letzten 500 Versionen einer Artikelhistorie:
usrntwrk = UserNetwork()
usrntwrk.add_article_data("https://en.wikipedia.org/w/index.php?title=Coronavirus_disease_2019&offset=&limit=500&action=history")

# Sicherung der Ergebnismenge als .csv unter Angabe von Titel und Tiefe.
usrntwrk.write_csv("_corona_500")

# Abruf der letzten 50 Edits für jeden User der abgerufenen Historie in allen definierten Sprachen (self.cont_languages). Zuordnung von Sprachen zu Nutzern gemäß Usercontributions.
usrntwrk.add_usercontributions("50")
usrntwrk.compute_language

# Entfernen aller Artikel mit weniger als 5 referenzierten Versionen und Zusammenfassen von gleichartigen Edges (selbe Relation)
usrntwrk.delete_articles_by_count(edgeCount = 5)
usrntwrk.condense_edges()

# Visualisierung der Sprachverteilung mittels Sprachknoten.
usrntwrk.create_language_network()

```

#### def _get_xml_data`(self, url, stylesheet)`

Ruft eine Seite ab und transformiert diese nach XML.

``` python
# url:          parametrisierte URL der Artikelhistorie oder User contributions
# stylesheet:   xslt zur Transformation der abzurufenden Daten
# returns:      etree-Objekt mit XML

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
```

#### def add_article_data`(self, url)`

Lädt eine via URL definierte Artikelhistorie der Wikipedia herunter oder lädt ein lokales Abbild und trägt den Artikel sowie die zugehörigen Benutzer in `nodes[]` und `edges[]` ein.

``` python
# url:  Parametrisierte URL der Artikelhistorie in der Form: https://en.wikipedia.org/w/index.php?title=TITLE&limit=LIMIT&action=history

# article XML beziehen bzw. lokale Kopie laden
article = self._get_xml_data(url, "history.xsl")

# article Sprache ermitteln
article_lang = article.xpath('/article/language')[0].text

# article-node zusammenstellen
article_node = self.nodes_append(article.xpath('/article/title')[0].text.rsplit(": ", 1)[0], 'article', article_lang, 1)

for version in article.xpath('/article/versions/version'):
    user_node = self.nodes_append(version.xpath('./user')[0].text, 'user', '')
    
    # version als edge hinzufügen
    self.edges_append(user_node[0],
        article_node[0],
        version.xpath('./timestamp')[0].text,
        version.xpath('./id',)[0].text,
        article_lang)
```

#### def compute_language`(self)`

Ermittelt über die User Contributions die Sprachen und deren absolute Häufigkeit je User.

``` python
# NB: Vor condense_edges() und delete_nodes_by_count() ausführen.

# aus nodes[] _alle_ Artikel und deren Sprache (z.B. {"en":1}) auflisten
articles = [[name, lang] for [name, lang, type] in self.nodes if type == 'article']
for node in self.nodes:
    if node[2] == 'user':

        # alle Artikel-User-Relationen für den aktuellen User aus edges[]
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
```

#### def add_usercontributions`(self, depth = "100", offset = "", users = None)`

Fügt für alle User des aktuellen Netzwerkes für alle definierten Sprachen (`self._cont_languages`) die User-Contributions als Nodes hinzu und verknüpft diese mit dem User. Dient der Ermittlung der User-Sprachen über die Contributions und zur Sichtbarmachung eventueller Contributionnetzwerke.

``` python
# depth:    Int. Default = 100. Anzahl an Einträgen je Contribution die geladen werden soll.
# offset:   Str. Datum im Format YYYYMMDDhhmmss. Zeitpunkt ab dem antichronologisch die Contributions ermittelt werden.
# Users:    List. Default = None. Ermittelt die Contributions für die direkt als Liste übergebenen User. Die lokale nodes[] wird hierbei ignoriert.

# wenn Users nicht gesetzt ist -> vorhandene User ermitteln
if users is None or len(users) == 0:
    users = [name for [name, lang, nodetype] in self._nodes if nodetype == "user"]

    # (falsche) Stringeingaben abfangen und in Liste umwandeln
    if isinstance(users, str) and len(users) > 0:
        users = [users]

    for user in users:
        print("ermittle Artikel für User " + user + " ..")
        for cont in self._cont_languages.items():

            # je Sprachversion, NB &target=USERNAME muss als letztes Element notiert sein
            self.add_user_data(cont[1] + '&offset=' + str(offset) + '&limit=' + str(depth) + '&target=' + user)
```

#### def delete_nodes_by_count`(self, edgeCount = 2, user = False)`

Entfernt sämtliche Article-Nodes mit weniger als n Versionen gesamt (`edgeCount`). Optional werden auch Usernodes entfernt (`user`).

``` python
# edgeCount:    Anzahl an Versionen (edges) unter der ein Artikel gelöscht wird. Optional, default = 2
# user:         Bool. Default = False. Wenn gesetzt, werden User analog zu Artikeln entfernt.

# NB: Vor condense_edges() ausführen.

# lokale Kopie zur Manipulation
nodes_reduced = self.nodes.copy()
for item in self.nodes:
    mentions = None

    if user and item[2] == 'user':
        # Referenzen für User ermitteln
        mentions = [article for [user, article, timestamp, vid, lang] in self.edges if user == item[0]]
    
    elif item[2] == 'article':
        # Referenzen für Artikel ermitteln
        mentions = [user for [user, article, timestamp, vid, lang] in self.edges if article == item[0]]

    # Wenn Referenzen < Parameter, Item löschen
    if mentions is not None and len(set(mentions)) < edgeCount:
        nodes_reduced.remove(item)

# reduzierte Liste übergeben (an private, da setter appended)
self._nodes = nodes_reduced.copy()
```

#### def return_interval`(self, begin, end)`

Vergleicht die Timestamps in `edges[]` mit den übergebenen Grenzwerten und gibt ein (`nodes[]`, `edges[]`) tuple für den gegebenen Zeitraum zurück. Relationen zu den nachträglich erzeugten Sprach-Nodes werden immer übernommen, sind also interval-unabhängig.

``` python
# begin:                Datetime. <= Intervall.
# end:                  Datetime. >= Intervall.
# Parametersignatur:    datetime(YYYY, M, D, h, m)
# returns:              tuple(nodes[], edges[])

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
            # liste -> also condensed -> auf Listeneinträge prüfen
            if type(edge[2]) == type(list()):
                timestamps = [timestamp for timestamp in edge[2] 
                    if timestamp >= begin and timestamp <= end]
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
users_in_edges = set([user for [user, article, timestamp, vid, lang]
                    in edges_slice])
articles_in_edges = set([article for [user, article, timestamp, vid, lang] 
                    in edges_slice])

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
```

## XSLT-SCHEMATA

Die folgenden Schema-Auszüge zeigen die verwendeten Transformationsschemata zur Auswertung der HTML-Dateien. Der Quelltext entspricht XSLT in der Version 1.0. Die Auszüge beschränken sich auf die Funktionslogik.

### history.xsl

Die Schemadatei dient dazu, das HTML-Dokument einer Wikipedia-Versionsgeschichte zu zerlegen und in eine auswertbare Struktur zu überführen.

``` xslt
<xsl:variable name="lang" select="//@lang" />

<xsl:template match="/">
    <article>
        <language><xsl:value-of select="$lang"/></language>
        <xsl:apply-templates />
    </article>
</xsl:template>

<xsl:template match='title'>
    <title>
        <xsl:value-of select='.'/>
    </title>
</xsl:template>

<xsl:template match='ul[@id="pagehistory"]'>
    <versions>
        <xsl:for-each select="li">
            <version>
                <id><xsl:value-of select="@data-mw-revid"/></id>
                <timestamp>
                    <xsl:value-of select='*[@class="mw-changeslist-date"]' />
                </timestamp>
                <user>
                    <xsl:value-of select=".//bdi"/>
                </user>
                <minoredit>
                    <xsl:choose>
                        <xsl:when test='.//@class="minoredit"'>1</xsl:when>
                        <xsl:otherwise>0</xsl:otherwise>
                    </xsl:choose>
                </minoredit>
                <comment>
                    <xsl:value-of select='*[@class="comment comment--without-parentheses"]'/>
                </comment>
           </version>
        </xsl:for-each>
    </versions>
</xsl:template>
```

### user.xsl

Diese Schemadatei dient dazu, das HTML-Dokument einer Wikipedia-Benutzerbeiträgeseite zu zerlegen und in eine auswertbare Struktur zu überführen.

``` xslt
<xsl:variable name="lang" select="//@lang" />

<xsl:template match="/">
    <user>
        <language><xsl:value-of select="$lang"/></language>
        <xsl:apply-templates />
    </user>
</xsl:template>

<xsl:template match='link[@rel="canonical"]'>
    <name>
        <xsl:value-of select='substring-after(@href, "target=")'/>
    </name>
</xsl:template>

<xsl:template match='ul[@class="mw-contributions-list"]'>
    <versions>
        <xsl:for-each select="li">
            <version>
                <id><xsl:value-of select="@data-mw-revid"/></id>
                <timestamp>
                    <xsl:value-of select='*[@class="mw-changeslist-date"]' />
                </timestamp>
                <title>
                    <xsl:value-of select="a/@title"/>
                </title>
                <comment>
                    <xsl:value-of select='*[@class="autocomment"]'/>
                </comment>
            </version>
        </xsl:for-each>
    </versions>
</xsl:template>
```