@echo off
cd /d "%~dp0"

echo ==========================================
echo        UNIFIEDLAB - INICIO
echo ==========================================

set MYSQL_HOST=127.0.0.1
set MYSQL_PORT=3306
set MYSQL_USER=unifiedlab
set MYSQL_PASSWORD=xqgy1ECJ

set MYSQL_DATABASE_PORTAL=unifiedlab
set MYSQL_DATABASE_PHYSICLAB=physiclab
set MYSQL_DATABASE_DATACENTER=datacenter
set MYSQL_DATABASE_STELLAR=stellarlab

echo.
echo Iniciando UnifiedLab Portal...
start "UnifiedLab Portal" cmd /k "python run_portal.py"

echo Iniciando DataCenter...
start "DataCenter" cmd /k "cd datacenter_original && python main.py"

echo Iniciando PhysicLab...
start "PhysicLab" cmd /k "python run_physics.py"

echo.
echo Portal: http://127.0.0.1:8000
echo PhysicLab: http://127.0.0.1:5001
echo.
pause