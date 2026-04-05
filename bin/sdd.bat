@echo off
REM SDD-Workflow launcher with proper PATH handling

REM Get the directory of this script
set SCRIPT_DIR=%~dp0

REM Add script directory to PATH for this session
set PATH=%SCRIPT_DIR%;%PATH%

REM Execute the main command
call "%SCRIPT_DIR%sdd.cmd" %*