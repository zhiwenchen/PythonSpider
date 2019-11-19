from MyUtils import get_HTML_text,write_to_mysql
from bs4 import BeautifulSoup
url = 'https://book.douban.com/tag/?icn=index-nav'
html = get_HTML_text(url)
soup = BeautifulSoup(html,'lxml')
tags = soup.select('.tagCol td')
id = 1
for tag in tags:
    sort = tag.find('a').text
    number = tag.find('b').text[1:-1]
    write_to_mysql('book_tag',[id,sort,number])
    id += 1