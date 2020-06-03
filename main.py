from flask.cli import run_command
from redash.cli import rq
from multiprocessing import Pool, freeze_support
import os
import webbrowser
import psutil

def run_process(process):
    if process == 0:
        run_command()
    elif process == 1:
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
        os.system('powershell -executionPolicy bypass "Start-Process -WindowStyle hidden -FilePath redis-server.exe"')
        freeze_support()
        pool = Pool(4)
        pool.map(run_process, range(4))
    else:
        webbrowser.open('http://localhost:5000')