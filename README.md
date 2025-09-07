# qApp – Queue Management SaaS via Email

**qApp** is a minimalist, open-source queue management platform that enables businesses to interact with clients through **email**. Perfectly suited for **banks, clinics, government offices, restaurants**, and more, qApp simplifies the queueing experience for both staff and customers.  

---

## 🚀 Features

- **Attendant Dashboard**  
  Manage queues efficiently: pause, call next, switch, cancel, or add clients.  

- **Manager/Admin Dashboard**  
  Access analytics, track performance, and configure settings.  

- **Customizable Email Notifications**  
  Send automated notifications via **email**, fully configurable per organization.  

- **Real-Time Interactions**  
  Powered by **HTMX**, allowing dynamic updates without full page reloads.  

- **Flexible Deployment & Pricing**  
  Supports a **pay-as-you-go model**, dedicated deployments, or local server setups.  

---

## 🧱 Tech Stack

| Layer       | Technology                              |
|------------|----------------------------------------|
| Backend    | FastAPI (Python)                        |
| Frontend   | HTMX + Tailwind CSS                     |
| Automation | n8n for workflows and background jobs   |
| Messaging  | Email (SMTP or service like SendGrid)   |
| Database   | SQLite (for local/testing), pluggable with Postgres |
| Deployment | Container-ready or simple local server |

---

### Why qApp?

- Lightweight, minimal, and open-source.  
- Enables organizations to manage queues digitally without heavy infrastructure.  
- Fast and flexible—works on both small setups and enterprise deployments.  
- Easy integration with email ensures clients are notified in real time.
