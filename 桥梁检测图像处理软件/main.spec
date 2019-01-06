# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['D:\\\xd7\xd4\xbc\xba\xd7\xf6\xb5\xc4\xc4\xc7\xd0\xa9\xce\xc4\xbc\xfe\\\xbf\xc6\xd1\xd0\xd1\xa1\xcc\xe2\\\xc7\xc5\xc1\xba\xbc\xec\xb2\xe2\xcd\xbc\xcf\xf1\xb4\xa6\xc0\xed\xc8\xed\xbc\xfe'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')
