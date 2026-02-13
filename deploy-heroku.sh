#!/bin/bash

echo "🚀 Deploying to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null
then
    echo "❌ Heroku CLI not found. Please install it first."
    exit 1
fi

# Check if logged in
if ! heroku auth:whoami &> /dev/null
then
    echo "Please login to Heroku first:"
    heroku login
fi

# Get app name
read -p "Enter your Heroku app name (or leave blank to create new): " APP_NAME

if [ -z "$APP_NAME" ]
then
    echo "Creating new Heroku app..."
    heroku create
    APP_NAME=$(heroku apps:info --json | jq -r '.app.name')
else
    # Check if app exists
    if ! heroku apps:info --app $APP_NAME &> /dev/null
    then
        echo "Creating app $APP_NAME..."
        heroku create $APP_NAME
    fi
fi

echo "📧 Setting up email configuration..."
read -p "SMTP Server (default: smtp.gmail.com): " SMTP_SERVER
SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}

read -p "SMTP Port (default: 587): " SMTP_PORT
SMTP_PORT=${SMTP_PORT:-587}

read -p "Sender Email: " SENDER_EMAIL
read -sp "Sender Password (App Password): " SENDER_PASSWORD
echo

# Set environment variables
echo "Setting environment variables..."
heroku config:set SMTP_SERVER=$SMTP_SERVER --app $APP_NAME
heroku config:set SMTP_PORT=$SMTP_PORT --app $APP_NAME
heroku config:set SENDER_EMAIL=$SENDER_EMAIL --app $APP_NAME
heroku config:set SENDER_PASSWORD=$SENDER_PASSWORD --app $APP_NAME
heroku config:set FLASK_ENV=production --app $APP_NAME
heroku config:set ALLOWED_ORIGINS=* --app $APP_NAME

# Navigate to backend directory
cd backend

# Initialize git if needed
if [ ! -d .git ]; then
    git init
fi

# Add Heroku remote
heroku git:remote -a $APP_NAME

# Add all files and commit
git add .
git commit -m "Deploy to Heroku"

# Deploy
echo "🚀 Deploying..."
git push heroku main

echo "✅ Backend deployed successfully!"
echo "🌐 Your API is available at: https://$APP_NAME.herokuapp.com"
echo ""
echo "Next steps:"
echo "1. Deploy frontend to Vercel or Netlify"
echo "2. Set VITE_API_URL=https://$APP_NAME.herokuapp.com in frontend"
echo "3. Update ALLOWED_ORIGINS after deploying frontend"
