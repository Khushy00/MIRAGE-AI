import re
from typing import Dict, Any

class DetectionEngine:
    def __init__(self):
        # Regex for common SQLi
        self.sqli_pattern = re.compile(
            r"(?i)(\%27)|(\')|(\-\-)|(\%23)|(#)|(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|TRUNCATE)"
        )
        
        # Regex for XSS
        self.xss_pattern = re.compile(
            r"(?i)(<\s*script>)|(javascript:)|(onerror=)|(onload=)|(<.*>.*<\/.*>)"
        )
        
        # Track brute force attempts (In-memory for prototype, normally Redis)
        self.login_attempts = {}

    def analyze_payload(self, ip: str, endpoint: str, payload: str, is_login: bool = False) -> Dict[str, Any]:
        """
        Analyzes the incoming payload for malicious signatures.
        Returns a dict with attack type, severity, and recommended action.
        """
        
        if is_login:
            # Check Brute Force
            attempts = self.login_attempts.get(ip, 0) + 1
            self.login_attempts[ip] = attempts
            if attempts > 5:
                return {
                    "is_malicious": True,
                    "attack_type": "Brute Force",
                    "severity": "High",
                    "action": "Block IP and Redirect to tarpit"
                }

        if payload:
            if self.xss_pattern.search(payload):
                return {
                    "is_malicious": True,
                    "attack_type": "XSS (Cross-Site Scripting)",
                    "severity": "High",
                    "action": "Block Request and Redirect to Honeypot"
                }
                
            if self.sqli_pattern.search(payload):
                return {
                    "is_malicious": True,
                    "attack_type": "SQL Injection",
                    "severity": "Critical",
                    "action": "Drop Request and Alert SOC"
                }

        return {
            "is_malicious": False,
            "attack_type": "None",
            "severity": "Low",
            "action": "Allow"
        }

engine = DetectionEngine()
