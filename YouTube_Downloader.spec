# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_main.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates')],
    hiddenimports=[
        'flask',
        'yt_dlp',
        'werkzeug',
        'jinja2',
        'markupsafe',
        'itsdangerous',
        'click',
        'blinker',
        'certifi',
        'charset_normalizer',
        'idna',
        'urllib3',
        'requests',
        'websockets',
        'mutagen',
        'pycryptodome',
        'brotli',
        'certifi',
        'charset_normalizer',
        'idna',
        'urllib3',
        'requests',
        'websockets',
        'mutagen',
        'pycryptodome',
        'brotli'
    ],
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
    name='YouTube Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='YouTube Downloader',
)

app = BUNDLE(
    coll,
    name='YouTube Downloader.app',
    icon=None,
    bundle_identifier='com.youtubedownloader.app',
    info_plist={
        'CFBundleName': 'YouTube Downloader',
        'CFBundleDisplayName': 'YouTube Downloader',
        'CFBundleIdentifier': 'com.youtubedownloader.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.15.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSAppleEventsUsageDescription': 'This app needs to open your default web browser.',
    },
)
