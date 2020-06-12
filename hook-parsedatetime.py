from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all( 'parsedatetime', include_py_files=False )