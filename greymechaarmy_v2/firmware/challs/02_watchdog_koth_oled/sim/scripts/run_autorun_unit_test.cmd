@echo off
setlocal
set PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
if not exist "%PY%" set PY=python
"%PY%" tests\unit\test_watchdog_oled_autorun.py
