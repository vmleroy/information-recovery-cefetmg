from typing import Optional

from bs4 import BeautifulSoup
from threading import Thread, Lock
import requests
from urllib.parse import urlparse, urljoin, ParseResult


class PageFetcher(Thread):
    def __init__(self, obj_scheduler):
        super().__init__()
        self.obj_scheduler = obj_scheduler

    def request_url(self, obj_url: ParseResult) -> Optional[bytes] or None:
        """
        :param obj_url: Instância da classe ParseResult com a URL a ser requisitada.
        :return: Conteúdo em binário da URL passada como parâmetro, ou None se o conteúdo não for HTML
        """

        response = requests.get(url=obj_url.geturl(), headers={'User-Agent': self.obj_scheduler.usr_agent})
        return response.content if 'text/html' in response.headers['Content-Type'] else None

    def discover_links(self, obj_url: ParseResult, depth: int, bin_str_content: bytes):
        """
        Retorna os links do conteúdo bin_str_content da página já requisitada obj_url
        """
        soup = BeautifulSoup(bin_str_content, features="lxml")
        for link in soup.select("body a"):
            if not link.has_attr('href'): # Se não tiver o atributo href, pula para o próximo link
                continue # continue é como um break, mas não sai do loop
            href = link['href']
            if "://" not in href: # Se não for um link absoluto, transforma em absoluto (ex: /about -> http://www.google.com/about, # -> http://www.google.com/#, etc.) 
                href = urljoin(obj_url.geturl(), href)
            new_depth = depth + 1
            if obj_url.hostname not in href: # Se o link não for do mesmo domínio, adiciona o novo domínio na fila com profundidade 0
                new_depth = 0
            yield urlparse(href), new_depth

    def crawl_new_url(self):
        """
        Coleta uma nova URL, obtendo-a do escalonador
        """
        url, depth = self.obj_scheduler.get_next_url()
        if url is not None:
            if self.obj_scheduler.can_fetch_page(url): # Verifica se pode requisitar a página
                base_html = self.request_url(url) # Requisita a página
                if base_html is not None:                    
                    print(f'URL: {url.geturl()}')
                    self.obj_scheduler.count_fetched_page() # Conta a página requisitada
                    for obj_new_url, new_depth in self.discover_links(url, depth, base_html): # Descobre os links da página requisitada
                        self.obj_scheduler.add_new_page(obj_new_url, new_depth) # Adiciona os links na fila

    def run(self):
        """
        Executa coleta enquanto houver páginas a serem coletadas
        """
        while not self.obj_scheduler.has_finished_crawl():
            try:
                self.crawl_new_url()
            except Exception as e:
                print(f'Error: {e}')
