import time
from urllib.parse import urlparse
from crawler import page_fetcher, scheduler


def activity12_test():
    start = time.time()
    usr_agent = 'crawler-bot'
    depth_limit = 6
    page_limit = 30
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

    obj_scheduler = scheduler.Scheduler(
        usr_agent, page_limit, depth_limit, parsed_webpage_seeds)

    fetchers_qtd = 5
    obj_process = []
    for i in range(fetchers_qtd):
        obj_process.append(page_fetcher.PageFetcher(obj_scheduler))
        obj_process[i].start()

    for p in obj_process:
        p.join()

    print('Fim da coleta')
    print('Quantidade de páginas coletadas: ', obj_scheduler.page_count)
    print('Quantidade de URLS: ', len(obj_scheduler.set_discovered_urls))
    end = time.time()
    print('Tempo total: ', end - start)


def crawler_50k_pages():
    start = time.time()

    usr_agent = 'crawler-bot'

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
        'https://www.crunchyroll.com/pt-br/welcome',
    ]
    parsed_webpage_seeds = [urlparse(url) for url in webpage_seeds]

    depth_limit = 6
    page_limit = 50000
    obj_scheduler = scheduler.Scheduler(
        usr_agent, page_limit, depth_limit, parsed_webpage_seeds)

    fetchers_qtd = 16
    obj_process = []
    for i in range(fetchers_qtd):
        obj_process.append(page_fetcher.PageFetcher(obj_scheduler))
        obj_process[i].start()

    for p in obj_process:
        p.join()

    print('Fim da coleta')
    print('Quantidade de páginas coletadas: ', obj_scheduler.page_count)
    print('Quantidade de URLS: ', len(obj_scheduler.set_discovered_urls))
    end = time.time()
    print('Tempo total: ', end - start)


def thread_qty_func(thread_qty):
    usr_agent = 'crawler-bot'
    depth_limit = 3
    page_limit = 10
    webpage_seeds = [
        'http://www.globo.com/',
        'http://www.cnpq.br/',
        'http://www.uol.com.br/',
        # 'https://www.uai.com.br/',
        # 'https://www.terra.com.br/',
        # 'https://www.bbc.com/',
        # 'https://www.tecmundo.com.br/',
        # 'https://www.olhardigital.com.br/',
        # 'https://www.estadao.com.br/',
        # 'https://www.em.com.br/',
        # 'https://www.gazetadopovo.com.br/',
        # 'https://www.correiobraziliense.com.br/',
    ]
    parsed_webpage_seeds = [urlparse(url) for url in webpage_seeds]
    obj_scheduler = scheduler.Scheduler(
        usr_agent, page_limit, depth_limit, parsed_webpage_seeds)

    start = time.time()
    obj_process = []
    print('Iniciando coleta com ', thread_qty, ' threads')
    for i in range(thread_qty):
        obj_process.append(page_fetcher.PageFetcher(obj_scheduler))
        obj_process[i].start()

    for p in obj_process:
        p.join()

    end = time.time()
    run_time = end - start
    qty_per_sec = obj_scheduler.page_count/run_time
    print('Fim da coleta com ', thread_qty, ' threads')
    print('Tempo total: ', run_time)
    print('Quantidade de páginas coletadas por segundo: ', qty_per_sec)
    return (qty_per_sec, thread_qty)


def thread_qty_test():
    results = []
    for i in range(1, 20):
        results.append(thread_qty_func(i))
    for i in range(20, 100, 10):
        results.append(thread_qty_func(i))
    for result in results:
        qty_per_sec, thread_qty = result
        print(qty_per_sec, ' páginas coletadas por segundo com ',
              thread_qty, ' threads')
