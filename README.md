# YouTube MP3 Downloader Web App
Este é um aplicativo web completo construído com Flask e Celery que permite aos usuários baixar o áudio de vídeos ou playlists do YouTube em formato MP3. A aplicação é projetada para ser robusta, lidando com downloads demorados em segundo plano sem travar a interface do usuário.

Este projeto foi totalmente implantado em um Droplet da DigitalOcean, utilizando uma arquitetura de produção com Nginx, Gunicorn, Celery e Redis.

## ✨ Funcionalidades
- Download de Vídeo Único ou Playlist: Permite ao usuário escolher entre baixar um único arquivo MP3 ou uma playlist inteira.

- Processamento em Segundo Plano: Utiliza Celery e Redis para enfileirar e processar os downloads, proporcionando uma experiência de usuário fluida e sem bloqueios.

- Status em Tempo Real: A interface atualiza o status do download (Processando, Concluído, Erro) em tempo real usando JavaScript para consultar o backend.

- Detecção de Conteúdo Privado: Verifica se um vídeo ou playlist é privado/indisponível antes de iniciar o download e informa o usuário.

- Autenticação com Cookies: Utiliza um arquivo de cookies para contornar verificações anti-bot do YouTube, garantindo maior estabilidade.

- Auto-limpeza: Os arquivos são automaticamente deletados do servidor após o usuário iniciar o download, economizando espaço em disco.

## 🛠️ Tecnologias Utilizadas
- Backend: Python, Flask, Celery

- Frontend: HTML, JavaScript (vanilla)

- Fila de Tarefas: Redis

- Download Engine: yt-dlp

- Servidor de Produção:

- Nginx (Proxy Reverso)

- Gunicorn (Servidor de Aplicação WSGI)

- Systemd (Gerenciador de Serviços)

- Ubuntu 22.04 (Sistema Operacional)
