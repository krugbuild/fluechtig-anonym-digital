<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- 
## history.xsl
# Die Schemadatei dient dazu, das HTML-Dokument einer Wikipedia-Versionsgeschichte zu zerlegen und in eine auswertbare Struktur zu bringen.
# Das Tag <versions/> beinhaltet hierbei die zentrale Liste mit den einzelnen Versionen des zugehörigen Artikels. Der restliche Seiteninhalt wird entsprechend davor und dahinter im Tag <article/> gekapselt.
# Das Schema zerlegt die dargestellten Datumsangaben in das neutrale Format `YYYYMMDDhhmm` um eine einfache Verarbeitung zu gewährleisten. 
# Mit Stand 27.01.2020 ist nur die Zerlegung des in der chinesischen Wikipedia benutzten Datumsformat (etwa `2020年1月4日 (六) 10:20`) implementiert.
# Update 2020-04-09: <title> hinzugefügt.
# Update 2020-05-06:  Datum wird nun unverändert übernommen, Formatierung findet in usernetwork.py statt.
#
# Autor: 		Alexandra Krug
# Lizenz: 		CC BY 3.0 DE Dieses Werk ist lizenziert unter einer Creative Commons Namensnennung 3.0 Deutschland Lizenz. (http://creativecommons.org/licenses/by/3.0/de/)
# Stand:		2020-05-06
-->

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

<xsl:template match='ul[@id="pagehistory"]'>		<!-- match: <ul id="pagehistory"> -->
		<versions>
			<xsl:for-each select="li">
				<version>
					<id><xsl:value-of select="@data-mw-revid"/></id>
					<timestamp>	
						<xsl:value-of select='*[@class="mw-changeslist-date"]' />
					</timestamp>
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

</xsl:stylesheet>