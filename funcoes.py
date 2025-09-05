import os

def url_verify(url):
    if not url.startswith(("http://", "https://")) or "youtu" not in url:
        return True
    return False

def local_verify(local):
    if local.strip() == "":
        return os.getcwd()
    try:
        if not os.path.exists(local):
            os.makedirs(local)
        return local
    except Exception as e:
        print(f'Erro ao criar ou acessar o diretorio: {e}')
        return 0

