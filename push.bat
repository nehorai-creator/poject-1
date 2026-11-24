@echo off
chcp 65001 > nul
echo ========================================
echo   Auto Git Commit ^& Push
echo ========================================
echo.

git status -s

echo.
set /p msg="Enter commit message (or press Enter for 'Auto update'): "
if "%msg%"=="" set msg=Auto update

echo.
echo [+] Adding all changes...
git add -A

echo [+] Committing...
git commit -m "%msg%"

echo [+] Pushing to GitHub...
git push origin master

echo.
echo ========================================
echo   Done!
echo ========================================
pause
