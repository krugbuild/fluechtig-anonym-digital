<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- 
## history.xsl
# Die Schemadatei dient dazu, das HTML-Dokument einer Wikipedia-Versionsgeschichte zu zerlegen und in eine auswertbare Struktur zu bringen.
# Das Tag <versions/> beinhaltet hierbei die zentrale Liste mit den einzelnen Versionen des zugehörigen Artikels. Der restliche Seiteninhalt wird entsprechend davor und dahinter im Tag <article/> gekapselt.
# Das Schema zerlegt die dargestellten Datumsangaben in das neutrale Format `YYYYMMDDhhmm` um eine einfache Verarbeitung zu gewährleisten. 
# Mit Stand 27.01.2020 ist nur die Zerlegung des in der chinesischen Wikipedia benutzten Datumsformat (etwa `2020年1月4日 (六) 10:20`) implementiert.
# Update 04-09: <title> hinzugefügt.
#
# Autor: 		Stefan Krug
# Lizenz: 		CC BY 3.0 DE Dieses Werk ist lizenziert unter einer Creative Commons Namensnennung 3.0 Deutschland Lizenz. (http://creativecommons.org/licenses/by/3.0/de/)
# Stand:		2020-04-09
-->

<xsl:template match="/">
	<article>
	<!-- includiert alle Elemente vor der Tabelle, kapselt diese im <document>-Tag und schafft somit valides XML -->
		<xsl:apply-templates />
	<!-- Elemente nach der Tabelle landen hier -->
	</article>
</xsl:template>

<xsl:template match='title'>
	<title>
		<xsl:value-of select='.'/>
	</title>
</xsl:template>

<xsl:template match='ul[@id="pagehistory"]'>		<!-- match: <ul id="pagehistory"> -->
		<versions>
			<xsl:for-each select="li">
				<version>
					<id><xsl:value-of select="@data-mw-revid"/></id>
					<timestamp>	<!-- zur Filterung -->
						<xsl:call-template name="formatDateChinese">
							<xsl:with-param name="dateTime" select='*[@class="mw-changeslist-date"]' />
							<xsl:with-param name="outputType" select="1" />
						</xsl:call-template>
					</timestamp>
					<date>	<!-- lesbares Datum -->
						<xsl:call-template name="formatDateChinese">
							<xsl:with-param name="dateTime" select='*[@class="mw-changeslist-date"]' />
							<xsl:with-param name="outputType" select="2" />
						</xsl:call-template>
					</date>
					<time>	<!-- lesbare Zeit -->
						<xsl:call-template name="formatDateChinese">
							<xsl:with-param name="dateTime" select='*[@class="mw-changeslist-date"]' />
							<xsl:with-param name="outputType" select="3" />
						</xsl:call-template>
					</time>
					<user>	<!-- match: <bdi> auf einer variablen Tiefe zu <li> -->
						<xsl:value-of select=".//bdi"/>
					</user>			
					<minoredit>	<!-- Kennzeichen fuer kleine Aenderungen -->
						<xsl:choose>
							<xsl:when test='.//@class="minoredit"'>1</xsl:when>
							<xsl:otherwise>0</xsl:otherwise>
						</xsl:choose>
					</minoredit>
					<comment>	<!-- Aenderungskommentar -->
						<xsl:value-of select='*[@class="comment comment--without-parentheses"]'/>
					</comment>
				</version>
			</xsl:for-each>
		</versions>
</xsl:template>

<!--	___formatDateChinese (dateTime)___
	Parameter:	- dateTime (string)
				- outputType (int)	1 = YYYYMMDDhhmm; 2 = YYYY-MM-DD; 3 = hh:mm
				
	Template zum Aufloesen des chinesischen Timestamps gem. Parameter, um einfache Sortierung und Pruefung sowie lesbare Darstellung zu gewaehrleisten.
	Um Monat und Tag zu bestimmen, muessen folgende Variationen augeloest werden:
	- 2020年1月4日 (六) 10:20 | 2019年12月18日 (三) 07:19 | 2019年11月2日 (六) 19:16 | 2019年2月12日 (六) 01:01
	- Die variable Länge der Monats- und Tagesangabe ist fuer die Zerlegung des Strings das Kernproblem.
	Implementation über Prüfung auf Datentyp Zahl:
	- 6+7 != Zahl?				(6 und 7 markieren die Stellen innerhalb der Zeichenkette)
		- ja: 6 = Monat			(7 ist folglich ein Schriftzeichen)
			- 8+9 != Zahl?
				- ja: 8 = Tag
				- nein: 8+9 = Tag
		- nein: 6+7 = Monat		(8 ist somit ein Schriftzeichen)
			- 9+10 != Zahl?
				- ja: 9 = Tag
				- nein: 9+10 = Tag	-->
