import time
from urllib.parse import urlparse

from crawler import page_fetcher, scheduler

def main_test_crawler():
  start = time.time()
  usr_agent = "crawler-bot"
  depth_limit = 6
  page_limit = 50000
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
                    'https://www.correiobraziliense.com.br;',
                  ]
  parsed_webpage_seeds = [urlparse(url) for url in webpage_seeds]

  obj_scheduler = scheduler.Scheduler(usr_agent, page_limit, depth_limit, parsed_webpage_seeds)


  page_fetcher_num = 10
  obj_process = []
  for i in range(page_fetcher_num):
    obj_process.append(page_fetcher.PageFetcher(obj_scheduler))
    obj_process[i].start()

  for p in obj_process:
    p.join()

  print("Fim da coleta")
  print("Quantidade de páginas coletadas: ", obj_scheduler.page_count)
  print("Quantidade de URLS: ", len(obj_scheduler.set_discovered_urls))
  end = time.time()
  print("Tempo total: ", end - start)
  
  
  