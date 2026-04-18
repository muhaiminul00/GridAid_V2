# GridHaat V2 — Setup & Run Guide

## Quick start (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy your data from gridhaat_demo (or regenerate)
# If you already ran gridhaat_demo scripts, link the data:
#   The dashboard looks for ../gridhaat_demo/data/
# OR run from the gridhaat_v2 folder and adjust the path in dashboard_v2.py

# 3. Run the dashboard
streamlit run dashboard_v2.py
```

---

## Enabling real SMS (CRITICAL for competition)

### Option A: Twilio (recommended — 5 min setup)
1. Sign up free at https://www.twilio.com
2. Get your: Account SID, Auth Token, Trial phone number
3. Set environment variables:

```bash
export TWILIO_SID="ACffbe5fd39e61b7f0ea9d676673270123"
export TWILIO_TOKEN="daaf125526115cd8de79d5b02f9d78f8"
export TWILIO_FROM="+13203147308"   # your Twilio number
export DEMO_PHONE="+8801639097885"  # the phone on your table
```

Then run: `streamlit run dashboard_v2.py`

**IMPORTANT**: Twilio free trial can send to verified numbers only.
Add the judge's (or your teammate's) number as a verified number in Twilio console.
BD numbers (+880...) work fine with Twilio.

### Option B: SSL Wireless BD (authentic BD option)
Register at https://sslwireless.com/sms-api/
Requires BD business registration. Better for post-competition deployment.

```bash
export SSL_API_KEY="your_ssl_api_key"
export SSL_SID="your_ssl_sid"
```

### Demo mode (no credentials)
If no credentials are set, the SMS content is generated and shown
on screen exactly as it would be sent. Use this if you can't set up
Twilio in time. Show judges the message content — it's equally impressive.

---

## The live demo script (memorize this)

**[Open dashboard on laptop connected to projector]**

"Bangladesh is wasting electricity right now. Watch this counter."
→ Point to the waste ticker in the sidebar

"Let me show you our AI detecting a real anomaly."
→ Go to Live Anomaly Demo page
→ Select "Narayanganj Industrial Zone"
→ Enter YOUR phone number (or teammate's)
→ Hit TRIGGER ANOMALY

"Our AI just detected an anomaly. Score: 91/100. 67 MW being lost."
→ Point to verification hash: "This code was just generated — #B7F2"

"Now watch."
→ Phone on table buzzes
→ Read SMS aloud: "GridHaat Alert #B7F2 — Narayanganj..."
→ "Same code. Same timestamp. Both came from the AI."

"The incharge is notified. Let me show you what happens next."
→ Go to Resolution Workflow
→ Click through steps (or have teammate click on their phone)

"67 MW recovered. In 90 seconds."
→ Go to Simulator
→ "Now if we deploy to 30% of factories..."
→ Drag slider
→ "1,100 MW. From software alone."

**Total demo time: 4-5 minutes. Unrepeatable.**

---

## Verify hash explanation (for when judges ask)

The verify code (e.g. #B7F2) is generated using SHA-256:
```python
hash = SHA256(f"{sector}:{mw}:{unix_timestamp}")[:6].upper()
```
It appears in:
1. The dashboard at the moment of detection
2. The SMS body simultaneously
3. The map popup

No human could coordinate this timing. It proves the system is live.
If a judge wants to verify: show them the source code live.

---

## Troubleshooting

**"Module not found"**: Run `pip install -r requirements.txt`
**Map not showing**: `pip install streamlit-folium`
**SMS not sending**: Check TWILIO_SID env variable is set
**Data not found**: Run generate_data.py + train_model.py in gridhaat_demo/ first
