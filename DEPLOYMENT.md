# Wayback Security Scanner - Deployment Guide

This guide covers multiple deployment options for hosting your Wayback Security Scanner as a public website.

## 📋 Table of Contents
- [Option 1: Heroku (Easiest)](#option-1-heroku)
- [Option 2: Vercel + Railway](#option-2-vercel--railway)
- [Option 3: DigitalOcean/AWS/Azure](#option-3-digitalocean-vps)
- [Option 4: Docker Anywhere](#option-4-docker)
- [Custom Domain Setup](#custom-domain-setup)

---

## Option 1: Heroku (Easiest) ⭐

### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed

### Steps

1. **Install Heroku CLI**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
# Or use npm
npm install -g heroku
```

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Heroku App**
```bash
cd "C:\Users\princ\OneDrive\Desktop\Web Crawler Ai"
heroku create your-scanner-name
```

4. **Set Environment Variables**
```bash
heroku config:set SMTP_SERVER=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SENDER_EMAIL=your-email@gmail.com
heroku config:set SENDER_PASSWORD=your-app-password
heroku config:set FLASK_ENV=production
heroku config:set ALLOWED_ORIGINS=*
```

5. **Deploy Backend**
```bash
cd backend
git init
heroku git:remote -a your-scanner-name
git add .
git commit -m "Initial deployment"
git push heroku main
```

6. **Deploy Frontend to Vercel**
```bash
cd ../frontend
npm install -g vercel
vercel
# Follow prompts, set VITE_API_URL to your Heroku backend URL
```

**Result:** Your API will be at `https://your-scanner-name.herokuapp.com`

---

## Option 2: Vercel + Railway

### Backend on Railway

1. **Go to [Railway.app](https://railway.app/)**
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set Root Directory: `backend`
5. Add environment variables:
   - `SMTP_SERVER=smtp.gmail.com`
   - `SMTP_PORT=587`
   - `SENDER_EMAIL=your-email@gmail.com`
   - `SENDER_PASSWORD=your-app-password`
   - `PORT=5000`
6. Deploy!

### Frontend on Vercel

1. **Go to [Vercel.com](https://vercel.com/)**
2. Click "Import Project"
3. Select your repository
4. Set Root Directory: `frontend`
5. Add environment variable:
   - `VITE_API_URL=https://your-railway-backend.railway.app`
6. Deploy!

**Result:** 
- Backend: `https://your-project.railway.app`
- Frontend: `https://your-project.vercel.app`

---

## Option 3: DigitalOcean VPS

### Prerequisites
- DigitalOcean account
- SSH access to your droplet

### Steps

1. **Create Droplet**
   - Go to DigitalOcean
   - Create Ubuntu 22.04 droplet ($6/month)
   - Note your droplet IP address

2. **SSH into Server**
```bash
ssh root@your-droplet-ip
```

3. **Install Dependencies**
```bash
# Update system
apt update && apt upgrade -y

# Install Python, Node.js, Nginx
apt install python3 python3-pip nodejs npm nginx -y

# Install PM2 for process management
npm install -g pm2
```

4. **Clone Your Project**
```bash
cd /var/www
git clone https://github.com/your-username/wayback-scanner.git
cd wayback-scanner
```

5. **Setup Backend**
```bash
cd backend
pip3 install -r requirements.txt

# Create .env file
nano .env
# Add your SMTP credentials

# Start with PM2
pm2 start app.py --interpreter python3 --name scanner-api
pm2 save
pm2 startup
```

6. **Setup Frontend**
```bash
cd ../frontend
npm install
npm run build

# Copy build to nginx
cp -r dist/* /var/www/html/
```

7. **Configure Nginx**
```bash
nano /etc/nginx/sites-available/default
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

8. **Restart Nginx**
```bash
systemctl restart nginx
```

**Result:** Access at `http://your-droplet-ip` or your domain

---

## Option 4: Docker (Any Platform)

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

1. **Navigate to Project**
```bash
cd "C:\Users\princ\OneDrive\Desktop\Web Crawler Ai"
```

2. **Create .env File**
```bash
# Create backend/.env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

3. **Build and Run**
```bash
docker-compose up -d
```

4. **Access Application**
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5000`

### Deploy to Cloud with Docker

**AWS ECS, Google Cloud Run, Azure Container Instances:**

```bash
# Build image
docker build -t wayback-scanner .

# Tag for registry
docker tag wayback-scanner your-registry/wayback-scanner:latest

# Push to registry
docker push your-registry/wayback-scanner:latest

# Deploy using your cloud provider's console or CLI
```

---

## Custom Domain Setup

### 1. Buy Domain
- Namecheap, GoDaddy, Google Domains, etc.
- Example: `securityscanner.com`

### 2. Configure DNS

**For Heroku:**
```
CNAME: www → your-app.herokuapp.com
ALIAS: @ → your-app.herokuapp.com
```

**For Vercel:**
```
CNAME: www → cname.vercel-dns.com
```

**For VPS (DigitalOcean/AWS):**
```
A Record: @ → your-server-ip
A Record: www → your-server-ip
```

### 3. SSL Certificate

**Heroku/Vercel:** Automatic SSL (free)

**VPS with Nginx:**
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renew
certbot renew --dry-run
```

---

## Production Checklist ✅

Before going live:

- [ ] Set strong environment variables
- [ ] Configure proper CORS origins (not `*`)
- [ ] Set up SSL/HTTPS
- [ ] Configure rate limiting
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Create backup strategy for email_recipients.json
- [ ] Test email sending functionality
- [ ] Set up error logging
- [ ] Configure firewall rules
- [ ] Enable automatic backups

---

## Recommended: Quick Start with Vercel + Railway

**Best for beginners, free tier available:**

1. **Backend on Railway** (5 minutes)
   - Connect GitHub repo
   - Set root to `backend`
   - Add environment variables
   - Deploy!

2. **Frontend on Vercel** (3 minutes)
   - Connect GitHub repo
   - Set root to `frontend`
   - Add `VITE_API_URL` variable
   - Deploy!

3. **Point Custom Domain** (2 minutes)
   - Add domain in Vercel settings
   - Update DNS records
   - Done!

**Total Time:** ~10 minutes
**Cost:** Free (with Railway/Vercel free tier)

---

## Environment Variables Reference

### Backend
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
PORT=5000
FLASK_ENV=production
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Frontend
```
VITE_API_URL=https://your-backend-domain.com
```

---

## Support & Troubleshooting

**Common Issues:**

1. **CORS Error:** Set `ALLOWED_ORIGINS` to your frontend URL
2. **Email Not Sending:** Check SMTP credentials and Gmail App Password
3. **502 Bad Gateway:** Backend not running or wrong port
4. **Build Failed:** Check Node.js/Python versions

**Need Help?**
- Check logs: `heroku logs --tail` or `pm2 logs`
- Test API: `curl https://your-api.com/api/health`
- Verify environment variables are set

---

## Cost Estimates

| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| Heroku | 550 hours/month | $7/month |
| Railway | 500 hours + $5 credit | $5-20/month |
| Vercel | Unlimited | $20/month |
| DigitalOcean | N/A | $6/month |
| AWS EC2 | 750 hours (1 year) | $5-10/month |

**Recommendation:** Start with Railway (backend) + Vercel (frontend) free tier, then upgrade as needed.
