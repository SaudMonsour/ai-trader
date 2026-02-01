#!/usr/bin/env python3
"""
Telegram Alert Utility
Send alerts to Telegram on critical failures.

Usage:
    python tools/alert_telegram.py "Alert message here"

Environment Variables:
    TG_BOT_TOKEN: Telegram bot token
    TG_CHAT_ID: Telegram chat/group ID
"""
import os
import sys
import requests

TG_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")  # group or user id

def send_telegram(message: str) -> bool:
    """Send alert message to Telegram."""
    if not TG_TOKEN or not TG_CHAT_ID:
        print("⚠️  Telegram not configured. Skipping alert.", file=sys.stderr)
        print("   Set TG_BOT_TOKEN and TG_CHAT_ID environment variables.", file=sys.stderr)
        return False
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print("✅ Alert sent successfully")
            return True
        else:
            print(f"❌ Failed to send alert: HTTP {r.status_code}", file=sys.stderr)
            print(f"   Response: {r.text}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}", file=sys.stderr)
        return False

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python tools/alert_telegram.py <message>")
        print("Example: python tools/alert_telegram.py 'ALERT: State write failed'")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    ok = send_telegram(message)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
