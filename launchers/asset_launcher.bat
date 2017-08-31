@echo off

set _script="../tools/asset_launcher.py"

set _python="C:\Program Files\Autodesk\Maya2017\bin\mayapy.exe"
IF EXIST %_python% GOTO LAUNCH
set _python="c:\Python27\python.exe"
IF EXIST %_python% GOTO LAUNCH

echo "No python or Maya install found!"
pause
exit

:LAUNCH

%_python% %_script%

pause


