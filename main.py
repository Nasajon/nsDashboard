from redash.app import create_app
from redash.utils import rq, data_sources, events
from multiprocessing import Pool, freeze_support
import os
import webbrowser
import psutil
import sys
import getopt
import dotenv
from functools import partial
import requests
import subprocess
app = create_app()

def run_process(process, ds_options, user, password):
    try:
        if process == 0:
            with app.app_context():
                events.record("iniciando_app","log",None)
                app.run()
        elif process == 1:
            with app.app_context():
                rq.worker()
        elif process == 2:
            rq.scheduler()
        elif process == 3:
            with app.app_context():
                events.record("abrindo_browser","log",None)
            if user is not None and password is not None:
                webbrowser.open('http://localhost:5000/login?user={}&password={}'.format(user, password))
            else:
                webbrowser.open('http://localhost:5000/login')
        elif process == 4:
            with app.app_context():
                data_sources.new("Padrão", "pg_multi_tenant",ds_options)
    except Exception as e:
        with app.app_context():
            events.record("erro_process","log",{"process":process,"erro": str(e)})
        return 0

    return 1


if __name__ == '__main__':
    freeze_support()
    program_up = False
    for conn in psutil.net_connections():
        if conn.status == psutil.CONN_LISTEN and conn.laddr[1] == 5000:
            program_up = True
            break

    opts, args = getopt.getopt(sys.argv[1:], "u:s:p:i:b:", ["multiprocessing-fork","user=","password="])
    usuario = None
    senha = None
    porta = None
    ip = None
    banco = None
    user = None
    for opt, arg in opts:
        if opt == '-u':
            usuario = arg
        elif opt == '-s':
            senha = arg
        elif opt == '-p':
            porta = arg
        elif opt == '-i':
            ip = arg
        elif opt == '-b':
            banco = arg
        elif opt == '--user':
            user = arg
           
    if not program_up:
        if usuario != None and senha != None and porta != None and ip != None and banco != None:
            os.environ['REDASH_DATABASE_URL'] = "postgresql://{}:{}@{}:{}/{}".format(usuario, senha, ip, porta, banco)
            app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{}:{}@{}:{}/{}".format(usuario, senha, ip, porta, banco)
            ds_options = {"host":ip,"port":int(porta),"user":usuario,"password":senha,"dbname": banco}
        else:
            path = dotenv.find_dotenv('.env', usecwd=True)

            if path:
                dotenv.load_dotenv(path)
                ds_options = {"host":os.getenv("DB_HOST","localhost"),"port":int(os.getenv("DB_PORT","5432")),"user":os.getenv("DB_USER","postgres"),"password":os.getenv("DB_PASSWORD","postgres"),"dbname": os.getenv("DB_NAME","integratto2")}
            else:
                print("Arquivo env nao encontrado")

        with app.app_context():
            events.record("parametros_entrada","log",{"parametros": opts})
            events.record("conexao_banco","log",ds_options)

        bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        path_to_redis = os.path.join(bundle_dir, 'redis-server.exe')
        with app.app_context():
            events.record("iniciando_redis","log",{"path_redis":path_to_redis})
            try:
                output = subprocess.check_output('powershell -executionPolicy bypass "Start-Process -WindowStyle hidden -FilePath {}"'.format(path_to_redis))
                events.record("funcionando_redis","log",None)
                pool = Pool(5)
                pool.map(partial(run_process, ds_options=ds_options, user=user, password=senha), range(5))
            except subprocess.CalledProcessError as e:
                events.record("erro_redis","log",{"erro":str(e.output)})
            except Exception as e:
                events.record("erro_main","log",{"erro":str(e)})
    else:
        with app.app_context():
            events.record("abrindo_browser","log",None)
        if user is not None and senha is not None:
            webbrowser.open('http://localhost:5000/login?user={}&password={}'.format(user, senha))
        else:
            webbrowser.open('http://localhost:5000/login')
