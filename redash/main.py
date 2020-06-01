
from flask.cli import run_command
from redash.cli import rq
from multiprocessing import Pool, Process
import signal   
import os
import psutil
import webbrowser
import werkzeug
                                             
def run_process(process):                                                             
    try:
        if process == 0:
            run_command()
        elif process == 1:
            rq.worker()
        elif process == 2:
            rq.scheduler()
        elif process == 3:
            webbrowser.open('http://localhost:5000')
    except KeyboardInterrupt as e:
        print("processo {} erro".format(process))
        print(str(e))
        return 0

    print("processo {} normal".format(process))
    return 1

if __name__ == '__main__':
    os.system('powershell -executionPolicy bypass "Start-Process -WindowStyle hidden -FilePath F:\\CFB\\redis-latest\\redis-server.exe"')
    pool = Pool(4)
    try:
        pool.map_async(run_process, range(4))    
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
    
    
    # Start-Process -WindowStyle hidden -FilePath F:\CFB\redis-latest\redis-server.exe