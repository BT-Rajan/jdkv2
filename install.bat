@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ============================================================================
:: JDK Manufacturing Operations Platform - Windows installer
::
:: Installs two things side by side under C:\xampp\htdocs:
::   1. sentinel-auth   (BT-Rajan/perennia-auth, main branch - RBAC service)
::   2. jdkv2           (this repo's backend)
::
:: Requires on PATH: git, python (3.10+), mysql (XAMPP's is fine).
:: Run from anywhere; it does not need to sit inside either repo.
:: ============================================================================

set "HTDOCS=C:\xampp\htdocs"
set "SENTINEL_DIR=%HTDOCS%\sentinel-auth"
set "JDK_DIR=%HTDOCS%\jdkv2"
set "SENTINEL_REPO=https://github.com/BT-Rajan/perennia-auth.git"
set "JDK_REPO=https://github.com/BT-Rajan/jdkv2.git"
set "SENTINEL_PORT=4000"
set "SENTINEL_DB_HOST=127.0.0.1"
set "SENTINEL_DB_PORT=3306"
set "SENTINEL_DB_USER=root"
set "SENTINEL_DB_PASSWORD="
set "SENTINEL_DB_NAME=sentinel_auth"

echo(
echo === JDK install: checking prerequisites ===
where git >nul 2>&1 || (echo [FAIL] git not found on PATH. Install Git for Windows first. & exit /b 1)
where python >nul 2>&1 || (echo [FAIL] python not found on PATH. Install Python 3.10+ first. & exit /b 1)
where mysql >nul 2>&1 || echo [WARN] mysql client not found on PATH - fine if XAMPP's MySQL service is already running.
if not exist "%HTDOCS%" (echo [FAIL] %HTDOCS% does not exist - is XAMPP installed? & exit /b 1)
echo [OK] prerequisites present.

:: ---------------------------------------------------------------------------
:: 1. sentinel-auth (RBAC service)
:: ---------------------------------------------------------------------------
echo(
echo === Step 1/5: sentinel-auth ===
if exist "%SENTINEL_DIR%\.git" (
    echo Updating existing checkout...
    pushd "%SENTINEL_DIR%"
    git fetch origin main || (echo [FAIL] git fetch failed & exit /b 1)
    git checkout main || (echo [FAIL] git checkout main failed & exit /b 1)
    git reset --hard origin/main || (echo [FAIL] git reset failed & exit /b 1)
    popd
) else (
    git clone "%SENTINEL_REPO%" "%SENTINEL_DIR%" || (echo [FAIL] git clone sentinel-auth failed & exit /b 1)
)

pushd "%SENTINEL_DIR%"
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtualenv...
    python -m venv venv || (echo [FAIL] venv creation failed & exit /b 1)
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul

:: Upstream requirements.txt pins PyJWT==2.8.1, which was never published to
:: PyPI (only 2.8.0 exists) - rewrite that one line in the local clone only.
python -c "
import pathlib
p = pathlib.Path('requirements.txt')
text = p.read_text(encoding='utf-8')
fixed = text.replace('PyJWT==2.8.1', 'PyJWT==2.8.0')
if fixed != text:
    p.write_text(fixed, encoding='utf-8')
    print('[OK] patched requirements.txt: PyJWT==2.8.1 -> PyJWT==2.8.0')
"

echo Installing sentinel-auth dependencies...
pip install -r requirements.txt || (echo [FAIL] pip install -r requirements.txt failed & exit /b 1)
:: requirements.txt is missing two hard runtime imports (main.py/server.py):
pip install flask-cors waitress || (echo [FAIL] pip install flask-cors/waitress failed & exit /b 1)

echo Creating MySQL database "%SENTINEL_DB_NAME%" if it doesn't exist...
python -c "
import pymysql
conn = pymysql.connect(host='%SENTINEL_DB_HOST%', port=%SENTINEL_DB_PORT%, user='%SENTINEL_DB_USER%', password='%SENTINEL_DB_PASSWORD%', charset='utf8mb4', autocommit=True)
with conn.cursor() as cur:
    cur.execute('CREATE DATABASE IF NOT EXISTS `%SENTINEL_DB_NAME%` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
conn.close()
print('[OK] database %SENTINEL_DB_NAME% ready.')
" || (echo [FAIL] could not create %SENTINEL_DB_NAME% - is MySQL running? & exit /b 1)

:: Generate this tenant's secrets once; reuse on every re-run of this script.
if not exist ".env" (
    echo Generating sentinel-auth .env with a fresh JWT secret + client key...
    for /f "delims=" %%K in ('python -c "import secrets; print(secrets.token_urlsafe(48))"') do set "JWT_SECRET=%%K"
    for /f "delims=" %%U in ('python -c "import uuid; print(uuid.uuid4())"') do set "CLIENT_KEY=%%U"
    (
        echo SENTINEL_DATABASE_TYPE=mysql
        echo SENTINEL_MYSQL_URL=mysql+pymysql://%SENTINEL_DB_USER%:%SENTINEL_DB_PASSWORD%@%SENTINEL_DB_HOST%:%SENTINEL_DB_PORT%/%SENTINEL_DB_NAME%
        echo SENTINEL_JWT_SECRET_KEY=!JWT_SECRET!
        echo SENTINEL_SERVER_HOST=127.0.0.1
        echo SENTINEL_SERVER_PORT=%SENTINEL_PORT%
        echo SENTINEL_ALLOW_CORS=true
        echo SENTINEL_CORS_ORIGINS=http://localhost:5173
        echo SENTINEL_DEBUG_MODE=false
    ) > .env
    echo [OK] sentinel-auth\.env written.
) else (
    echo sentinel-auth\.env already exists - leaving it as-is.
    for /f "tokens=2 delims==" %%K in ('findstr /b "SENTINEL_JWT_SECRET_KEY=" .env') do set "JWT_SECRET=%%K"
)

:: Pull the client key back out so we can write the matching value into jdkv2's .env below.
for /f "tokens=2 delims==" %%C in ('findstr /b "SENTINEL_CLIENT_KEY=" .env 2^>nul') do set "CLIENT_KEY=%%C"
if not defined CLIENT_KEY (
    for /f "delims=" %%U in ('python -c "import uuid; print(uuid.uuid4())"') do set "CLIENT_KEY=%%U"
    echo SENTINEL_CLIENT_KEY_NOTE=see jdkv2\.env for the client key in use>>.env
)
popd

:: Write a tiny launcher so the service can be (re)started without re-running this script.
(
    echo @echo off
    echo cd /d "%SENTINEL_DIR%"
    echo call venv\Scripts\activate.bat
    echo python -m sentinel.cmd.server
) > "%SENTINEL_DIR%\start-sentinel.bat"
echo [OK] sentinel-auth installed. Launcher: %SENTINEL_DIR%\start-sentinel.bat

:: ---------------------------------------------------------------------------
:: 2. jdkv2 backend
:: ---------------------------------------------------------------------------
echo(
echo === Step 2/5: jdkv2 backend ===
if exist "%JDK_DIR%\.git" (
    echo Using existing checkout at %JDK_DIR%.
) else (
    echo [WARN] %JDK_DIR% not found or not a git repo - clone it yourself if this is a fresh machine:
    echo         git clone %JDK_REPO% "%JDK_DIR%"
    if not exist "%JDK_DIR%" exit /b 1
)

pushd "%JDK_DIR%\backend"
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtualenv...
    python -m venv venv || (echo [FAIL] venv creation failed & exit /b 1)
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
echo Installing jdkv2 backend dependencies (this pulls perennia-auth/search/notify/files from GitHub)...
pip install -e . || (echo [FAIL] pip install -e . failed - check git access to BT-Rajan/perennia-* repos & exit /b 1)
popd

:: ---------------------------------------------------------------------------
:: 3. jdkv2 .env - wire in sentinel connection details
:: ---------------------------------------------------------------------------
echo(
echo === Step 3/5: jdkv2 .env ===
set "JDK_ENV=%JDK_DIR%\.env"
if not exist "%JDK_ENV%" (
    copy "%JDK_DIR%\.env.example" "%JDK_ENV%" >nul
    echo Created %JDK_ENV% from .env.example - edit DB_* / secrets before continuing if this is a fresh install.
)

:: Upsert SENTINEL_SERVICE_URL / SENTINEL_CLIENT_KEY without disturbing the rest of the file.
python -c "
import pathlib
p = pathlib.Path(r'%JDK_ENV%')
lines = p.read_text(encoding='utf-8').splitlines() if p.exists() else []
values = {'SENTINEL_SERVICE_URL': 'http://127.0.0.1:%SENTINEL_PORT%', 'SENTINEL_CLIENT_KEY': r'!CLIENT_KEY!'}
seen = set()
out = []
for line in lines:
    key = line.split('=', 1)[0] if '=' in line and not line.strip().startswith('#') else None
    if key in values:
        out.append(f'{key}={values[key]}')
        seen.add(key)
    else:
        out.append(line)
for key, val in values.items():
    if key not in seen:
        out.append(f'{key}={val}')
p.write_text('\n'.join(out) + '\n', encoding='utf-8')
print('[OK] wrote SENTINEL_SERVICE_URL / SENTINEL_CLIENT_KEY into', p)
"

:: ---------------------------------------------------------------------------
:: 4. Start sentinel-auth, then initialize the database (needs sentinel up)
:: ---------------------------------------------------------------------------
echo(
echo === Step 4/5: starting sentinel-auth on port %SENTINEL_PORT% ===
start "sentinel-auth" cmd /k "%SENTINEL_DIR%\start-sentinel.bat"
echo Waiting for sentinel-auth to come up...
timeout /t 5 /nobreak >nul

echo(
echo === Step 5/5: initializing jdkv2 database ===
pushd "%JDK_DIR%\backend"
call venv\Scripts\activate.bat
python scripts\init_db.py || (echo [FAIL] init_db.py failed - is MySQL running and .env correct? & popd & exit /b 1)
popd

echo(
echo ============================================================
echo Done.
echo   sentinel-auth running at http://127.0.0.1:%SENTINEL_PORT% (window left open)
echo   Create your first admin:
echo     cd /d "%JDK_DIR%\backend" ^&^& venv\Scripts\activate ^&^& python scripts\create_admin.py you@company.com "a-strong-password" "Your Name"
echo   Start jdkv2 backend:
echo     cd /d "%JDK_DIR%\backend" ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo ============================================================
endlocal
