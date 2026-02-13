@echo off
echo 🚀 Deploying to Heroku...

REM Check if Heroku CLI is installed
where heroku >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Heroku CLI not found. Please install it first.
    echo Download from: https://devcenter.heroku.com/articles/heroku-cli
    exit /b 1
)

REM Check if logged in
heroku auth:whoami >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Please login to Heroku first:
    heroku login
)

REM Get app name
set /p APP_NAME="Enter your Heroku app name (or leave blank to create new): "

if "%APP_NAME%"=="" (
    echo Creating new Heroku app...
    heroku create
    for /f "tokens=*" %%i in ('heroku apps:info --json ^| jq -r ".app.name"') do set APP_NAME=%%i
) else (
    REM Check if app exists
    heroku apps:info --app %APP_NAME% >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Creating app %APP_NAME%...
        heroku create %APP_NAME%
    )
)

echo 📧 Setting up email configuration...
set /p SMTP_SERVER="SMTP Server (default: smtp.gmail.com): "
if "%SMTP_SERVER%"=="" set SMTP_SERVER=smtp.gmail.com

set /p SMTP_PORT="SMTP Port (default: 587): "
if "%SMTP_PORT%"=="" set SMTP_PORT=587

set /p SENDER_EMAIL="Sender Email: "
set /p SENDER_PASSWORD="Sender Password (App Password): "

REM Set environment variables
echo Setting environment variables...
heroku config:set SMTP_SERVER=%SMTP_SERVER% --app %APP_NAME%
heroku config:set SMTP_PORT=%SMTP_PORT% --app %APP_NAME%
heroku config:set SENDER_EMAIL=%SENDER_EMAIL% --app %APP_NAME%
heroku config:set SENDER_PASSWORD=%SENDER_PASSWORD% --app %APP_NAME%
heroku config:set FLASK_ENV=production --app %APP_NAME%
heroku config:set ALLOWED_ORIGINS=* --app %APP_NAME%

REM Navigate to backend directory
cd backend

REM Initialize git if needed
if not exist .git (
    git init
)

REM Add Heroku remote
heroku git:remote -a %APP_NAME%

REM Add all files and commit
git add .
git commit -m "Deploy to Heroku"

REM Deploy
echo 🚀 Deploying...
git push heroku main

echo ✅ Backend deployed successfully!
echo 🌐 Your API is available at: https://%APP_NAME%.herokuapp.com
echo.
echo Next steps:
echo 1. Deploy frontend to Vercel or Netlify
echo 2. Set VITE_API_URL=https://%APP_NAME%.herokuapp.com in frontend
echo 3. Update ALLOWED_ORIGINS after deploying frontend

pause
