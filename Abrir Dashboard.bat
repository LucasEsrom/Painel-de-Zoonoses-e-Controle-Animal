@echo off
setlocal
title Dashboard de Zoonoses
cd /d "%~dp0"
where python >nul 2>nul
if not errorlevel 1 goto usar_python
where py >nul 2>nul
if not errorlevel 1 goto usar_py
echo Python nao encontrado. Instale o Python para abrir o dashboard.
pause
exit /b 1

:usar_python
python "%~dp0iniciar_dashboard.py"
goto finalizar

:usar_py
py -3 "%~dp0iniciar_dashboard.py"

:finalizar
if not errorlevel 1 exit /b 0
echo.
echo O dashboard nao iniciou. Confira o erro acima.
pause
exit /b 1
