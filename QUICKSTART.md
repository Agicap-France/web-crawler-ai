# Quick Start Guide

## 1. Backend Setup (5 minutes)

### Install Python dependencies:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Configure email:
```bash
copy .env.example .env
```

Edit `.env` file:
```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Gmail App Password Setup:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Copy the 16-character password to `.env`

## 2. Frontend Setup (3 minutes)

```bash
cd frontend
npm install
```

## 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 4. Use the Tool

1. Open http://localhost:3000
2. Enter domain(s) to scan (e.g., `expertzone.microsoft.com`)
3. Enter your email address
4. Click "Start Analysis"
5. Check your email for results!

## Example Test

Try scanning: `expertzone.microsoft.com`

This will:
- Find ~500 archived URLs
- Identify suspicious files (config.js, etc.)
- Detect any exposed API keys or credentials
- Send a detailed HTML report to your email

## Troubleshooting

**Port 5000 already in use?**
```bash
# Change port in backend/.env
PORT=8000
```

**Email not sending?**
- Make sure you're using Gmail App Password (not regular password)
- Check spam folder
- Verify SMTP settings in `.env`

**Backend errors?**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## What the Tool Detects

✅ API Keys & Secrets  
✅ Access Tokens  
✅ AWS Credentials  
✅ Private Keys  
✅ Passwords  
✅ Database URLs  
✅ JWT Tokens  
✅ Service-specific tokens (Slack, GitHub, Stripe, etc.)

## Next Steps

- Read the full README.md for advanced usage
- Customize detection patterns in `wayback_analyzer.py`
- Add more domains to scan
- Set up scheduled scans

---

**Need help?** Open an issue on GitHub or check the README.md for detailed documentation.
