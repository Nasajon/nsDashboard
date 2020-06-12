from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all( 'redash', include_py_files=False )