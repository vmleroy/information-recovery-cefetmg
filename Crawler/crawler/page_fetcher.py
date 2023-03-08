from typing import Optional

from bs4 import BeautifulSoup
from threading import Thread
import requests
from urllib.parse import urlparse, urljoin, ParseResult


class PageFetcher(Thread):
    def __init__(self, obj_scheduler):
        super().__init__()
        self.obj_scheduler = obj_scheduler
        self.usr_agent = obj_scheduler.usr_agent

    def request_url(self, obj_url: ParseResult) -> Optional[bytes] or None:
        """
        :param obj_url: Instância da classe ParseResult com a URL a ser requisitada.
        :return: Conteúdo em binário da URL passada como parâmetro, ou None se o conteúdo não for HTML
        """

        response = requests.get(url=obj_url.geturl(), headers={'User-Agent': self.usr_agent})
        return response.content if 'text/html' in response.headers['Content-Type'] else None

    def discover_links(self, obj_url: ParseResult, depth: int, bin_str_content: bytes):
        """
        Retorna os links do conteúdo bin_str_content da página já requisitada obj_url
        """
        soup = BeautifulSoup(bin_str_content, features="lxml")
        for link in soup.select('a'):
            obj_new_url = None
            new_depth = None
            try:
                obj_new_url = urlparse(urljoin(obj_url.geturl(), link['href']))
            except KeyError:
                pass
            else: 
                if obj_new_url is not None:
                    new_depth = 0 if obj_new_url.hostname != obj_url.hostname else depth + 1
            yield obj_new_url, new_depth


    def crawl_new_url(self):
        """
        Coleta uma nova URL, obtendo-a do escalonador
        """
        url, depth = self.obj_scheduler.get_next_url()
        if url is not None:
            if self.obj_scheduler.can_fetch_page(url):
                bin_str_content = self.request_url(url)
                if bin_str_content is not None:
                    for obj_new_url, new_depth in self.discover_links(url, depth, bin_str_content):
                        if obj_new_url is not None:
                            self.obj_scheduler.add_new_page(obj_new_url, new_depth)

    def run(self):
        """
        Executa coleta enquanto houver páginas a serem coletadas
        """
        while not self.obj_scheduler.has_finished_crawl():
            self.crawl_new_url()
        print('Finished crawling')
        print(f'Page count: {self.obj_scheduler.page_count}')
        print(f'URL count: {len(self.obj_scheduler.set_discovered_urls)}')
        print(f'Domain count: {len(self.obj_scheduler.dic_url_per_domain)}')
