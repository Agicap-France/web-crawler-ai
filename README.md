# Wayback Machine Security Scanner

An automated cybersecurity tool that analyzes archived web pages from the Wayback Machine to identify potentially sensitive information, API keys, credentials, and security vulnerabilities.

## Features

🔍 **Comprehensive Analysis**
- Fetches all archived URLs from Wayback Machine CDX API
- Identifies suspicious files (.js, .json, .config, .env, etc.)
- Detects API keys, tokens, secrets, and credentials
- Scans for AWS keys, JWT tokens, database URLs, and more

📧 **Email Reporting**
- Automated HTML email reports
- Detailed findings with archived URL links
- Highlighted sensitive data with context
- Professional, easy-to-read format

🚀 **Modern Web Interface**
- Clean, responsive React frontend
- Real-time progress tracking
- Background processing for large domain lists
- Easy-to-use interface

## Architecture

```
├── backend/
│   ├── app.py                  # Flask API server
│   ├── wayback_analyzer.py     # Core analysis engine
│   ├── email_sender.py         # Email reporting system
│   └── requirements.txt        # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── App.tsx             # Main React component
    │   ├── main.tsx            # App entry point
    │   └── index.css           # Styles
    └── package.json            # Node dependencies
```

## Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure email settings:
```bash
copy .env.example .env
```

Edit `.env` and add your email credentials:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Note for Gmail users:**
- You need to use an "App Password" instead of your regular password
- Enable 2-factor authentication on your Google account
- Generate an App Password: https://myaccount.google.com/apppasswords

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Usage

### Running the Application

1. **Start the backend server:**
```bash
cd backend
python app.py
```
The API will run on `http://localhost:5000`

2. **Start the frontend (in a new terminal):**
```bash
cd frontend
npm run dev
```
The web interface will open at `http://localhost:3000`

3. **Use the web interface:**
   - Enter domain(s) to analyze (one per line or comma-separated)
   - Provide your email address
   - Click "Start Analysis"
   - Monitor progress in real-time
   - Receive detailed results via email

### Example Usage

**Input:**
```
expertzone.microsoft.com
example.com
```

**Process:**
1. Fetches all archived URLs from Wayback Machine
2. Identifies suspicious files (config.js, .env, api endpoints)
3. Downloads and analyzes content
4. Detects sensitive patterns (API keys, tokens, credentials)
5. Generates detailed HTML report
6. Sends results to your email

## Detection Capabilities

The tool scans for:

- **API Keys & Secrets:** api_key, api_secret, client_secret
- **Access Tokens:** access_token, auth_token, bearer tokens
- **AWS Credentials:** AWS access keys and secret keys
- **Private Keys:** RSA, EC, DSA private keys
- **Passwords:** password, passwd, pwd fields
- **Database URLs:** MySQL, PostgreSQL, MongoDB, Redis
- **JWT Tokens:** JSON Web Tokens
- **Service Tokens:** Slack, GitHub, Google API, Stripe keys
- **Configuration Files:** .env, .config, .yml, .json

## API Endpoints

### `POST /api/analyze`
Start a new analysis job

**Request:**
```json
{
  "domains": "example.com\nanother.com",
  "email": "your-email@example.com"
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "message": "Analysis started. Results will be sent to your email.",
  "domains_count": 2
}
```

### `GET /api/status/:job_id`
Get job status and progress

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 45,
  "domains_count": 2,
  "results_count": 5,
  "started_at": "2024-01-01T00:00:00",
  "completed_at": null,
  "error": null
}
```

### `GET /api/results/:job_id`
Get complete analysis results

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "domains": ["example.com"],
  "results": [...],
  "started_at": "2024-01-01T00:00:00",
  "completed_at": "2024-01-01T00:05:00"
}
```

### `GET /api/health`
Health check endpoint

## Security Considerations

- The tool handles sensitive data - use appropriate access controls
- Store email credentials securely using environment variables
- Consider rate limiting for production deployments
- Review all findings carefully before taking action
- Never commit `.env` files to version control

## Limitations

- Analyzes up to 500 URLs per domain (configurable)
- Rate limited by Wayback Machine API
- Email sending requires proper SMTP configuration
- Large domain lists may take significant time to process

## Troubleshooting

**Email not sending:**
- Verify SMTP credentials in `.env`
- For Gmail, use App Passwords (not regular password)
- Check firewall/antivirus blocking port 587

**Backend errors:**
- Ensure all dependencies are installed
- Check Python version (3.8+)
- Verify virtual environment is activated

**Frontend issues:**
- Clear browser cache
- Check console for errors
- Verify backend is running on port 5000

## Technology Stack

**Backend:**
- Python 3.8+
- Flask (Web framework)
- Requests (HTTP client)
- SMTP (Email sending)

**Frontend:**
- React 18
- TypeScript
- Vite (Build tool)
- Tailwind CSS (Styling)
- Axios (HTTP client)

## Future Enhancements

- [ ] Database storage for historical results
- [ ] User authentication and multi-user support
- [ ] Scheduled periodic scans
- [ ] Webhook notifications
- [ ] Export results to PDF/CSV
- [ ] Custom pattern configuration
- [ ] Advanced filtering and search

## License

This tool is for educational and authorized security testing only. Always obtain proper authorization before scanning domains you don't own.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For issues or questions, please open a GitHub issue or contact the maintainer.

---

**⚠️ Disclaimer:** This tool is designed for legitimate security research and authorized testing only. Users are responsible for ensuring they have permission to scan target domains. The authors are not responsible for misuse of this tool.
