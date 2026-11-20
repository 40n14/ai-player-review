@echo off
rem Starts the terminal interface. Uses the "py" launcher when there is one, else python on PATH.
rem   prk            the menu
rem   prk check -p projects\my-game.json
setlocal
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -I "%~dp0prk.py" %*
) else (
  python -I "%~dp0prk.py" %*
)
exit /b %errorlevel%
