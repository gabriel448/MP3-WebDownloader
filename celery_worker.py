from celery import Celery

#define a url do "quadro de avisos" (Redis)
#o '0' no final refere ao banco de dados padrao do Redis
REDIS_URL = 'redis://localhost:6379/0'

#Cria a instancia do Celery
#tasks eh o nome do modulo de tarefas
#broker eh onde o celery vai buscar as novas tarefas
#backend eh onde o celery vai armazenar os resultados das tarefas
celery_app = Celery('tasks',
                    broker=REDIS_URL,
                    backend=REDIS_URL)

#aq so configurando o celery pra salvar a serializacao em .json
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)

#importar depois pois se nao vai virar um loop ja que o tasks importa o cerely_app logo no inicio
import tasks

