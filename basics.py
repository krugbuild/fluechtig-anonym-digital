import requests
from bs4 import BeautifulSoup as bs

result = requests.get("https://www.google.com")

print(result.status_code)

src = result.content

soup = bs(src, 'lxml')

links = soup.find_all("a")  

for link in links:
    print(link.text)
    if "about" in link.attrs['href']:
        print('found it')
        print(link)
        print(link.attrs['href'])
