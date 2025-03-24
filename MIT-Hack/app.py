from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

PERSPECTIVE_API_KEY = "YOUR_GOOGLE_PERSPECTIVE_API_KEY"
SLACK_WEBHOOK_URL = "YOUR_SLACK_WEBHOOK_URL"
SENDGRID_API_KEY = "YOUR_SENDGRID_API_KEY"
ADMIN_EMAIL = "admin@example.com"

class Message(BaseModel):
    message: str

@app.post("/analyze")
async def analyze_text(data: Message):
    """Analyzes the text for harassment using Perspective API."""
    api_url = f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={PERSPECTIVE_API_KEY}"
    request_data = {
        "comment": {"text": data.message},
        "languages": ["en"],
        "requestedAttributes": {"TOXICITY": {}}
    }
    response = requests.post(api_url, json=request_data)
    score = response.json()["attributeScores"]["TOXICITY"]["summaryScore"]["value"]

    is_harassment = score > 0.7  # Adjust threshold as needed
    return {"is_harassment": is_harassment}

@app.post("/notify-admin")
async def notify_admin(data: Message):
    """Sends alert to admin via Slack and Email."""
    message = data.message

    # Send Slack Notification
    slack_data = {"text": f"🚨 Harassment Alert: {message}"}
    requests.post(SLACK_WEBHOOK_URL, json=slack_data)

    # Send Email Notification
    email_data = {
        "personalizations": [{"to": [{"email": ADMIN_EMAIL}]}],
        "from": {"email": "no-reply@harassmentdetector.com"},
        "subject": "🚨 Harassment Detected",
        "content": [{"type": "text/plain", "value": f"Message flagged: {message}"}]
    }
    requests.post("https://api.sendgrid.com/v3/mail/send",
                  json=email_data,
                  headers={"Authorization": f"Bearer {SENDGRID_API_KEY}",
                           "Content-Type": "application/json"})

    return {"status": "Admin Notified"}
