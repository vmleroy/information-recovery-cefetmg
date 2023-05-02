from urllib.parse import ParseResult

def page_to_file(url: ParseResult, base_html: bytes):
    """
    Salva o conteúdo da página em um arquivo
    """
    urlStr = url.geturl()
    urlStr = urlStr[urlStr.find("://") + 3:].replace("/", "#").replace(":", "#").replace("?", "#").replace("&", "#")
    file_path = f'data/pages/{urlStr}.html'

    file = open(file_path, 'w')
    file.write(f'URL: {url.geturl()}\n\n')
    file.close()
    
    file = open(file_path, 'ab')
    file.write(base_html)
    file.close()