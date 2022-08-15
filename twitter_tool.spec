# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [('images/*.png', 'images'),
        ('roberta/*', 'roberta'),
        ('/Users/phutecker/opt/anaconda3/envs/TwitterTool/lib/python3.8/site-packages/customtkinter', 'customtkinter'),
        ('/Users/phutecker/opt/anaconda3/envs/TwitterTool/lib/python3.8/site-packages/huggingface_hub', 'huggingface_hub'),
        ('/Users/phutecker/opt/anaconda3/envs/TwitterTool/lib/python3.8/site-packages/transformers', 'transformers'),
        ('/Users/phutecker/opt/anaconda3/envs/TwitterTool/lib/python3.8/site-packages/importlib_metadata', 'importlib_metadata'),
        ('/Users/phutecker/opt/anaconda3/envs/TwitterTool/lib/python3.8/site-packages/wheel', 'wheel'),
        ('/Users/phutecker/opt/anaconda3/envs/TwitterTool/lib/python3.8/site-packages/setuptools', 'setuptools'),
        ('/Users/phutecker/opt/anaconda3/envs/TwitterTool/lib/python3.8/site-packages/tqdm', 'tqdm')]
datas += copy_metadata('tqdm')
datas += copy_metadata('regex')
datas += copy_metadata('requests')
datas += copy_metadata('packaging')
datas += copy_metadata('filelock')
datas += copy_metadata('numpy')
datas += copy_metadata('tokenizers')
datas += copy_metadata('torch')


block_cipher = None


a = Analysis(
    ['twitter_tool.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='twitter_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='twitter_tool',
)
