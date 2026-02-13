import json
import os
from typing import List

class EmailConfig:
    def __init__(self, config_file='email_recipients.json'):
        self.config_file = config_file
        self.recipients = self._load_config()
    
    def _load_config(self) -> List[str]:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return data.get('recipients', [])
            except Exception as e:
                print(f"Error loading email config: {str(e)}")
                return []
        return []
    
    def _save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'recipients': self.recipients}, f, indent=2)
        except Exception as e:
            print(f"Error saving email config: {str(e)}")
    
    def get_recipients(self) -> List[str]:
        return self.recipients.copy()
    
    def update_recipients(self, recipients: List[str]):
        valid_recipients = [email.strip() for email in recipients if email.strip()]
        self.recipients = list(set(valid_recipients))
        self._save_config()
    
    def add_recipient(self, email: str):
        email = email.strip()
        if email and email not in self.recipients:
            self.recipients.append(email)
            self._save_config()
    
    def remove_recipient(self, email: str):
        email = email.strip()
        if email in self.recipients:
            self.recipients.remove(email)
            self._save_config()
