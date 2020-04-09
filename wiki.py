import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia('en')

page_py = wiki_wiki.page('1989_Tiananmen_Square_protests:_Revision_history')

print(page_py.title+"\n")
text = page_py.text
print(page_py.wiki)