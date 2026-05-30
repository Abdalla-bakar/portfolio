import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Allow your deployed frontend(s) + local dev
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://localhost:8000,https://portfolio-theta-neon-82.vercel.app"
    ).split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
MAIL_TO = os.environ.get("MAIL_TO", "abdallabakar311@gmail.com")
MAIL_FROM = os.environ.get("MAIL_FROM", "onboarding@resend.dev")


class ContactPayload(BaseModel):
    name: str
    email: EmailStr
    subject: str = "Portfolio contact"
    message: str


@app.get("/")
def home():
    return {"status": "backend running"}


@app.post("/contact")
async def contact(payload: ContactPayload):
    name = payload.name.strip()
    email = payload.email.strip()
    subject = payload.subject.strip()
    message = payload.message.strip()

    if not all([name, email, message]):
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "All fields are required"},
        )

    if not RESEND_API_KEY:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Email service not configured"},
        )

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
            return {"success": True, "message": "Email sent!"}

        print(f"Resend error {response.status_code}: {response.text}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Failed to send"},
        )

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Failed to send email"},
        )
