# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Mockachu
Builds cross-platform executables for the desktop application
"""

import sys
import os
from pathlib import Path

# Get the absolute path of the project root
project_root = Path(SPECPATH).absolute()
src_path = project_root / "mockachu"

# Application info
app_name = "Mockachu"
version = "1.0.0"

# Platform-specific configurations
try:
    # Try to set icon files, but gracefully handle missing Pillow
    if sys.platform == "win32":
        icon_file = str(project_root / "mockachu" / "res" / "icon.ico") if (project_root / "mockachu" / "res" / "icon.ico").exists() else None
        executable_name = f"{app_name}.exe"
    elif sys.platform == "darwin":
        icon_file = str(project_root / "mockachu" / "res" / "icon.icns") if (project_root / "mockachu" / "res" / "icon.icns").exists() else None
        executable_name = app_name
    else:  # Linux
        icon_file = str(project_root / "mockachu" / "res" / "icon.png") if (project_root / "mockachu" / "res" / "icon.png").exists() else None
        executable_name = app_name.lower()
except Exception as e:
    print(f"Warning: Icon handling failed: {e}")
    print("Building without custom icon...")
    icon_file = None
    if sys.platform == "win32":
        executable_name = f"{app_name}.exe"
    elif sys.platform == "darwin":
        executable_name = app_name
    else:  # Linux
        executable_name = app_name.lower()

# Data files to include
datas = []

# Include all resource files
res_dir = src_path / "res"
if res_dir.exists():
    datas.append((str(res_dir), "mockachu/res"))

# Include UI resources
ui_res_dir = src_path / "ui" / "res"
if ui_res_dir.exists():
    datas.append((str(ui_res_dir), "mockachu/ui/res"))

# Include UI styles
ui_styles_dir = src_path / "ui" / "styles"
if ui_styles_dir.exists():
    datas.append((str(ui_styles_dir), "mockachu/ui/styles"))

# Include localization files
localization_dir = src_path / "localization"
if localization_dir.exists():
    datas.append((str(localization_dir), "mockachu/localization"))

# Hidden imports for PyQt6 and other dependencies
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtPrintSupport',
    'qdarkstyle',
    'mockachu.generators',
    'mockachu.ui',
    'mockachu.services',
    'mockachu.localization',
    'numpy',
    'pandas',
    'ujson',
    'ulid',
    'blinker',
    'flask',
    'flask_cors',
    'flask_restx',
    'werkzeug',
    'werkzeug.serving',
    'threading',
    'socketserver',
    'flask_restx',
    'dateutil',
    'pytz',
    'requests',
]

# Exclude unnecessary modules to reduce size
excludes = [
    'tkinter',
    'matplotlib',
    'scipy',
    'IPython',
    'jupyter',
    'notebook',
    'PIL.ImageTk',
    'PIL.ImageQt',
    'PIL._imagingcms',
]

# Analysis
a = Analysis(
    ['app.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Windows executable
if sys.platform == "win32":
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=executable_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,  # Disable UPX compression to reduce false positives
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # Windows app, not console
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        version='version_info.txt' if os.path.exists('version_info.txt') else None,
        icon=icon_file,
        # Additional options to reduce false positives
        manifest='mockachu.manifest' if os.path.exists('mockachu.manifest') else None,
        uac_admin=False,
        uac_uiaccess=False,
    )

# macOS app bundle
elif sys.platform == "darwin":
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=executable_name,
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
        name=executable_name,
    )
    
    app = BUNDLE(
        coll,
        name=f'{app_name}.app',
        icon=icon_file,
        bundle_identifier='org.mockdatagenerator.app',
        version=version,
        info_plist={
            'CFBundleName': 'Mockachu',
            'CFBundleDisplayName': 'Mockachu',
            'CFBundleIdentifier': 'org.mockdatagenerator.app',
            'CFBundleVersion': version,
            'CFBundleShortVersionString': version,
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
        },
    )

# Linux executable
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=executable_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file,
    )
