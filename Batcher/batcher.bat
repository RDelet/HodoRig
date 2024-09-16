@echo off

SET autodesk_dir=C:\Program Files\Autodesk
SET maya_version=2022
SET mayapy=%autodesk_dir%\Maya%maya_version%\bin\mayapy.exe
echo Maya python path: %mayapy% \n
echo

SET batcher_file=%~dp0\batcher.py
set /p batch_name=Enter batch name: 
set /p file_dir=Enter files directory: 
echo Batcher Directory "%file_dir%" with "%batch_name%"
echo

"%mayapy%" -s %batcher_file% -n %batch_name% -d %file_dir%
pause