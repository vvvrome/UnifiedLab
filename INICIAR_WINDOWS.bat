@echo off
cd /d "%~dp0"
echo UnifiedLab: inicia portal y servicios en ventanas separadas.
start "UnifiedLab Portal" cmd /k "python run_portal.py"
start "DataCenter" cmd /k "cd datacenter_original && python main.py"
start "PhysicLab" cmd /k "python run_physics.py"
echo Portal: http://127.0.0.1:8000
