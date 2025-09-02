import os
import shutil
from flask import Flask,render_template,request,send_from_directory, flash
from funcoes import mp3_downloader, playlist_downloader, url_verify

#crie a pasta downloads se ela nao existir
if not os.path.exists('downloads'):
    os.makedirs('downloads')

#nossa instancia app
app = Flask(__name__)

#Chave secreta necessaria pra usar o 'Flash'
app.secret_key='0101'

#define o local do download
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')

#rota principal que aceita GET e POST
@app.route('/', methods=['GET', 'POST'])
def pagina_inicial():
    #verifica se o usuario enviou algo, se sim, executa o codigo abaixo
    if request.method == 'POST':
        #pega a url digitada
        url = request.form.get('url')

        #pega o tipo de download selecionado
        tipo_download = request.form.get('tipo_download')

        #verifica se a url eh valida
        if url_verify(url):
            flash('URL invalida! Por favor, insira uma URL valida do YouTube')
            return render_template('index.html')
        
        flash("Seu Download foi iniciado. Por favor, aguarde...")

        #faz o download conforme o tipo desejado
        if tipo_download == 'video':
            nome_arquivo = mp3_downloader(url, DOWNLOAD_FOLDER)
        else:
            nome_pasta = playlist_downloader(url, DOWNLOAD_FOLDER)

            #ve se a pasta foi baixada
            if nome_pasta:
                #pega o camingo da pasta que foi criada
                caminho_da_pasta_criada = os.path.join(DOWNLOAD_FOLDER, nome_pasta)

                #esse vai ser o nome do arquivo zip que vai ser criado
                nome_arquivo_zip = f'{nome_pasta}.zip'

                #cria o arquivo zip
                shutil.make_archive(
                    base_name=os.path.join(DOWNLOAD_FOLDER, nome_pasta),
                    format='zip',
                    root_dir= caminho_da_pasta_criada
                )
                
                #manda pro usuario o arquivo zip
                return send_from_directory(DOWNLOAD_FOLDER, nome_arquivo_zip, as_attachment=True)
            else:
                nome_arquivo = None
        
        #manda o arquivo pro usuario caso exista um
        if nome_arquivo:
            return send_from_directory(DOWNLOAD_FOLDER, nome_arquivo, as_attachment=True)
        
        #caso nao ele manda uma mensagem de erro
        else:
            flash('Ocorreu um erro no Download. O video pode ser privado ou nao existir.')
            return render_template('index.html')
        
    #se nao ele so continua na pagina inicial
    return render_template('index.html')

#se tiver na main ele carrega a aplicacao (caso alguma funcao daqui for chamada em outro arquivo ele nao carrega tudo dnv)
if __name__ == '__main__':
    app.run(debug=True)