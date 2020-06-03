from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all( 'werkzeug', include_py_files=False )