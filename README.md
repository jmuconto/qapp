# qApp – Queue Management SaaS via WhatsApp/SMS

**qApp** is a minimalist open-source platform for queue management with client interaction via SMS and WhatsApp. Designed for banks, clinics, government services, restaurants, and more.

## 🚀 Features

- Attendant dashboard for managing queues (pause, call next, switch, cancel, add)
- Manager/admin dashboard with analytics and settings
- Customizable messages via Twilio (SMS/WhatsApp)
- Real-time interactions using HTMX
- Pay-as-you-go model and support for dedicated/custom deployments

## 🧱 Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTMX + Tailwind CSS
- **Automation**: n8n for workflows and background jobs
- **Messaging**: Twilio (SMS & WhatsApp)
- **Database**: SQLite (for local/testing), pluggable with Postgres
- **Deployment**: Designed to be container-ready or simple local server

## ⚙️ Local Development

```bash
git clone git@gitlab.com:YOUR_USERNAME/qapp.git
cd qapp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
