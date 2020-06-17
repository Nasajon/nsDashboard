from redash.app import create_app
from redash.utils import users
from multiprocessing import freeze_support, Process
import getopt
import sys
import os 

def create_user(email,name,tenant,password,admin):
    app = create_app()
    with app.app_context():
        users.create(email,name,tenant,password,admin)

if __name__ == '__main__':
    freeze_support()
    
    opts, args = getopt.getopt(sys.argv[1:], "u:s:p:i:b:",["user_name=","user_email=","user_tenant=","user_password=","admin"])
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
        name = None
        email=None
        tenant=None
        password=None
        admin=False
        for opt, arg in opts:
            if opt == '--user_name':
                name = arg
            elif opt == '--user_email':
                email = arg
            elif opt == '--user_tenant':
                tenant = arg
            elif opt == '--user_password':
                password = arg
            elif opt == '--admin':
                admin=True

        if name != None and email != None and tenant != None and password != None:
            #Permite a aplicação flask acessar a variável de ambiente REDASH_DATABASE_URL configurada anteriormente
            p = Process(target=create_user,args=[name,email,tenant,password,admin])
            p.start()
            p.join()
        else:
            print("Usuário não informado")    
    else:
        print("Banco não informado")
        
        