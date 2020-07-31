from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all( 'pywebview', include_py_files=False )