from redash.app import create_app
from redash.utils import rq
from multiprocessing import Pool, freeze_support
import os
import webbrowser
import psutil
import sys
import getopt
from flask.cli import load_dotenv
app = create_app()


def run_process(process):
    if process == 0:
        app.run()
    elif process == 1:
        with app.app_context():
            rq.worker()
    elif process == 2:
        rq.scheduler()
    elif process == 3:
        webbrowser.open('http://localhost:5000')

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
        else:
            load_dotenv()

        os.system('powershell -executionPolicy bypass "Start-Process -WindowStyle hidden -FilePath redis-server.exe"')
        freeze_support()
        pool = Pool(4)
        pool.map(run_process, range(4))
    else:
        webbrowser.open('http://localhost:5000')
