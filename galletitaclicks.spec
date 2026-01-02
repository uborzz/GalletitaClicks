# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['galletitaclicks.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pynput',
        'pynput.mouse',
        'pynput.keyboard',
        'pynput._util.darwin',
        'pyobjc_framework_Quartz',
        'pyobjc_framework_AppKit',
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
    name='GalletitaClicks',
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
    name='GalletitaClicks',
)

app = BUNDLE(
    coll,
    name='GalletitaClicks.app',
    icon='icon.icns',
    bundle_identifier='com.galletitaclicks.app',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'False',
        'LSMinimumSystemVersion': '10.13',
        'CFBundleName': 'GalletitaClicks',
        'CFBundleDisplayName': 'GalletitaClicks',
        'CFBundleIconFile': 'icon',
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': 'GalletitaClicks',
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSHumanReadableCopyright': 'Copyright © 2024',
        'NSAppleEventsUsageDescription': 'GalletitaClicks necesita controlar el mouse para realizar clicks automáticos.',
        'NSSystemAdministrationUsageDescription': 'GalletitaClicks necesita permisos de accesibilidad para controlar el mouse.',
    },
)

