@echo off
chcp 65001 > nul
set ROOT=%~dp0..\..
set TMPD=%TEMP%\emulator_check_%RANDOM%
mkdir "%TMPD%"
set INFO=%ROOT%\tests\scripts\vfs_info.txt

echo ### --vfs: каталог не существует
call "%ROOT%\run.bat" --headless --log "%TMPD%\log.csv" --vfs "%TMPD%\no_such_vfs" --script "%INFO%" < nul

echo.
echo ### --vfs: вместо каталога передан файл (неверный формат)
call "%ROOT%\run.bat" --headless --log "%TMPD%\log.csv" --vfs "%ROOT%\tests\vfs\minimal\readme.txt" --script "%INFO%" < nul

echo.
echo ### без --vfs: VFS по умолчанию
call "%ROOT%\run.bat" --headless --log "%TMPD%\log.csv" --script "%INFO%" < nul

rmdir /s /q "%TMPD%"
