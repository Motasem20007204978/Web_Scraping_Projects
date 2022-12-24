
from time import sleep
from urllib.request import urlopen 
# urlopen is a function that opens a connection to a URL with file stream only
# like file.html or file.txt and so on.
from urllib.request import urlretrieve
from urllib.error import HTTPError
# to ahndle errors like 404, 500, etc
from urllib.error import URLError
# to handle errors like network connection errors, missed DNS, etc
import requests
from bs4 import BeautifulSoup

def connect_to_url_get_content(url:str):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
        return None
    except URLError as e:
        print(e)
        return None
    return html.read()

content_of_page = connect_to_url_get_content('https://www.practicepython.org/exercise/2016/08/03/29-tic-tac-toe-game.html')
# print(content_of_page.read())# get content encoded as bytes
# print(content_of_page.read().decode())# get content encoded as text

# as

content = requests.get('https://www.practicepython.org/exercise/2016/08/03/29-tic-tac-toe-game.html')
print(content.status_code)# as errors in urllib are handled by exceptions
# print(content.content)# get content encoded as bytes
# print(content.text)# get content encoded as text

soup = BeautifulSoup(content.text, 'lxml')
# parsers = ['html.parser', 'lxml', 'xml', 'html5lib']
# html.parser is the default parser
# lxml is a parser that is faster than html.parser, can fixes some errors like unclosed tags
# lxml can cause problems for portability and ease of use
# html5lib is like lxml but it is more modern, it is not compatible with older browsers
# xml is a parser that is used to parse xml files
print(soup.h1)#get the first h1 tag

# if the expected tag is not found, it will return None
print(soup.h1.p)#get None because there is no p tag in h1

try:
    print(soup.h1.p.u)#return attribute error because neither p nor text is found
except AttributeError as e:
    print(e)

# find and find_all are used to find specific tags
# can use css selector to find tags
# find_all returns a list of all the tags that match the selector

h1_tags = soup.find_all('h1')#get all h1 tags
for tag in h1_tags:
    print(tag.getText())#get the text of the tag

link_on_header = soup.find_all(class_='header')#get all tags with class header
for tag in link_on_header:
    print(tag.getText())#get the text of the tag and the href of the a tag

# to get children of a tag
for child in soup.h1.children:
    print(child)

# to get an attribute of a tag
print(soup.a.get('href'))#get the href of the first a tag
print(soup.a.attrs['href'])#get the class of the first a tag


content= requests.get('https://www.w3schools.com/html/html_tables.asp')
soup = BeautifulSoup(content.text, 'lxml')
table_childs = soup.find('table', {'id':'customers', 'class':'ws-table-all'}).find_all('tr')

first_row = table_childs[0]#get the first row

# use spilling to get next data in the same list
print(first_row.find('th').next_sibling.next_sibling.text)
# next_sibling is used to get the next sibling of the tag
# previous_sibling is used to get the previous sibling of the tag
# next_siblings is used to get all the next siblings of the tag
# previous_siblings is used to get all the previous siblings of the tag

# store the image in the same directory as the script
color_picker = soup.find('img', {'alt':'colorpicker'})
urlretrieve(color_picker.attrs['src'], 'colorpicker.png')