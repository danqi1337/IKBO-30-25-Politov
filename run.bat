@echo off
chcp 65001 > nul
set PYTHONPATH=%~dp0src
python -m emulator %*
