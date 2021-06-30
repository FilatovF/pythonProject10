from datetime import datetime

import requests
from bs4 import BeautifulSoup
import dataclasses


@dataclasses.dataclass
class Image:
    link: str
    alt: str


@dataclasses.dataclass
class News:
    title: str
    full_text: str
    news_data: datetime
    autohr: str
    images: list[Image] = dataclasses.field(default_factory=lambda: [])


class LigaTek:
    def __init__(self):
        self.ses = requests.Session()

    def __iter__(self):
        self.num_page = 1
        self.load_news_list()
        self.max_page = self.max_page_number()
        self.inx = -1

        return self

    def max_page_number(self) -> int:
        nav_block = self.curent_news_page.find('div', class_='pages')
        return max(int(a.text) for a in nav_block.find_all('a') if a.text.isdigit())

    def load_news(self, link) -> News:
        page = self._load(link)
        title = page.h1.text.strip()
        full_text = page.find('div', id='news-text').text
        news_data = datetime.strptime(page.find('div', class_='article-time').text, '%d.%m.%Y, %H:%M')
        autohr = ''
        if page.find('div', class_='authors'):
            autohr = page.find('div', class_='authors').text
        elif   page.find('div', class_='author'):
            autohr = page.find('div', class_='author').text
        all_images_div = page.find_all('div', class_='content-image')
        images = []
        for d in all_images_div:
            if d.find('img'):
                images.append(Image(d.find('img').attrs.get('src'),d.find('img').attrs.get('title')))

        return News(title, full_text, news_data, autohr, images)


    def __next__(self):
        news_ul = self.curent_news_page.find('ul', class_='news')
        if news_ul is None:
            raise StopIteration
        a = news_ul.find_all('a')
        my_links = []
        for i in a:
            if 'href' in i.attrs and i.attrs['href']:
                my_links.append(i.attrs['href'])
        self.inx += 1
        if self.inx < len(my_links):
            return self.load_news(my_links[self.inx])
        self.num_page += 1
        if self.num_page > self.max_page:
            raise StopIteration
        self.load_news_list()
        self.inx = -1
        return self.__next__()

    def _load(self, link) -> BeautifulSoup:
        page = self.ses.get(link)
        if page.ok:
            return BeautifulSoup(page.content, 'html.parser')
        raise Exception('ошибка связи с сервером')

    def load_news_list(self):
        self.curent_news_page = self._load('https://tech.liga.net/technology/page' + str(self.num_page))


if __name__ == '__main__':
    for link in LigaTek():
        input(link)
