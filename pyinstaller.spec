block_cipher = None

a = Analysis(['gui.py'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

a.datas += [('assets\\ytdl.png', '.\\assets\\ytdl.png', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          a.binaries,
          name='YouTube Video & Audio Downloader',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon='assets\\ytdl.ico')
