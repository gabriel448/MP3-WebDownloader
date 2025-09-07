import os
import shutil
from flask import Flask,render_template,request,send_from_directory, flash, url_for, redirect,session,jsonify
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
            return redirect(url_for('pagina_inicial'))

        #faz o download conforme o tipo desejado
        #o .delay eh uma funcionalidade do celary, isso manda a tarefa pra "lista de tarefas" no Redis e assim 
        #o download fica em segundo plano e a tela nao congela enquanto faz o download
        if tipo_download == 'video':
            #pegamos o retorno do delay em uma variavel task
            task = mp3_downloader.delay(url, DOWNLOAD_FOLDER)
        else:
            task = playlist_downloader.delay(url, DOWNLOAD_FOLDER)

        #setamos o id da task na sessao do usuario 
        session['task_id'] = task.id

        return redirect(url_for('pagina_inicial'))
    
    #pegamos o id da sessao do cliente se existir(se n so retorna none e ta suave)
    task_id = session.get('task_id')
    #entao ele retorna a pagina inicial com o id da sessao
    return render_template('index.html', task_id=task_id)

#nova rota pra verificar o status do download
@app.route('/status/<task_id>')
def task_status(task_id):
    #objeto do celery que tem todas a informacoes de uma task especifica atraves do seu id
    task = AsyncResult(task_id, app=celery_app)

    #verifica se esta pendente, em processamento, finalizado, ou se ocorreu um erro
    #gerando um dicionario com o stado(mais formal e oficial) e o status(oque significa na pratica)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Na fila...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': 'Processando...'
        }
        if task.state == 'SUCCESS':
            #aqui ele retorna o resultado que no caso eh o nome do arquivo mp3 que baixamos
            response['result'] = task.result
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }

    #retorna o dicionario em um JSON para o JS analisar e decidir oque fazer dependendo da situacao do download
    return jsonify(response)

#se tiver na main ele carrega a aplicacao (caso alguma funcao daqui for chamada em outro arquivo ele nao carrega tudo dnv)
if __name__ == '__main__':
    app.run(debug=True)

#teste