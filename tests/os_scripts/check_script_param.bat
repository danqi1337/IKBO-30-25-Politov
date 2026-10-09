@echo off
chcp 65001 > nul
set ROOT=%~dp0..\..
set TMPD=%TEMP%\emulator_check_%RANDOM%
mkdir "%TMPD%"

echo ### --script: стартовый скрипт с комментариями
call "%ROOT%\run.bat" --headless --log "%TMPD%\log.csv" --script "%ROOT%\tests\scripts\test_stage2.txt" < nul
echo код возврата: %ERRORLEVEL%

echo.
echo ### --script: несуществующий файл (ошибка выводится, работа продолжается)
call "%ROOT%\run.bat" --headless --log "%TMPD%\log.csv" --script "%TMPD%\missing.txt" < nul
echo код возврата: %ERRORLEVEL%

rmdir /s /q "%TMPD%"
