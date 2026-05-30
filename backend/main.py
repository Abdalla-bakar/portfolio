import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow your deployed frontend(s) + local dev
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://localhost:8000"
    ).split(",") if o.strip()
]
CORS(app, origins=ALLOWED_ORIGINS)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
MAIL_TO = os.environ.get("MAIL_TO", "abdallabakar311@gmail.com")
MAIL_FROM = os.environ.get("MAIL_FROM", "onboarding@resend.dev")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "backend running"})


@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "Portfolio contact").strip()
    message = (data.get("message") or "").strip()

    if not all([name, email, message]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if not RESEND_API_KEY:
        return jsonify({"success": False, "message": "Email service not configured"}), 500

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": f"Portfolio <{MAIL_FROM}>",
                "to": [MAIL_TO],
                "reply_to": email,
                "subject": f"Portfolio: {subject} — {name}",
                "text": f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\n{message}",
                "html": f"""
                    <h2>New message from your portfolio</h2>
                    <p><b>Name:</b> {name}</p>
                    <p><b>Email:</b> {email}</p>
                    <p><b>Subject:</b> {subject}</p>
                    <p><b>Message:</b></p>
                    <p style="white-space:pre-wrap">{message}</p>
                """,
            },
            timeout=15,
        )

        if response.status_code in (200, 202):
            return jsonify({"success": True, "message": "Email sent!"})
        print(f"Resend error {response.status_code}: {response.text}")
        return jsonify({"success": False, "message": "Failed to send"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Failed to send email"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
