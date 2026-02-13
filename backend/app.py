from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import uuid
import json
from datetime import datetime
from wayback_analyzer import WaybackAnalyzer
from email_sender import EmailSender
from email_config import EmailConfig
import os

app = Flask(__name__)

ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
CORS(app, origins=ALLOWED_ORIGINS)

jobs = {}
email_config = EmailConfig()

MAX_JOBS_IN_MEMORY = 100

def cleanup_old_jobs():
    if len(jobs) > MAX_JOBS_IN_MEMORY:
        completed_jobs = [(k, v) for k, v in jobs.items() if v.status in ['completed', 'failed']]
        completed_jobs.sort(key=lambda x: x[1].completed_at or x[1].started_at)
        
        for job_id, _ in completed_jobs[:len(completed_jobs)//2]:
            del jobs[job_id]

class AnalysisJob:
    def __init__(self, job_id, domains, emails):
        self.job_id = job_id
        self.domains = domains
        self.emails = emails
        self.status = "queued"
        self.progress = 0
        self.results = []
        self.started_at = datetime.now().isoformat()
        self.completed_at = None
        self.error = None

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "status": self.status,
            "progress": self.progress,
            "domains_count": len(self.domains),
            "results_count": len(self.results),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error
        }

def process_domains(job_id):
    job = jobs[job_id]
    job.status = "processing"
    
    try:
        analyzer = WaybackAnalyzer()
        total_domains = len(job.domains)
        
        for idx, domain in enumerate(job.domains):
            domain = domain.strip()
            if not domain:
                continue
                
            print(f"[Job {job_id}] Processing domain {idx+1}/{total_domains}: {domain}")
            
            try:
                domain_results = analyzer.analyze_domain(domain)
                if domain_results:
                    job.results.append({
                        "domain": domain,
                        "findings": domain_results,
                        "analyzed_at": datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Error analyzing {domain}: {str(e)}")
                job.results.append({
                    "domain": domain,
                    "error": str(e),
                    "analyzed_at": datetime.now().isoformat()
                })
            
            job.progress = int(((idx + 1) / total_domains) * 100)
        
        job.status = "completed"
        job.completed_at = datetime.now().isoformat()
        
        if job.emails:
            email_sender = EmailSender()
            for email in job.emails:
                try:
                    email_sender.send_results(email, job.results, job.domains)
                except Exception as e:
                    print(f"Error sending email to {email}: {str(e)}")
            
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.now().isoformat()
        print(f"[Job {job_id}] Failed: {str(e)}")

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    domains_input = data.get('domains', '')
    custom_emails = data.get('emails', '')
    use_configured = data.get('use_configured_emails', True)
    
    if not domains_input:
        return jsonify({"error": "No domains provided"}), 400
    
    domains = [d.strip() for d in domains_input.replace(',', '\n').split('\n') if d.strip()]
    
    if not domains:
        return jsonify({"error": "No valid domains provided"}), 400
    
    if len(domains) > 10:
        return jsonify({"error": "Maximum 10 domains per scan"}), 400
    
    recipient_emails = []
    
    if use_configured:
        recipient_emails.extend(email_config.get_recipients())
    
    if custom_emails:
        custom_list = [e.strip() for e in custom_emails.replace(',', '\n').split('\n') if e.strip()]
        recipient_emails.extend(custom_list)
    
    recipient_emails = list(set(recipient_emails))
    
    if not recipient_emails:
        return jsonify({"error": "No recipient emails provided"}), 400
    
    cleanup_old_jobs()
    
    job_id = str(uuid.uuid4())
    job = AnalysisJob(job_id, domains, recipient_emails)
    jobs[job_id] = job
    
    thread = threading.Thread(target=process_domains, args=(job_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "job_id": job_id,
        "message": f"Analysis started. Results will be sent to {len(recipient_emails)} email(s).",
        "domains_count": len(domains),
        "recipients_count": len(recipient_emails)
    }), 202

@app.route('/api/email-config', methods=['GET'])
def get_email_config():
    return jsonify({
        "recipients": email_config.get_recipients(),
        "count": len(email_config.get_recipients())
    })

@app.route('/api/email-config', methods=['POST'])
def update_email_config():
    data = request.json
    
    if not data or 'recipients' not in data:
        return jsonify({"error": "No recipients provided"}), 400
    
    recipients = data['recipients']
    
    if not isinstance(recipients, list):
        return jsonify({"error": "Recipients must be a list"}), 400
    
    email_config.update_recipients(recipients)
    
    return jsonify({
        "message": "Email configuration updated successfully",
        "recipients": email_config.get_recipients(),
        "count": len(email_config.get_recipients())
    })

@app.route('/api/email-config/add', methods=['POST'])
def add_recipient():
    data = request.json
    
    if not data or 'email' not in data:
        return jsonify({"error": "No email provided"}), 400
    
    email = data['email'].strip()
    
    if not email:
        return jsonify({"error": "Invalid email"}), 400
    
    email_config.add_recipient(email)
    
    return jsonify({
        "message": f"Email {email} added successfully",
        "recipients": email_config.get_recipients(),
        "count": len(email_config.get_recipients())
    })

@app.route('/api/email-config/remove', methods=['POST'])
def remove_recipient():
    data = request.json
    
    if not data or 'email' not in data:
        return jsonify({"error": "No email provided"}), 400
    
    email = data['email'].strip()
    
    email_config.remove_recipient(email)
    
    return jsonify({
        "message": f"Email {email} removed successfully",
        "recipients": email_config.get_recipients(),
        "count": len(email_config.get_recipients())
    })

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    job = jobs.get(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(job.to_dict())

@app.route('/api/results/<job_id>', methods=['GET'])
def get_results(job_id):
    job = jobs.get(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify({
        "job_id": job_id,
        "status": job.status,
        "domains": job.domains,
        "results": job.results,
        "started_at": job.started_at,
        "completed_at": job.completed_at
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy", 
        "active_jobs": len([j for j in jobs.values() if j.status == "processing"]),
        "total_jobs": len(jobs)
    })

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "Wayback Security Scanner API",
        "version": "1.0.0",
        "status": "running"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
