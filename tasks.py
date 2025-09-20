import os
from celery_worker import celery_app
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

@celery_app.task
def playlist_downloader(url, local):
    try:   
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(local,'%(playlist)s','%(title)s.%(ext)s'),
            'ignoreerrors': True,
            'cookiefile': '/home/seu_usuario/nome-do-repositorio/cookies.txt',
            # 'progress_hooks': [progresso_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': False,
        }
        #lista dos arquivos que estavam antes do download
        arquivos_antes = set(os.listdir(local))
        with YoutubeDL(ydl_opts) as ydl:
            try:
                #trecho so pra ver se o video eh privado, se for, ele retorna uma string 'privado'
                info = ydl.extract_info(url, download= False)
                print('Titulo: ', info.get('title'))
                ydl.download([url])
            except DownloadError as e:
                if "private" in str(e).lower() or 'sign in' in str(e).lower():
                    return 'privado'
                else:
                    print(f'ERRO: {e}')
                    return f'ERRO {e}'
        #lista dos arquivos que estava depois do download
        arquivos_depois = set(os.listdir(local))
        #retorna um conjunto ser() com o nome da nova pasta
        nova_pasta = arquivos_depois - arquivos_antes

        #verifica se a pasta nao esta vazia
        if nova_pasta:
            #tira o nome da pasta da lista e joga pra variavel "nome_da_nova_pasta"
            nome_da_nova_pasta = nova_pasta.pop()
            #pega o caminho completo dessa nova pasta
            caminho_da_pasta = os.path.join(local, nome_da_nova_pasta)

            #verifica se eh realmente eh uma pasta
            if os.path.isdir(caminho_da_pasta):
                # verifica os arquivos dentro dessa pasta e ve se baixou algum .mp3
                for arquivo in os.listdir(caminho_da_pasta):
                    if arquivo.endswith('.mp3'):
                        #se sim, retorna o nome da pasta,q eh o nome da playlist
                        return {
                            'type': 'playlist',
                            'name': nome_da_nova_pasta
                        }
        #caso nada for baixado retorna None
        return None
    
    except Exception as e:
        print(f'\n[ERRO] ocorreu um erro no servidor: {e}')
        return None

@celery_app.task
def mp3_downloader(url, local):
    try:   
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(local, '%(title)s.%(ext)s'),
            'cookiefile': '/home/seu_usuario/nome-do-repositorio/cookies.txt',
            # 'progress_hooks': [progresso_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
        }
        
        #fazer a mesmo verificacao se baixou algo porem apenas com um arquivo agora
        
        arquivos_antes = set(os.listdir(local))#faz uma lista dos arquivos da pasta antes do download
        with YoutubeDL(ydl_opts) as ydl:
            try:
                #trecho so pra ver se o video eh privado, se for, ele retorna uma string 'privado'
                info = ydl.extract_info(url, download= False)
                print('Titulo: ', info.get('title'))
                ydl.download([url])
            except DownloadError as e:
                if "private" in str(e).lower() or 'sign in' in str(e).lower():
                    return 'privado'
                else:
                    print(f'ERRO: {e}')
                    return f'ERRO {e}'

        #ve se tem algo novo
        arquivos_depois = set(os.listdir(local))
        novos_arquivos = arquivos_depois - arquivos_antes

        for nome in novos_arquivos:
            if nome.endswith(".mp3"):
                return {
                    'type': 'arquivo',
                    'name': nome
                }
        return None
    except Exception as e:
        print(f'\n[ERRO] Ocorreu um erro no servidor: {e}')
        return None