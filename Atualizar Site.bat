@echo off
setlocal
title Atualizar Painel de Zoonoses
cd /d "%~dp0"
where python >nul 2>nul
if not errorlevel 1 goto usar_python
where py >nul 2>nul
if not errorlevel 1 goto usar_py
echo Python nao encontrado. Instale o Python para atualizar o site.
pause
exit /b 1

:usar_python
python "%~dp0atualizar_site.py"
goto finalizar

:usar_py
py -3 "%~dp0atualizar_site.py"

:finalizar
echo.
pause