<xsl:template name="formatDateChinese">
	<xsl:param name="dateTime" />
	<xsl:param name="outputType"/>
	<xsl:variable name="year" select="substring($dateTime, 1, 4)" />			<!-- uebernimmt die ersten vier Zeichen von dateTime als Jahreszahl -->
	<xsl:variable name="month">
		<xsl:choose>
			<!-- Stelle 6+7 sind keine Zahl -> Stelle 6 definiert den Monat, mit fuehrender 0-->
			<xsl:when test="string(number(substring($dateTime, 6, 2))) = 'NaN'"> 
				<xsl:value-of select='concat("0", substring($dateTime, 6, 1))'/>
			</xsl:when>
			<!-- Stelle 6+7 sind eine Zahl -> Stellen 6+7 definieren den Monat -->
			<xsl:when test="string(number(substring($dateTime, 6, 2))) != 'NaN'"> 
				<xsl:value-of select="substring($dateTime, 6, 2)"/>	
			</xsl:when>
			<xsl:otherwise>00</xsl:otherwise>
		</xsl:choose>
	</xsl:variable>
	<xsl:variable name="day">
		<xsl:choose>
			<!-- Stellen 6+7 sowie 8+9 sind keine Zahl -> Stelle 8 definiert den Tag, mit fuehrender 0 -->
			<xsl:when test="string(number(substring($dateTime, 6, 2))) = 'NaN' and string(number(substring($dateTime, 8, 2))) = 'NaN'"> 
				<xsl:value-of select='concat("0", substring($dateTime, 8, 1))'/>		
			</xsl:when>
			<!-- Stellen 6+7 sind keine Zahl, 8+9 sind eine Zahl -> Stellen 8+9 definieren den Tag -->
			<xsl:when test="string(number(substring($dateTime, 6, 2))) = 'NaN' and string(number(substring($dateTime, 8, 2))) != 'NaN'"> 
				<xsl:value-of select='substring($dateTime, 8, 2)'/>		
			</xsl:when>
			<!-- Stellen 6+7 sind eine Zahl, 9+10 sind keine Zahl -> Stelle 9 definiert den Tag, mit fuehrender 0 -->
			<xsl:when test="string(number(substring($dateTime, 6, 2))) != 'NaN' and string(number(substring($dateTime, 9, 2))) = 'NaN'"> 
				<xsl:value-of select='concat("0", substring($dateTime, 9, 1))'/>		
			</xsl:when>
			<!-- Stellen 6+7 sowie 9+10 sind eine Zahl -> Stellen 9+10 definieren den Tag -->
			<xsl:when test="string(number(substring($dateTime, 6, 2))) != 'NaN' and string(number(substring($dateTime, 9, 2))) != 'NaN'"> 
				<xsl:value-of select='substring($dateTime, 9, 2)'/>		
			</xsl:when>
			<xsl:otherwise>00</xsl:otherwise>
		</xsl:choose>
	</xsl:variable>
	<!--	Template zum Aufloesen des chinesischen Timestamps nach hhmm, um eine einfache Sortierung und Pruefung zu gewaehrleisten. 
	Vorlage: 2020年1月4日 (六) 10:20 -->
	<xsl:variable name="hour" select="substring($dateTime, number(string-length($dateTime))-4, 2)"/>
	<xsl:variable name="minute" select="substring($dateTime, number(string-length($dateTime))-1, 2)"/>
	<xsl:choose>
		<xsl:when test="$outputType = 1">
			<xsl:value-of select="concat($year,$month,$day,$hour,$minute)"/>
		</xsl:when>
		<xsl:when test="$outputType = 2">
			<xsl:value-of select="concat($year,'-',$month,'-',$day)"/>
		</xsl:when>
		<xsl:when test="$outputType = 3">
			<xsl:value-of select="concat($hour,':',$minute)"/>
		</xsl:when>
	</xsl:choose>
</xsl:template>
</xsl:stylesheet>