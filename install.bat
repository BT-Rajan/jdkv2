@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ============================================================================
:: JDK Manufacturing Operations Platform - Windows installer
::
:: Installs and brings up three things under C:\xampp\htdocs:
::   1. sentinel-auth   (BT-Rajan/perennia-auth, main branch - RBAC service)
::   2. jdkv2 backend   (this repo's FastAPI backend)
::   3. jdkv2 frontend  (Vue 3 dev server, if Node/npm is on PATH)
::
:: Requires on PATH: git, python (3.10+), and XAMPP's MySQL service running.
:: npm is optional - the frontend step is skipped (with a warning) without it.
:: Run from anywhere; it does not need to sit inside either repo.
::
:: Optional admin account args: install.bat [email] [password] [full name]
:: Defaults to admin@jdk.local / a freshly generated password (printed at
:: the end) / "Administrator" if not given.
:: ============================================================================

set "HERE=%~dp0"
set "HTDOCS=C:\xampp\htdocs"
set "SENTINEL_DIR=%HTDOCS%\sentinel-auth"
set "JDK_DIR=%HTDOCS%\jdkv2"
set "SENTINEL_REPO=https://github.com/BT-Rajan/perennia-auth.git"
set "JDK_REPO=https://github.com/BT-Rajan/jdkv2.git"
set "SENTINEL_PORT=4000"

set "ADMIN_EMAIL=%~1"
set "ADMIN_PASSWORD=%~2"
set "ADMIN_NAME=%~3"
if "%ADMIN_EMAIL%"=="" set "ADMIN_EMAIL=admin@jdk.local"
if "%ADMIN_NAME%"=="" set "ADMIN_NAME=Administrator"

echo(
echo === JDK install: checking prerequisites ===
where git >nul 2>&1 || (echo [FAIL] git not found on PATH. Install Git for Windows first. & exit /b 1)
where python >nul 2>&1 || (echo [FAIL] python not found on PATH. Install Python 3.10+ first. & exit /b 1)
where npm >nul 2>&1 || echo [WARN] npm not found on PATH - frontend step will be skipped.
if not exist "%HTDOCS%" (echo [FAIL] %HTDOCS% does not exist - is XAMPP installed? & exit /b 1)
echo Checking MySQL is reachable on 127.0.0.1:3306 (root, no password)...
python -c "import pymysql,sys; pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', connect_timeout=3).close()" 2>nul || (
    echo [FAIL] Could not connect to MySQL on 127.0.0.1:3306 as root with no password.
    echo         Start XAMPP's MySQL service, or edit jdkv2\.env's DB_* values after this
    echo         run if your credentials differ, then re-run.
    exit /b 1
)
echo [OK] prerequisites present.

:: ---------------------------------------------------------------------------
:: 1. sentinel-auth (RBAC service)
:: ---------------------------------------------------------------------------
echo(
echo === Step 1/8: sentinel-auth - fetch ===
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

echo(
echo === Step 2/8: sentinel-auth - install (patched requirements) ===
:: Upstream requirements.txt has several problems on a modern Windows +
:: Python 3.13 setup, found by actually running this end to end:
::   - PyJWT==2.8.1 was never published to PyPI (only 2.8.0 exists)
::   - pydantic==2.5.0 / pydantic-core==2.14.1 have no cp313 Windows wheel,
::     so pip falls back to a from-source build that needs a Rust toolchain,
::     and that bootstrap fails on a clean machine. pydantic 2.9.2 (with
::     pydantic-core 2.23.4) has a real cp313 wheel.
::   - PyYAML==6.0.1 has no cp313 wheel either; 6.0.2 does.
::   - SQLAlchemy==2.0.23 predates a Python 3.13 compatibility fix (their
::     issue #11334 - CPython 3.13 added __firstlineno__/__static_attributes__
::     to every class, which trips SQLAlchemy's TypingOnly check). Fixed
::     upstream in 2.0.30; pin past that.
::   - psycopg/PyMySQL/pyodbc (Postgres/MySQL/MSSQL drivers) are unnecessary -
::     sentinel-auth runs on SQLite here (see the .env step below), which
::     only needs Python's built-in sqlite3.
::   - slowapi is listed but unused; the code actually imports flask_limiter
::     (optional, only used if AUTH_ENABLE_RATE_LIMIT is set).
::   - flask-cors, waitress, python-json-logger, APScheduler, and bleach are
::     hard runtime imports (main.py/server.py/logging_config.py/
::     workflow_checker.py/sanitizer.py) that are missing from requirements.txt
::     entirely.
:: Rewriting the whole file in this local clone rather than patching lines,
:: so re-running this installer stays deterministic.
(
    echo Flask==3.0.0
    echo SQLAlchemy==2.0.36
    echo PyJWT==2.8.0
    echo pydantic==2.9.2
    echo pydantic-settings==2.5.2
    echo python-dotenv==1.0.0
    echo PyYAML==6.0.2
    echo requests==2.31.0
    echo cryptography==41.0.7
    echo flask-cors
    echo waitress
    echo python-json-logger
    echo APScheduler
    echo bleach
) > requirements.txt
echo [OK] wrote a corrected requirements.txt for this clone.

pip install -r requirements.txt || (echo [FAIL] pip install -r requirements.txt failed & exit /b 1)

echo(
echo === Step 3/8: sentinel-auth - patch permission-name validation ===
:: sentinel/validation.py's permission-name regex only allows
:: [a-zA-Z0-9_-], but jdkv2's whole permission vocabulary uses dotted codes
:: (users.view, customer.manage, ...) - every assign_permission_to_role call
:: 400s with "Invalid permission name" until dots are allowed.
python "%HERE%installer\patch_sentinel_validation.py" "%SENTINEL_DIR%" || (echo [FAIL] patch_sentinel_validation.py failed & exit /b 1)

echo(
echo === Step 4/8: sentinel-auth - .env ===
for /f "delims=" %%K in ('python "%HERE%installer\write_sentinel_env.py" "%SENTINEL_DIR%" "%SENTINEL_PORT%"') do set "CLIENT_KEY=%%K"
if "%CLIENT_KEY%"=="" (echo [FAIL] write_sentinel_env.py failed & exit /b 1)
echo [OK] sentinel-auth\.env ready.
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
echo === Step 5/8: jdkv2 backend ===
if exist "%JDK_DIR%\.git" (
    echo Updating existing checkout...
    pushd "%JDK_DIR%"
    git fetch origin main || (echo [FAIL] git fetch failed & exit /b 1)
    git checkout main || (echo [FAIL] git checkout main failed & exit /b 1)
    git reset --hard origin/main || (echo [FAIL] git reset failed & exit /b 1)
    popd
) else (
    git clone "%JDK_REPO%" "%JDK_DIR%" || (echo [FAIL] git clone jdkv2 failed & exit /b 1)
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
:: app/models/users.py uses pydantic's EmailStr, which needs this optional
:: extra - pyproject.toml doesn't list it.
pip install email-validator || (echo [FAIL] pip install email-validator failed & exit /b 1)
popd

:: ---------------------------------------------------------------------------
:: 3. jdkv2 .env
:: ---------------------------------------------------------------------------
echo(
echo === Step 6/8: jdkv2 .env ===
if not exist "%JDK_DIR%\.env" (
    copy "%JDK_DIR%\.env.example" "%JDK_DIR%\.env" >nul
    echo Created %JDK_DIR%\.env from .env.example.
)
python "%HERE%installer\upsert_jdk_env.py" "%JDK_DIR%" "%SENTINEL_PORT%" "%CLIENT_KEY%" || (echo [FAIL] upsert_jdk_env.py failed & exit /b 1)

:: ---------------------------------------------------------------------------
:: 4. Start sentinel-auth, wait for it, then initialize the jdk database
:: ---------------------------------------------------------------------------
echo(
echo === Step 7/8: starting sentinel-auth and initializing the database ===
start "sentinel-auth" cmd /k "%SENTINEL_DIR%\start-sentinel.bat"
echo Waiting for sentinel-auth to come up (polling http://127.0.0.1:%SENTINEL_PORT%/ping)...
python "%HERE%installer\wait_for_url.py" "http://127.0.0.1:%SENTINEL_PORT%/ping" 90
if errorlevel 1 (
    echo [FAIL] sentinel-auth never became ready.
    echo         Check the separate "sentinel-auth" console window for a traceback.
    echo         Common causes: port %SENTINEL_PORT% already in use by another process.
    exit /b 1
)

pushd "%JDK_DIR%\backend"
call venv\Scripts\activate.bat
python scripts\init_db.py || (echo [FAIL] init_db.py failed - is MySQL running and .env correct? & popd & exit /b 1)

echo(
echo Creating admin account (%ADMIN_EMAIL%)...
if "%ADMIN_PASSWORD%"=="" (
    for /f "delims=" %%P in ('python "%HERE%installer\gen_secret.py"') do set "ADMIN_PASSWORD=%%P"
)
if not exist ".admin_created" (
    python scripts\create_admin.py "%ADMIN_EMAIL%" "%ADMIN_PASSWORD%" "%ADMIN_NAME%"
    if errorlevel 1 (
        echo [WARN] create_admin.py failed - it may already exist, or check the error above.
    ) else (
        echo %ADMIN_EMAIL%>.admin_created
    )
) else (
    echo [OK] admin already created previously ^(.admin_created marker present^) - skipping.
)
popd

:: ---------------------------------------------------------------------------
:: 5. Start jdkv2 backend + frontend
:: ---------------------------------------------------------------------------
echo(
echo === Step 8/8: starting jdkv2 backend and frontend ===
(
    echo @echo off
    echo cd /d "%JDK_DIR%\backend"
    echo call venv\Scripts\activate.bat
    echo uvicorn app.main:app --reload --port 8000
) > "%JDK_DIR%\start-backend.bat"
start "jdkv2-backend" cmd /k "%JDK_DIR%\start-backend.bat"

if exist "%JDK_DIR%\frontend\package.json" (
    where npm >nul 2>&1 && (
        pushd "%JDK_DIR%\frontend"
        if not exist "node_modules" (
            echo Installing frontend dependencies ^(npm install^)...
            call npm install || echo [WARN] npm install failed - start the frontend manually.
        )
        popd
        (
            echo @echo off
            echo cd /d "%JDK_DIR%\frontend"
            echo npm run dev
        ) > "%JDK_DIR%\start-frontend.bat"
        start "jdkv2-frontend" cmd /k "%JDK_DIR%\start-frontend.bat"
    ) || echo [WARN] npm not found - skipping frontend. Run %JDK_DIR%\frontend manually once Node is installed.
)

echo(
echo ============================================================
echo Done. Windows now running (left open):
echo   sentinel-auth  - http://127.0.0.1:%SENTINEL_PORT%
echo   jdkv2 backend  - http://127.0.0.1:8000
echo   jdkv2 frontend - check its window for the local URL ^(usually http://localhost:5173^)
echo(
echo   Admin login:
echo     email:    %ADMIN_EMAIL%
echo     password: %ADMIN_PASSWORD%
echo(
echo   Re-launch any of these later without reinstalling:
echo     %SENTINEL_DIR%\start-sentinel.bat
echo     %JDK_DIR%\start-backend.bat
echo     %JDK_DIR%\start-frontend.bat
echo ============================================================
endlocal
