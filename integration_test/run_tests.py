import smtplib
import json
import random
import string
import sys
import time
from email.mime.text import MIMEText
import urllib.request # Standard lib to avoid installing requests if possible, but requests is easier. 
# actually, let's just use standard lib urllib to avoid 'pip install' step in the container command if we can, 
# but for clarity/robustness I'll use 'requests' and install it in the command.

RECIPIENT = "test@tienzo.net"
HERMES_HOST = "hermes"

def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def test_smtp():
    print(f"\n[SMTP] Testing SMTP delivery to {HERMES_HOST}:2525...")
    sender = "tester@hermes.local"
    subject = f"Hermes SMTP Test [{generate_id()}]"
    body = "This is a test message sent via the Hermes SMTP interface."
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = RECIPIENT

    try:
        with smtplib.SMTP(HERMES_HOST, 2525) as server:
            server.set_debuglevel(0) # Set to 1 for verbose output
            server.sendmail(sender, [RECIPIENT], msg.as_string())
        print("✅ [SMTP] Email sent successfully.")
    except Exception as e:
        print(f"❌ [SMTP] Failed: {e}")

def test_http():
    print(f"\n[HTTP] Testing HTTP API delivery to http://{HERMES_HOST}:8000/notify...")
    
    url = f"http://{HERMES_HOST}:8000/notify"
    data = {
        "channel": "email",
        "recipient": RECIPIENT,
        "subject": f"Hermes HTTP Test [{generate_id()}]",
        "body": "This is a test message sent via the Hermes HTTP API."
    }
    
    try:
        # Using standard urllib to keep container lightweight (no pip install needed)
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            if 200 <= response.status < 300:
                print(f"✅ [HTTP] Request successful. Response: {response.read().decode()}")
            else:
                print(f"❌ [HTTP] Failed with status {response.status}")
    except Exception as e:
        print(f"❌ [HTTP] Failed: {e}")

if __name__ == "__main__":
    print("Starting Hermes Integration Tests...")
    # Wait a moment for network resolution if spinning up simultaneously
    time.sleep(2) 
    
    test_http()
    test_smtp()
    print("\nTests completed.")
