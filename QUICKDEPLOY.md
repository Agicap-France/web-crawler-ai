# Quick Deployment Guide

## Fastest Way to Deploy (5-10 minutes)

### Option 1: Vercel + Railway (Recommended) ⭐

#### Step 1: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app/)
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Click "Add variables" and add:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   PORT=5000
   ```
6. Set "Root Directory" to `backend`
7. Click "Deploy"
8. Copy your Railway URL (e.g., `https://your-app.up.railway.app`)

#### Step 2: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com/)
2. Click "Import Project"
3. Select your repository
4. Set "Root Directory" to `frontend`
5. Add environment variable:
   ```
   VITE_API_URL=https://your-railway-app.up.railway.app
   ```
6. Click "Deploy"

**Done! Your site is live at `https://your-project.vercel.app`** 🎉

---

### Option 2: Using Deploy Script (Windows)

1. Open PowerShell in project directory
2. Run:
   ```powershell
   .\deploy-heroku.bat
   ```
3. Follow the prompts
4. Deploy frontend to Vercel (see above)

---

### Option 3: Manual Heroku Deployment

```powershell
# Install Heroku CLI if needed
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
cd backend
heroku create your-scanner-name

# Set environment variables
heroku config:set SMTP_SERVER=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SENDER_EMAIL=your-email@gmail.com
heroku config:set SENDER_PASSWORD=your-app-password
heroku config:set FLASK_ENV=production

# Deploy
git init
heroku git:remote -a your-scanner-name
git add .
git commit -m "Deploy"
git push heroku main
```

---

## Custom Domain Setup

### Add Domain to Vercel
1. Go to your project in Vercel
2. Click "Settings" → "Domains"
3. Add your domain (e.g., `scanner.yourdomain.com`)
4. Update your DNS:
   - **CNAME**: `www` → `cname.vercel-dns.com`
   - **A**: `@` → Vercel's IP (shown in settings)

### Add Domain to Railway
1. Go to your project in Railway
2. Click "Settings" → "Domains"
3. Add custom domain
4. Update DNS as instructed

---

## Email Setup (Gmail)

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Create new app password
5. Copy the 16-character password
6. Use this password in `SENDER_PASSWORD` environment variable

---

## Testing Your Deployment

1. Visit your frontend URL
2. Go to "Email Settings" tab
3. Add your email address
4. Go to "Scanner" tab
5. Enter a test domain (e.g., `example.com`)
6. Click "Start Analysis"
7. Check your email for results!

---

## Troubleshooting

**Frontend can't connect to backend?**
- Check `VITE_API_URL` is set correctly
- Make sure backend URL includes `https://`
- Test backend: `curl https://your-backend-url/api/health`

**Emails not sending?**
- Verify Gmail App Password (not regular password)
- Check spam folder
- View Railway logs for errors

**Build failed?**
- Check Node.js version (should be 18+)
- Check Python version (should be 3.11+)
- Review deployment logs

---

## Free Tier Limits

- **Railway**: $5 credit/month (enough for moderate use)
- **Vercel**: Unlimited frontend hosting
- **Combined**: Free for personal/small projects

---

## Support

For detailed deployment options, see [DEPLOYMENT.md](./DEPLOYMENT.md)

Need help? Check the logs:
- Railway: View in project dashboard
- Vercel: View in deployment details
- Heroku: `heroku logs --tail`
