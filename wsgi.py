from app import app

# Esta parte é opcional para o Gunicorn, mas é uma boa prática.
# Permite que você execute este arquivo diretamente com 'python wsgi.py' para testes.
if __name__ == "__main__":
    app.run()