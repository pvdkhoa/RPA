@echo off
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM UiPath.Python.Runner.exe /T 2>nul
taskkill /F /IM UiPath.Python.Service.exe /T 2>nul
echo Done killing python processes