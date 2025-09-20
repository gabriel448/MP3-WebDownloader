import os
import shutil
import tempfile
from flask import Flask,render_template,request,send_from_directory, flash, url_for, redirect,session,jsonify, send_file, after_this_request
from funcoes import url_verify
from tasks import mp3_downloader, playlist_downloader
from celery.result import AsyncResult
from celery_worker import celery_app

#crie a pasta downloads se ela nao existir
if not os.path.exists('downloads'):
    os.makedirs('downloads')

#nossa instancia app
app = Flask(__name__)

#Chave secreta necessaria pra usar o 'Flash'
app.secret_key='0101'

#define o local do download
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')

#rota principal que aceita GET e POST e um parametro opcional, caso o video for privado(olhar index.html linha:69)
@app.route('/',defaults = {'privado': False}, methods=['GET', 'POST'])
@app.route('/<privado>', methods=['GET', 'POST'])
def pagina_inicial(privado):

    #verifica se o video eh privado
    if privado:
        flash("Video privado")
        return redirect(url_for('pagina_inicial'))
    
    #verifica se o usuario enviou algo, se sim, executa o codigo abaixo
    if request.method == 'POST':

        #pega a url digitada
        url = request.form.get('url')

        #pega o tipo de download selecionado
        tipo_download = request.form.get('tipo_download')

        #verifica se a url eh valida
        if url_verify(url):
            flash('URL invalida! Por favor, insira uma URL valida do YouTube')
            return redirect(url_for('pagina_inicial'))

        #faz o download conforme o tipo desejado
        #o .delay eh uma funcionalidade do celary, isso manda a tarefa pra "lista de tarefas" no Redis e assim 
        #o download fica em segundo plano e a tela nao congela enquanto faz o download
        if tipo_download == 'video':
            
            #pegamos o retorno do delay em uma variavel task
            task = mp3_downloader.delay(url, DOWNLOAD_FOLDER)
        else:
            task = playlist_downloader.delay(url, DOWNLOAD_FOLDER)

        #retornamos a pagina tarefa com a task_id criada para monitorar o status do download
        return redirect(url_for('pagina_tarefa', task_id=task.id))
    
    #retornamos o index.html em caso de get com a task_id como None
    return render_template('index.html', task_id=None)

#uma pagina tarefas exatamente igual a inicial porem com task_id, isso faz com que toda vez que a pagina inicial for chamada
#com GET a task_id eh apagada, iss evita o navegador ficar mostrando "Download concluido" depois que voce sai e entra na pagina
#assim sempre que abrimos o site temos a pagina limpa e etc..
@app.route('/task/<task_id>')
def pagina_tarefa(task_id):
    return render_template('index.html', task_id=task_id)

#nova rota pra verificar o status do download
@app.route('/status/<task_id>')
def task_status(task_id):

    #objeto do celery que tem todas a informacoes de uma task especifica atraves do seu id
    task = AsyncResult(task_id, app=celery_app)

    #verifica se esta pendente, em processamento, finalizado, ou se ocorreu um erro
    #gerando um dicionario com o stado(mais formal e oficial) e o status(oque significa na pratica)

    if task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': 'Processando...'
        }
        if task.state == 'SUCCESS':
            #aqui ele retorna o resultado que no caso eh o nome do arquivo mp3 que baixamos
            response = {
                'state': task.state,
                'status': 'Download conlcuido!!'
            }
            response['result'] = task.result
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }

    #retorna o dicionario em um JSON para o JS analisar e decidir oque fazer dependendo da situacao do download
    return jsonify(response)

@app.route('/downloads/<string:type>/<path:name>')
def download(type,name):

    #essa funcao so sera executada quando a download() retornar a reposta pro usuario(no caso baixar o arquivo)
    @after_this_request
    def delete_file(response):
        try:
            path = os.path.join(os.getcwd(), 'downloads', name)

            #verifica se eh uma pasta ou um arquivo, e deleta oque queremos de acordo
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f'{name} DELETADO DO SERVIDOR')
            return redirect(url_for('pagina_inicial'))

        except Exception as e:
            print(f'ERRO: {e}')
        return response
    if type == 'arquivo':
        return send_from_directory(DOWNLOAD_FOLDER, name, as_attachment=True)

    elif type == 'playlist':
        #pega o diretorio onde estao baixados os mp3s da playlist
        playlist_path = os.path.join(DOWNLOAD_FOLDER, name)

        #cria um nome temporario pro zip temporario (tmp.name retorna o diretorio exato desse zip temporario)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip')as tmp:
            zip_path = tmp.name
        
        #cria de fato o arquivo zip com todos os mp3s
        shutil.make_archive(zip_path.replace('.zip',''),'zip',playlist_path)

        #envia o zip pra download do usuario
        return send_file(zip_path, as_attachment=True, download_name=f'{name}.zip')
    
    else:
        return "tipo de download invalido", 400


#se tiver na main ele carrega a aplicacao (caso alguma funcao daqui for chamada em outro arquivo ele nao carrega tudo dnv)
if __name__ == '__main__':
    app.run(debug=True)