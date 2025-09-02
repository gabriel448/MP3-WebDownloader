import os
import re
from yt_dlp import YoutubeDL


class CustomLogger:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        print(f'[AVISO] {msg}')

    def error(self, msg):
        print(f'[ERRO] ocorreu um problema: {msg}')

# def progresso_hook(d):
#     if d['status'] == 'downloading':
#         if d.get('total_bytes') is not None and d.get('downloaded_bytes') is not None:
#             perc_float = (d['downloaded_bytes']/d['total_bytes'])*100
#             percent = f'{perc_float:.1f}'
#         else:
#             percent = 'Unknow'
#             perc_float = 0.0
#         speed = d.get('_speed_str', '').strip()
#         eta = d.get('_eta_str', '').strip()

#         total_blocos = 30
#         blocos_preenchidos = int((perc_float/100)*total_blocos)
#         blocos_vazios = total_blocos - blocos_preenchidos
#         barra = Fore.GREEN + ('▇' * blocos_preenchidos) + Fore.WHITE + ('░'*blocos_vazios)

#         print(f"{Fore.GREEN}[⇩] Baixando: {percent} | Velocidade: {speed} | Tempo estimado: {eta} | {barra}      ", end='\r', flush=True)

#     elif d['status'] == 'finished':
#         total_blocos = 30
#         barra_completa = Fore.GREEN + '▇' * total_blocos
#         print(f"{Fore.GREEN}[⇩] Baixando: 100.0% | Velocidade: Unknown | Tempo estimado: 00:00 | {barra_completa}      ", end='\r', flush=True)
#         print(f"\n{Fore.GREEN}[✓] Download finalizado. Convertendo para MP3...", flush=True)

def playlist_downloader(url, local):
    try:   
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(local,'%(playlist)s','%(title)s.%(ext)s'),
            'ignoreerrors': True,
            # 'progress_hooks': [progresso_hook],
            'logger': CustomLogger(),
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
            ydl.download([url])
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
                        return nome_da_nova_pasta
        #caso nada for baixado retorna None
        return None
    
    except Exception as e:
        print(f'\n[ERRO] ocorreu um erro no servidor: {e}')
        return None

def mp3_downloader(url, local):
    try:   
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(local, '%(title)s.%(ext)s'),
            # 'progress_hooks': [progresso_hook],
            'logger': CustomLogger(),
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
            ydl.download([url])

        #ve se tem algo novo
        arquivos_depois = set(os.listdir(local))
        novos_arquivos = arquivos_depois - arquivos_antes

        for nome in novos_arquivos:
            if nome.endswith(".mp3"):
                return nome
        return None
    except Exception as e:
        print(f'\n[ERRO] Ocorreu um erro no servidor: {e}')
        return None

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

