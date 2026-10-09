@echo off
chcp 65001 > nul
set ROOT=%~dp0..\..
set TMPD=%TEMP%\emulator_check_%RANDOM%
mkdir "%TMPD%"
set SCRIPT=%ROOT%\tests\scripts\test_stage2.txt

echo ### --log: первый запуск создаёт файл с заголовком
call "%ROOT%\run.bat" --headless --log "%TMPD%\events.csv" --script "%SCRIPT%" < nul > nul
type "%TMPD%\events.csv"

echo.
echo ### --log: второй запуск дописывает события
call "%ROOT%\run.bat" --headless --log "%TMPD%\events.csv" --script "%SCRIPT%" < nul > nul
find /c /v "" "%TMPD%\events.csv"

echo.
echo ### --log: недоступный путь (журнал отключается, работа продолжается)
call "%ROOT%\run.bat" --headless --log "%TMPD%\no\such\dir\log.csv" < nul

rmdir /s /q "%TMPD%"
