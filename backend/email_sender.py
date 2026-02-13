import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from typing import List, Dict, Any

class EmailSender:
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.sender_email = os.environ.get('SENDER_EMAIL', '')
        self.sender_password = os.environ.get('SENDER_PASSWORD', '')
        
    def generate_html_report(self, results: List[Dict[str, Any]], domains: List[str]) -> str:
        total_findings = sum(len(r.get('findings', [])) for r in results)
        sensitive_count = sum(1 for r in results for f in r.get('findings', []) if f.get('has_sensitive_data', False))
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .summary {{
                    background: white;
                    padding: 25px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }}
                .stat-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #667eea;
                }}
                .stat-number {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 10px 0;
                }}
                .stat-label {{
                    color: #666;
                    font-size: 14px;
                    text-transform: uppercase;
                }}
                .domain-section {{
                    background: white;
                    padding: 25px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .domain-header {{
                    font-size: 22px;
                    color: #667eea;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #eee;
                }}
                .finding {{
                    background: #fff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 15px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                }}
                .finding.critical {{
                    border-left: 4px solid #dc3545;
                }}
                .finding.warning {{
                    border-left: 4px solid #ffc107;
                }}
                .finding-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }}
                .url {{
                    color: #667eea;
                    text-decoration: none;
                    word-break: break-all;
                    font-weight: 500;
                }}
                .url:hover {{
                    text-decoration: underline;
                }}
                .badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                .badge-critical {{
                    background: #dc3545;
                    color: white;
                }}
                .badge-warning {{
                    background: #ffc107;
                    color: #000;
                }}
                .reasons {{
                    margin: 10px 0;
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 5px;
                }}
                .reason-tag {{
                    display: inline-block;
                    background: #e9ecef;
                    padding: 4px 10px;
                    border-radius: 4px;
                    margin: 2px;
                    font-size: 13px;
                }}
                .sensitive-data {{
                    margin-top: 15px;
                    padding: 15px;
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    border-radius: 5px;
                }}
                .sensitive-category {{
                    font-weight: bold;
                    color: #856404;
                    margin-top: 10px;
                    margin-bottom: 5px;
                }}
                .match {{
                    background: white;
                    padding: 10px;
                    border-radius: 4px;
                    margin: 5px 0;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    word-break: break-all;
                    border: 1px solid #dee2e6;
                }}
                .context {{
                    color: #666;
                    font-size: 11px;
                    margin-top: 5px;
                    font-style: italic;
                }}
                .timestamp {{
                    color: #666;
                    font-size: 13px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 13px;
                    margin-top: 30px;
                }}
                .no-findings {{
                    text-align: center;
                    padding: 40px;
                    color: #666;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 Wayback Machine Security Analysis Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Executive Summary</h2>
                <div class="summary-grid">
                    <div class="stat-card">
                        <div class="stat-label">Domains Analyzed</div>
                        <div class="stat-number">{len(domains)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Findings</div>
                        <div class="stat-number">{total_findings}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Sensitive Data Detected</div>
                        <div class="stat-number">{sensitive_count}</div>
                    </div>
                </div>
                <div style="margin-top: 20px;">
                    <strong>Analyzed Domains:</strong><br>
                    {', '.join(domains)}
                </div>
            </div>
        """
        
        if not results or all(not r.get('findings') for r in results):
            html += """
            <div class="no-findings">
                <h3>✅ No suspicious findings detected</h3>
                <p>The analysis did not identify any potentially sensitive or suspicious files in the archived URLs.</p>
            </div>
            """
        else:
            for domain_result in results:
                domain = domain_result.get('domain', 'Unknown')
                findings = domain_result.get('findings', [])
                
                if not findings:
                    continue
                
                html += f"""
                <div class="domain-section">
                    <div class="domain-header">🌐 {domain}</div>
                """
                
                for finding in findings:
                    has_sensitive = finding.get('has_sensitive_data', False)
                    severity_class = 'critical' if has_sensitive else 'warning'
                    badge_class = 'badge-critical' if has_sensitive else 'badge-warning'
                    badge_text = 'CRITICAL' if has_sensitive else 'SUSPICIOUS'
                    
                    html += f"""
                    <div class="finding {severity_class}">
                        <div class="finding-header">
                            <span class="badge {badge_class}">{badge_text}</span>
                            <span class="timestamp">📅 {finding.get('timestamp', 'N/A')}</span>
                        </div>
                        
                        <div>
                            <strong>Original URL:</strong><br>
                            <a href="{finding.get('archived_url', '#')}" class="url" target="_blank">
                                {finding.get('original_url', 'N/A')}
                            </a>
                        </div>
                        
                        <div>
                            <strong>Archived URL:</strong><br>
                            <a href="{finding.get('archived_url', '#')}" class="url" target="_blank">
                                {finding.get('archived_url', 'N/A')}
                            </a>
                        </div>
                        
                        <div class="reasons">
                            <strong>🚨 Detection Reasons:</strong><br>
                            {''.join(f'<span class="reason-tag">{reason}</span>' for reason in finding.get('reasons', []))}
                        </div>
                    """
                    
                    if has_sensitive and finding.get('findings'):
                        html += '<div class="sensitive-data"><strong>⚠️ SENSITIVE DATA DETECTED:</strong>'
                        
                        for category, matches in finding.get('findings', {}).items():
                            html += f'<div class="sensitive-category">📌 {category.replace("_", " ").title()}:</div>'
                            
                            for match in matches[:5]:
                                html += f'''
                                <div class="match">
                                    <strong>Match:</strong> {match.get('match', 'N/A')[:200]}
                                    <div class="context">Context: {match.get('context', 'N/A')[:150]}...</div>
                                </div>
                                '''
                        
                        html += '</div>'
                    
                    if finding.get('error'):
                        html += f'<div style="color: #dc3545; margin-top: 10px;"><strong>Error:</strong> {finding.get("error")}</div>'
                    
                    html += '</div>'
                
                html += '</div>'
        
        html += """
            <div class="footer">
                <p><strong>Wayback Machine Security Scanner</strong></p>
                <p>This automated report was generated to identify potentially sensitive data in archived web pages.</p>
                <p>⚠️ Please review all findings carefully and take appropriate action to secure any exposed credentials or sensitive information.</p>
            </div>
        </body>
        </html>
        """
        
        return html

    def send_results(self, recipient_email: str, results: List[Dict[str, Any]], domains: List[str]):
        if not self.sender_email or not self.sender_password:
            print("Email credentials not configured. Skipping email send.")
            print(f"Results would be sent to: {recipient_email}")
            return
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'🔒 Wayback Security Analysis Report - {len(domains)} Domain(s)'
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            html_content = self.generate_html_report(results, domains)
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            print(f"Sending email to {recipient_email}...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {recipient_email}")
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            raise
