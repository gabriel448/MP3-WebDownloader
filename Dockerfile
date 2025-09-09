#define uma imagem base pra usar
FROM python:3.9-slim

#cria uma pasta chamada app pra organizar tudo dentro dessa pasta no container
WORKDIR /app

#copia o rquirements.txt e instala as dependecias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copia o projeto pra pasta app
COPY . .

#diz em que porta vai se comunicar e rodar, tipo um canal de walkie-talkie
EXPOSE 5000

#defini um comando pra iniciar a aplicacao web, usando o gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

