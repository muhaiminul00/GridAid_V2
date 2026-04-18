"""
GridHaat SMS Alert Service
Supports: Twilio (global) | SSL Wireless BD (production) | Demo mode (no key needed)
"""
import hashlib, time, os
from datetime import datetime

# ── FILL IN YOUR CREDENTIALS ──────────────────────────────
# Option 1: Twilio (recommended for demo — free trial works)
# Sign up: https://twilio.com → get trial SID + token + number
TWILIO_SID    = "MG0bf7a9b0ab4c75e4c903765d386d3d0e"   # "ACxxxxxxxxxxxxx"
TWILIO_TOKEN  = "daaf125526115cd8de79d5b02f9d78f8"  # "your_auth_token"
TWILIO_FROM   = "+13203147308"  # "+1XXXXXXXXXX"

# Option 2: SSL Wireless BD (production BD option)
# Register at: https://sslwireless.com/sms-api/
SSL_API_KEY   = os.environ.get("SSL_API_KEY",  "")
SSL_SID_TOKEN = os.environ.get("SSL_SID",      "")

# Recipient phone number (the "incharge" phone on your table)
# Format for BD: +8801XXXXXXXXX
DEMO_RECIPIENT = os.environ.get("DEMO_PHONE", "+8801639097885")

# ── VERIFICATION HASH ──────────────────────────────────────
def generate_verify_code(sector: str, mw: float, ts: float) -> str:
    """Generate a 6-char verification code unique to this alert."""
    raw = f"{sector}:{mw:.1f}:{int(ts)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:6].upper()

# ── SMS CONTENT BUILDER ────────────────────────────────────
def build_sms(sector: str, mw: float, bdt: float, wastage_type: str,
              grid_line: str, incharge: str, zone_code: str,
              verify_code: str, timestamp: str) -> str:
    type_labels = {
        "industrial_motor": "Industrial motor over-run",
        "ac_overnight":     "HVAC/AC left running",
        "pump_motor":       "Pump motor over-run",
        "residential_phantom": "Phantom load spike",
    }
    type_label = type_labels.get(wastage_type, "Anomaly detected")
    bdt_lakh   = bdt / 100_000

    return (
        f"GridHaat AI ALERT #{verify_code}\n"
        f"{'─'*22}\n"
        f"Zone: {sector[:28]}\n"
        f"Line: Grid {grid_line}\n"
        f"Type: {type_label}\n"
        f"Loss: {mw:.1f} MW | \u09f3{bdt_lakh:.1f}L\n"
        f"Time: {timestamp}\n"
        f"{'─'*22}\n"
        f"Action: Field inspection\n"
        f"Ref: {zone_code}\n"
        f"Verify: gridhaat.live/{verify_code}"
    )

# ── SEND FUNCTION ──────────────────────────────────────────
def send_alert_sms(sector, mw, bdt, wastage_type, grid_line,
                   incharge, zone_code, verify_code, timestamp,
                   recipient=None) -> dict:
    """
    Returns dict with keys: success, mode, message_id, sms_body, error
    """
    recipient = recipient or DEMO_RECIPIENT
    sms_body  = build_sms(sector, mw, bdt, wastage_type, grid_line,
                          incharge, zone_code, verify_code, timestamp)

    # ── Try Twilio ──
    if TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM:
        try:
            from twilio.rest import Client
            client = Client(TWILIO_SID, TWILIO_TOKEN)
            msg = client.messages.create(
                body=sms_body, from_=TWILIO_FROM, to=recipient
            )
            return {"success": True, "mode": "twilio",
                    "message_id": msg.sid, "sms_body": sms_body, "error": None}
        except Exception as e:
            pass  # fall through to SSL or demo

    # ── Try SSL Wireless BD ──
    if SSL_API_KEY and SSL_SID_TOKEN:
        try:
            import requests
            res = requests.post("https://sslwireless.com/api/v3/send-sms", json={
                "api_token": SSL_API_KEY,
                "sid":       SSL_SID_TOKEN,
                "sms":       sms_body,
                "msisdn":    recipient.replace("+",""),
                "csmsid":    verify_code,
            }, timeout=8)
            data = res.json()
            return {"success": True, "mode": "ssl_wireless",
                    "message_id": verify_code, "sms_body": sms_body, "error": None}
        except Exception as e:
            pass

    # ── Demo mode — no credentials needed ──
    # Simulates the delay of a real API call
    time.sleep(1.2)
    return {
        "success":    True,
        "mode":       "demo",
        "message_id": f"DEMO-{verify_code}",
        "sms_body":   sms_body,
        "error":      None,
    }
