from redash.app import create_app
from redash.utils import rq, data_sources
from multiprocessing import Pool, freeze_support
import os
import webbrowser
import psutil
import sys
import getopt
import dotenv
from functools import partial
app = create_app()

def run_process(process, ds_options):
    try:
        if process == 0:
            app.run()
        elif process == 1:
            with app.app_context():
                rq.worker()
        elif process == 2:
            rq.scheduler()
        elif process == 3:
            webbrowser.open('http://localhost:5000')
        elif process == 4:
            with app.app_context():
                data_sources.new("Padrão", "pg_multi_tenant",ds_options)
    except Exception as e:
        print(str(e))
        return 0

    return 1


if __name__ == '__main__':
    program_up = False
    for conn in psutil.net_connections():
        if conn.status == psutil.CONN_LISTEN and conn.laddr[1] == 5000:
            program_up = True
            break

    if not program_up:
        opts, args = getopt.getopt(sys.argv[1:], "u:s:p:i:b:", ["multiprocessing-fork"])
        usuario = None
        senha = None
        porta = None
        ip = None
        banco = None
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

        if usuario != None and senha != None and porta != None and ip != None and banco != None:
            os.environ['REDASH_DATABASE_URL'] = "postgresql://{}:{}@{}:{}/{}".format(usuario, senha, ip, porta, banco)
            ds_options = {"host":ip,"port":int(porta),"user":usuario,"password":senha,"dbname": banco}
        else:
            path = dotenv.find_dotenv('.env', usecwd=True)

            if path:
                dotenv.load_dotenv(path)
                ds_options = {"host":os.getenv("DB_HOST","localhost"),"port":int(os.getenv("DB_PORT","5432")),"user":os.getenv("DB_USER","postgres"),"password":os.getenv("DB_PASSWORD","postgres"),"dbname": os.getenv("DB_NAME","nasajon")}
            else:
                print("Arquivo env nao encontrado")
                sys.exit(1)

        os.system('powershell -executionPolicy bypass "Start-Process -WindowStyle hidden -FilePath redis-server.exe"')
        freeze_support()
        pool = Pool(5)
        pool.map(partial(run_process, ds_options=ds_options), range(5))
    else:
        webbrowser.open('http://localhost:5000')
