@echo off
echo Building Path Dumper...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import tkinter; import zipfile; import threading" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Required Python packages are not available
    echo Please install the required packages first
    pause
    exit /b 1
)

if not exist "build" mkdir build

echo Copying files...
copy main.py build\
xcopy /E /I locales build\locales
copy README*.md build\
copy requirements.txt build\

python -c "import PyInstaller" >nul 2>&1
if %errorlevel% equ 0 (
    echo Creating standalone executable with static linking...
    
    echo Creating spec file for static linking...
    (
    echo # -*- mode: python ; coding: utf-8 -*-
    echo.
    echo # Path Dumper Build Configuration
    echo # This tool creates directory structure archives with large file placeholders
    echo # Source: https://github.com/fernvenue/path-dumper-windows
    echo.
    echo block_cipher = None
    echo.
    echo a = Analysis^(['main.py'],
    echo              pathex=[],
    echo              binaries=[],
    echo              datas=[^('locales', 'locales'^)],
    echo              hiddenimports=[
    echo                  'tkinter',
    echo                  'tkinter.ttk',
    echo                  'tkinter.filedialog', 
    echo                  'tkinter.messagebox',
    echo                  'zipfile',
    echo                  'tempfile',
    echo                  'uuid'
    echo              ],
    echo              hookspath=[],
    echo              hooksconfig={},
    echo              runtime_hooks=[],
    echo              excludes=[
    echo                  'matplotlib',
    echo                  'numpy', 
    echo                  'scipy',
    echo                  'pandas',
    echo                  'requests',
    echo                  'urllib3',
    echo                  'subprocess',
    echo                  'os.system'
    echo              ],
    echo              win_no_prefer_redirects=False,
    echo              win_private_assemblies=False,
    echo              cipher=block_cipher,
    echo              noarchive=False^)
    echo.
    echo pyz = PYZ^(a.pure, a.zipped_data,
    echo              cipher=block_cipher^)
    echo.
    echo exe = EXE^(pyz,
    echo           a.scripts,
    echo           a.binaries,
    echo           a.zipfiles,
    echo           a.datas,
    echo           [],
    echo           name='PathDumper',
    echo           debug=False,
    echo           bootloader_ignore_signals=False,
    echo           strip=False,
    echo           upx=False,
    echo           upx_exclude=[],
    echo           runtime_tmpdir=None,
    echo           console=False,
    echo           disable_windowed_traceback=False,
    echo           target_arch=None,
    echo           codesign_identity=None,
    echo           entitlements_file=None,
    echo           version=None,
    echo           uac_admin=False,
    echo           uac_uiaccess=False^)
    ) > PathDumper.spec
    
    echo Building with PyInstaller...
    pyinstaller --clean PathDumper.spec
    
    if exist "dist\PathDumper.exe" (
        copy dist\PathDumper.exe build\
        echo Standalone executable created: build\PathDumper.exe
        echo Cleaning up temporary files...
        if exist "build\main" rmdir /s /q "build\main"
        if exist "__pycache__" rmdir /s /q "__pycache__"
        if exist "PathDumper.spec" del "PathDumper.spec"
    ) else (
        echo Failed to create executable
    )
) else (
    echo PyInstaller not found, installing...
    pip install pyinstaller
    if %errorlevel% equ 0 (
        echo Retrying build...
        call "%~f0"
        exit /b
    ) else (
        echo Failed to install PyInstaller
        echo You can run the application with: python main.py
    )
)

echo Creating launcher...
(
echo @echo off
echo cd /d "%%~dp0"
echo if exist "PathDumper.exe" ^(
echo     start "" "PathDumper.exe"
echo ^) else ^(
echo     python main.py
echo ^)
echo pause
) > build\run.bat

echo.
echo Build completed successfully!
echo Files are available in the 'build' directory
echo.
echo IMPORTANT: Windows Defender Notice
echo =====================================
echo If Windows Defender blocks the executable, this is a false positive.
echo The tool only reads files and creates archives - it never deletes user files.
echo.
echo To resolve this:
echo 1. Add the 'build' folder to Windows Defender exclusions
echo 2. Or run from source with: python main.py
echo 3. Report false positive to Microsoft if needed
echo.
echo To run the application:
echo   1. Use build\PathDumper.exe ^(recommended^)
echo   2. Or use build\run.bat
echo   3. Or run: python build\main.py
echo.
pause
