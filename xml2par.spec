# -*- mode: python -*-
a = Analysis(['xml2par.py'],
             pathex=['.'],
             excludes=[ 'win32pdh','win32pipe',
                        'select', 'pydoc', 'pickle', '_hashlib', '_ssl',
                        'setuptools'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)               
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break             
a.datas = [x for x in a.datas if not ('mpl-data\\fonts' in os.path.dirname(x[1]))]                     
a.datas = [x for x in a.datas if not ('mpl-data\fonts' in os.path.dirname(x[1]))]                     
a.datas = [x for x in a.datas if not ('mpl-data\\sample_data' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('mpl-data\sample_data' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tk8.5\msgs' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tk8.5\images' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tk8.5\demos' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tcl8.5\opt0.4' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tcl8.5\http1.0' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tcl8.5\encoding' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tcl8.5\msgs' in os.path.dirname(x[1]))]               
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='xml2par.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True, icon='xml2par.ico')          
