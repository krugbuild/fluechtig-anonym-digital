<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- 
## user.xsl
## Siehe auch history.xsl
# 
# Autor: 		Alexandra Krug
# Lizenz: 		CC BY 3.0 DE Dieses Werk ist lizenziert unter einer Creative Commons Namensnennung 3.0 Deutschland Lizenz. (http://creativecommons.org/licenses/by/3.0/de/)
# Stand:		2020-05-06

-->

<xsl:variable name="lang" select="//@lang" />

<xsl:template match="/">
	<user>
		<language><xsl:value-of select="$lang"/></language>
		<xsl:apply-templates />
	</user>
</xsl:template>

<xsl:template match='link[@rel="canonical"]'>
	<name>
		<!-- Seitenaufruf muss unbedingt mit dem Parameter "&target=" enden ! -->
		<xsl:value-of select='substring-after(@href, "target=")'/>
	</name>
</xsl:template>

<xsl:template match='ul[@class="mw-contributions-list"]'>		<!-- match: <ul class="mw-contributions-list"> -->
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
					<comment>	<!-- Aenderungskommentar -->
						<xsl:value-of select='*[@class="autocomment"]'/>
					</comment>
				</version>
			</xsl:for-each>
		</versions>
</xsl:template>

</xsl:stylesheet>