import requests
import re
import json
from urllib.parse import urlparse, unquote
from typing import List, Dict, Any
import time

class WaybackAnalyzer:
    def __init__(self):
        self.cdx_api = "https://web.archive.org/cdx/search/cdx"
        self.wayback_base = "https://web.archive.org/web"
        
        self.sensitive_patterns = {
            "api_keys": [
                r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
                r'apikey["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
                r'api[_-]?secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
            ],
            "access_tokens": [
                r'access[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
                r'auth[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
                r'bearer["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
            ],
            "client_secrets": [
                r'client[_-]?secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
                r'client[_-]?id["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
            ],
            "aws_keys": [
                r'AKIA[0-9A-Z]{16}',
                r'aws[_-]?access[_-]?key[_-]?id["\']?\s*[:=]\s*["\']([A-Z0-9]{20})["\']',
                r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9/+=]{40})["\']',
            ],
            "private_keys": [
                r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----',
                r'private[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-/+=]{40,})["\']',
            ],
            "passwords": [
                r'password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
                r'passwd["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
                r'pwd["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
            ],
            "database_urls": [
                r'mysql://[^"\s]+',
                r'postgres://[^"\s]+',
                r'mongodb://[^"\s]+',
                r'redis://[^"\s]+',
            ],
            "jwt_tokens": [
                r'eyJ[a-zA-Z0-9_\-]*\.eyJ[a-zA-Z0-9_\-]*\.[a-zA-Z0-9_\-]*',
            ],
            "slack_tokens": [
                r'xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24,}',
            ],
            "github_tokens": [
                r'gh[ps]_[a-zA-Z0-9]{36}',
            ],
            "google_api": [
                r'AIza[0-9A-Za-z\-_]{35}',
            ],
            "stripe_keys": [
                r'sk_live_[0-9a-zA-Z]{24,}',
                r'pk_live_[0-9a-zA-Z]{24,}',
            ],
        }
        
        self.suspicious_extensions = [
            '.js', '.json', '.xml', '.config', '.yml', '.yaml', 
            '.env', '.ini', '.conf', '.properties', '.bak', 
            '.old', '.backup', '.sql', '.db', '.log'
        ]
        
        self.suspicious_patterns = [
            'config', 'secret', 'key', 'token', 'password', 'credential',
            'auth', 'api', 'private', 'internal', 'admin', 'backup',
            'database', 'db', 'prod', 'production', 'staging', '.env'
        ]

    def fetch_archived_urls(self, domain: str, limit: int = 10000) -> List[str]:
        print(f"Fetching archived URLs for {domain}...")
        
        params = {
            'url': f'*.{domain}/*',
            'fl': 'original',
            'collapse': 'urlkey',
            'limit': limit,
            'filter': 'statuscode:200'
        }
        
        try:
            response = requests.get(self.cdx_api, params=params, timeout=30)
            response.raise_for_status()
            
            urls = response.text.strip().split('\n')
            urls = [url.strip() for url in urls if url.strip()]
            
            print(f"Found {len(urls)} archived URLs for {domain}")
            return urls
            
        except Exception as e:
            print(f"Error fetching URLs for {domain}: {str(e)}")
            return []

    def is_suspicious_url(self, url: str) -> tuple[bool, List[str]]:
        reasons = []
        url_lower = url.lower()
        
        for ext in self.suspicious_extensions:
            if url_lower.endswith(ext):
                reasons.append(f"Suspicious file extension: {ext}")
                break
        
        for pattern in self.suspicious_patterns:
            if pattern in url_lower:
                reasons.append(f"Suspicious keyword: {pattern}")
        
        return len(reasons) > 0, reasons

    def get_archived_snapshot(self, url: str) -> tuple[str, str]:
        print(f"Getting snapshot for {url}")
        
        cdx_url = f"{self.cdx_api}?url={url}&output=json&limit=1"
        
        try:
            response = requests.get(cdx_url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) > 1:
                timestamp = data[1][1]
                original_url = data[1][2]
                archived_url = f"{self.wayback_base}/{timestamp}/{original_url}"
                return archived_url, timestamp
            
        except Exception as e:
            print(f"Error getting snapshot: {str(e)}")
        
        return None, None

    def analyze_content(self, content: str) -> Dict[str, List[Dict[str, str]]]:
        findings = {}
        
        for category, patterns in self.sensitive_patterns.items():
            matches = []
            
            for pattern in patterns:
                try:
                    found = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in found:
                        matched_text = match.group(0)
                        
                        if len(matched_text) > 200:
                            matched_text = matched_text[:200] + "..."
                        
                        context_start = max(0, match.start() - 50)
                        context_end = min(len(content), match.end() + 50)
                        context = content[context_start:context_end]
                        
                        matches.append({
                            "match": matched_text,
                            "context": context,
                            "position": match.start()
                        })
                except Exception as e:
                    print(f"Pattern error in {category}: {str(e)}")
                    continue
            
            if matches:
                findings[category] = matches[:10]
        
        return findings

    def fetch_and_analyze(self, archived_url: str) -> Dict[str, Any]:
        try:
            print(f"Fetching content from {archived_url}")
            
            response = requests.get(archived_url, timeout=20, allow_redirects=True)
            response.raise_for_status()
            
            content = response.text
            
            findings = self.analyze_content(content)
            
            return {
                "has_sensitive_data": len(findings) > 0,
                "findings": findings,
                "content_length": len(content),
                "final_url": response.url
            }
            
        except Exception as e:
            print(f"Error fetching/analyzing content: {str(e)}")
            return {
                "error": str(e),
                "has_sensitive_data": False,
                "findings": {}
            }

    def analyze_domain(self, domain: str) -> List[Dict[str, Any]]:
        print(f"\n{'='*60}")
        print(f"Starting analysis for domain: {domain}")
        print(f"{'='*60}\n")
        
        archived_urls = self.fetch_archived_urls(domain)
        
        if not archived_urls:
            print(f"No archived URLs found for {domain}")
            return []
        
        suspicious_results = []
        
        for idx, url in enumerate(archived_urls[:500]):
            if idx > 0 and idx % 50 == 0:
                print(f"Processed {idx}/{min(500, len(archived_urls))} URLs...")
            
            is_suspicious, reasons = self.is_suspicious_url(url)
            
            if not is_suspicious:
                continue
            
            print(f"\n[SUSPICIOUS] {url}")
            print(f"Reasons: {', '.join(reasons)}")
            
            archived_url, timestamp = self.get_archived_snapshot(url)
            
            if not archived_url:
                print("Could not get archived snapshot")
                suspicious_results.append({
                    "original_url": url,
                    "archived_url": None,
                    "timestamp": None,
                    "reasons": reasons,
                    "has_sensitive_data": False,
                    "findings": {},
                    "error": "Could not retrieve snapshot"
                })
                continue
            
            analysis = self.fetch_and_analyze(archived_url)
            
            result = {
                "original_url": url,
                "archived_url": archived_url,
                "timestamp": timestamp,
                "reasons": reasons,
                "has_sensitive_data": analysis.get("has_sensitive_data", False),
                "findings": analysis.get("findings", {}),
                "content_length": analysis.get("content_length", 0),
                "error": analysis.get("error")
            }
            
            suspicious_results.append(result)
            
            if analysis.get("has_sensitive_data"):
                print(f"[ALERT] Sensitive data detected!")
                for category, matches in analysis.get("findings", {}).items():
                    print(f"  - {category}: {len(matches)} match(es)")
            
            time.sleep(0.5)
        
        print(f"\n{'='*60}")
        print(f"Analysis complete for {domain}")
        print(f"Total suspicious URLs found: {len(suspicious_results)}")
        print(f"URLs with sensitive data: {sum(1 for r in suspicious_results if r['has_sensitive_data'])}")
        print(f"{'='*60}\n")
        
        return suspicious_results
