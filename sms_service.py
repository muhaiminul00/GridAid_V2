"""
GridHaat Email Alert Service
Supports: Gmail SMTP (production) | Demo mode (no key needed)
"""
import hashlib, smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── EMAIL CREDENTIALS ─────────────────────────────────────
EMAIL_SENDER         = "muhaiminulabedin00@gmail.com"  # Sender Gmail
EMAIL_PASSWORD       = "zapb lplw efdn aidk"           # Gmail App Password
EMAIL_SMTP_HOST      = "smtp.gmail.com"
EMAIL_SMTP_PORT      = 587
DEMO_RECIPIENT_EMAIL = "afnanohi01817@gmail.com"       # Default recipient

# ── VERIFICATION HASH ─────────────────────────────────────
def generate_verify_code(sector: str, mw: float, ts: float) -> str:
    """Generate a 6-char verification code unique to this alert."""
    raw = f"{sector}:{mw:.1f}:{int(ts)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:6].upper()

# ── EMAIL BODY BUILDER ────────────────────────────────────
def build_email_body(sector: str, mw: float, bdt: float, wastage_type: str,
                     grid_line: str, incharge: str, zone_code: str,
                     verify_code: str, timestamp: str) -> str:
    type_labels = {
        "industrial_motor":    "Industrial motor over-run",
        "ac_overnight":        "HVAC/AC left running",
        "pump_motor":          "Pump motor over-run",
        "residential_phantom": "Phantom load spike",
    }
    type_label = type_labels.get(wastage_type, "Anomaly detected")
    bdt_lakh   = bdt / 100_000
    return (
        f"GridHaat AI ALERT #{verify_code}\n"
        f"{'─'*22}\n"
        f"Zone    : {sector[:28]}\n"
        f"Line    : Grid {grid_line}\n"
        f"Type    : {type_label}\n"
        f"Loss    : {mw:.1f} MW | ৳{bdt_lakh:.1f}L\n"
        f"Time    : {timestamp}\n"
        f"Incharge: {incharge}\n"
        f"{'─'*22}\n"
        f"Action  : Field inspection required\n"
        f"Ref     : {zone_code}\n"
        f"Verify  : gridhaat.live/{verify_code}"
    )

# ── SEND FUNCTION ─────────────────────────────────────────
def send_alert_email(sector, mw, bdt, wastage_type, grid_line,
                     incharge, zone_code, verify_code, timestamp,
                     recipient_email=None) -> dict:
    """
    Sends alert via Gmail SMTP.
    Returns dict with keys: success, mode, message_id, email_body, error
    """
    recipient_email = recipient_email or DEMO_RECIPIENT_EMAIL

    email_body = build_email_body(sector, mw, bdt, wastage_type, grid_line,
                                  incharge, zone_code, verify_code, timestamp)

    subject = f"⚡ GridHaat Alert — Sector {sector} | {wastage_type}"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = recipient_email

        msg.attach(MIMEText(email_body, "plain"))

        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())

        return {
            "success":    True,
            "mode":       "smtp_email",
            "message_id": f"{sector}-{verify_code}",
            "email_body": email_body,
            "error":      None
        }

    except smtplib.SMTPAuthenticationError as e:
        return {"success": False, "mode": "smtp_email",
                "message_id": None, "email_body": email_body,
                "error": f"Auth failed — check EMAIL_PASSWORD: {e}"}

    except smtplib.SMTPException as e:
        return {"success": False, "mode": "smtp_email",
                "message_id": None, "email_body": email_body,
                "error": f"SMTP error: {e}"}

    except Exception as e:
        return {"success": False, "mode": "smtp_email",
                "message_id": None, "email_body": email_body,
                "error": f"Unexpected error: {e}"}
