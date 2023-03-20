from crawler.scheduler import Scheduler
from crawler.page_fetcher import PageFetcher
from urllib.parse import urlparse
import time
import matplotlib.pyplot as plt

USR_AGENT = 'Linkin-Crawken-Bot (https://vmleroy.github.io/ri-crawler-page/)'

arr_results = []

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

###################

def test(num_threads):
  scheduler = Scheduler(usr_agent=USR_AGENT, page_limit=100, depth_limit=10, arr_urls_seeds=parsed_webpage_seeds)

  obj_process = []

  start = time.time()
  for i in range(num_threads):
    obj_process.append(PageFetcher(scheduler))
    print(f'Thread {i} started, {obj_process[i].name}')
    obj_process[i].start()

  for fetcher in obj_process:
    fetcher.join()
    print(f'Joining {fetcher.name}')
  end = time.time()

  interval = end - start
  arr_results.append((num_threads, interval))

###################

def test_threads():
  arr_threads = [ x*5 for x in range(4)]
  arr_threads[0] = 1
  arr_threads += [ x*20+30 for x in range(4)]
  arr_threads.append(100)

  for t in arr_threads:
    test(t)

  x_coords = [coord[0] for coord in arr_results]
  y_coords = [coord[1] for coord in arr_results]

  print(arr_results)

  plt.plot(x_coords, y_coords)
  plt.xlabel('Threads')
  plt.ylabel('Time (s)')
  plt.title('Time x Threads')
  plt.show()
