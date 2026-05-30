# Portfolio Backend (Flask + Resend)

Receives contact-form submissions and forwards them to your inbox via Resend.

## Environment variables
- `RESEND_API_KEY` — your Resend API key (https://resend.com/api-keys)
- `MAIL_TO` — recipient inbox (default: abdallabakar311@gmail.com)
- `MAIL_FROM` — verified sender (default: onboarding@resend.dev — works without domain verification)
- `ALLOWED_ORIGINS` — comma-separated list of allowed frontend origins (e.g. `https://your-site.vercel.app`)
- `PORT` — provided automatically by Render

## Local run
```bash
cd backend
pip install -r requirements.txt
export RESEND_API_KEY=re_xxx
export MAIL_TO=abdallabakar311@gmail.com
python main.py
```

## Render deploy (Web Service)
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn main:app`
- Add env vars: `RESEND_API_KEY`, `MAIL_TO`, `ALLOWED_ORIGINS`
