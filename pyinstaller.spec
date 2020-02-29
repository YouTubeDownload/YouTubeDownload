block_cipher = None

a = Analysis(['qt_gui.py', 'qt_assets/main.py'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

a.datas += [
    ('assets/ytdl.png', './assets/ytdl.png', 'DATA'),
    ('qt_assets/Main.ui', './qt_assets/Main.ui', 'DATA'),
    ('qt_assets/dialogs/About.ui', './qt_assets/dialogs/About.ui', 'DATA'),
    ('qt_assets/dialogs/Error.ui', './qt_assets/dialogs/Error.ui', 'DATA'),
    ('qt_assets/tabs/tab_download.ui', './qt_assets/tabs/tab_download.ui', 'DATA'),
    ('qt_assets/tabs/tab_not_yet.ui', './qt_assets/tabs/tab_not_yet.ui',  'DATA'),
    ]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          a.binaries,
          name='YouTube Download',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon='assets\\ytdl.ico')
