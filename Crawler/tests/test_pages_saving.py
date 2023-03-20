import time
from urllib.parse import urlparse
from crawler import page_fetcher, scheduler

USR_AGENT = 'Linkin-Crawken-Bot (https://vmleroy.github.io/ri-crawler-page/)'


def test_1M_pages_saving_files():
  depth_limit = 6
  page_limit = 1000000
  webpage_seeds = [
                    'http://www.globo.com/',
                    'http://www.cnpq.br/', 
                    'http://www.uol.com.br/', 
                    'https://www.uai.com.br/', 
                    'https://www.terra.com.br/', 
                    'https://www.bbc.com/', 
                    'https://www.tecmundo.com.br/', 
                    'https://www.olhardigital.com.br/',
                    'https://www.estadao.com.br/', 
                    'https://www.em.com.br/',
                    'https://www.gazetadopovo.com.br/',
                    'https://www.correiobraziliense.com.br/',
                  ]
  parsed_webpage_seeds = [urlparse(url) for url in webpage_seeds]

  obj_scheduler = scheduler.Scheduler(USR_AGENT, page_limit, depth_limit, parsed_webpage_seeds)

  fetchers_qtd = 1000
  obj_process = []
  
  start = time.time()
  for i in range(fetchers_qtd):
    obj_process.append(page_fetcher.PageFetcher(obj_scheduler, save_file=True))
    obj_process[i].start()

  for p in obj_process:
    p.join()
  end = time.time()

  print('Fim da coleta')
  print('Quantidade de páginas coletadas: ', obj_scheduler.page_count)
  print('Quantidade de URLS: ', len(obj_scheduler.set_discovered_urls))
  print('Tempo total: ', end - start)

########################

def test_50k_pages_saving_files():
  depth_limit = 6
  page_limit = 50000
  webpage_seeds = [
                    'https://www.youtube.com/',
                    'https://crunchyroll.com/',
                    'https://www.reddit.com'
                  ]
  parsed_webpage_seeds = [urlparse(url) for url in webpage_seeds]

  obj_scheduler = scheduler.Scheduler(USR_AGENT, page_limit, depth_limit, parsed_webpage_seeds)

  fetchers_qtd = 16
  obj_process = []
  
  start = time.time()
  for i in range(fetchers_qtd):
    obj_process.append(page_fetcher.PageFetcher(obj_scheduler, save_file=True))
    obj_process[i].start()

  for p in obj_process:
    p.join()
  end = time.time()

  print('Fim da coleta')
  print('Quantidade de páginas coletadas: ', obj_scheduler.page_count)
  print('Quantidade de URLS: ', len(obj_scheduler.set_discovered_urls))
  print('Tempo total: ', end - start)