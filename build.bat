@SET PYTHONPATH=%CD%
@SET PARAMS=-y --clean^
 --onefile^
 -p %PYTHONPATH%^
 --name "nsDash"^
 --add-data "client;client"^
 --add-data "redis-server.exe;."^
 --additional-hooks-dir "."^
 --hidden-import "pkg_resources.py2_warn"^
 --hidden-import "sqlalchemy.ext.baked"^
 --distpath "%NSBIN%"^
 --workpath "%NSDCU%"
             
@IF DEFINED JENKINS_HOME (
	@SET PARAMS=%PARAMS% --version-file "%WORKSPACE%\output\VersionInfo2"
)

@IF EXIST venv (
  @CALL @%CD%\venv\Scripts\deactivate.bat
)

@ECHO ##### Criando o ambiente virtual #####

@python -m venv --clear venv

@ECHO ##### Compilando o projeto #####

@CMD "/c @%CD%\venv\Scripts\activate.bat && @pip install -r requirements.txt && @pyinstaller %PARAMS% main.py && @%CD%\venv\Scripts\deactivate.bat"