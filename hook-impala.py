from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all( 'impala', include_py_files=False )