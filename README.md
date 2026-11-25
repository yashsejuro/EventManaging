# ClubEvents — Campus, in Motion ⚡

<div align="center">

<img src="static/images/favicon.svg" alt="ClubEvents Logo" width="100" height="100">

### Discover, join, and organize unforgettable campus experiences.

**🌐 Live Platform:** [https://eventmanaging-blue.vercel.app](https://eventmanaging-blue.vercel.app)

[![Live Site](https://img.shields.io/badge/Live_Site-Online-success?style=for-the-badge&logo=vercel&logoColor=white)](https://eventmanaging-blue.vercel.app)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

## 🌟 What is ClubEvents?

University portals and campus bulletin boards are usually scattered, clunky, and outdated. Important hackathons get lost in chat groups, workshop registrations fill up silently, and sports tournaments struggle with manual attendance sheets.

**ClubEvents** reimagines the campus experience. It brings your university's entire social and academic calendar into one motion-driven, beautifully crafted community hub. Whether you're a freshman hunting for a robotics workshop or a club president running an annual cultural fest, ClubEvents makes it effortless.

---

## ✨ Features at a Glance

### 🎓 For Students & Attendees
* **Explore by Vibe & Category**: Filter events seamlessly across **Tech, Workshops, Guest Talks, Cultural Fests, Gaming, and Sports**.
* **Real-Time Seat Tracking**: Live countdown of remaining spots—never wonder if an auditorium has space left.
* **Instant One-Click RSVP**: Reserve a seat in seconds and receive an automated digital entry pass.
* **Personal Ticket Wallet**: Access all your registered passes, dates, timings, and venues under **My Tickets**.
* **Zero Lag & Fluid Motion**: Experience smooth kinetic scrolling, interactive 3D hero canvas, and atmospheric ambient lighting.

### 🛠️ For Club Leads & Organizers
* **Organizer Command Center**: Create, publish, update, and manage campus events with custom cover posters and capacity limits.
* **Live Attendee Management**: Track bookings in real time as registrations roll in.
* **One-Click CSV Export**: Download instant attendance sheets ready for university administration and faculty advisors.
* **Campus Operations Console**: A custom-designed, glassmorphic management dashboard featuring live metric cards and recent community activity feeds.

---

## 🎨 Visual Design & Aesthetics

ClubEvents is built on a custom design system prioritizing kinetic energy and modern web aesthetics:

* **Typography**: Expressive headline hierarchy using **Space Grotesk**, paired with ultra-legible **Inter** for UI copy.
* **Atmospheric Glassmorphism**: Frosted glass cards with backdrop blur filters, glowing lime (`#d6ff3f`) and electric violet (`#8067ff`) ambient lighting.
* **Infinite Energy**: High-velocity category marquee and interactive Three.js 3D physics geometry.
* **Mobile-First Responsiveness**: Designed from the ground up for smartphones, tablets, and desktop displays.

---

## 🚀 Live Demo & Quick Links

| Destination | Link | Credentials |
|---|---|---|
| **Public Website** | [eventmanaging-blue.vercel.app](https://eventmanaging-blue.vercel.app) | Browse and explore without logging in |
| **Student Portal** | [eventmanaging-blue.vercel.app/accounts/login/](https://eventmanaging-blue.vercel.app/accounts/login/) | User: `demo_student` (or `student` / `demo12345`) \| Password: `Demo@12345` |
| **Organizer Portal** | [eventmanaging-blue.vercel.app/organizer/](https://eventmanaging-blue.vercel.app/organizer/) | User: `demo_organizer` (or `organizer` / `demo12345`) \| Password: `Demo@12345` |
| **Admin Operations** | [eventmanaging-blue.vercel.app/admin/](https://eventmanaging-blue.vercel.app/admin/) | User: `demo_admin` (or `admin` / `admin12345`) \| Password: `Demo@12345` |

---

## 🛠️ Technology Stack

* **Core Framework**: Django 5.2 & Python 3.12
* **Database**: PostgreSQL (Production) / SQLite (Local Demo)
* **Frontend Design**: Semantic HTML5, Modern CSS3 with CSS Variables & Glassmorphism, Three.js 3D Canvas, GSAP, Lenis Smooth Scroll
* **Deployment & Cloud**: Vercel Serverless Functions (`@vercel/python`) with Edge CDN Static Pipelines (`@vercel/static-build`) & WhiteNoise
* **Telemetry**: Integrated Vercel Web Analytics

---

<details>
<summary><b>💻 For Developers: Running Locally</b></summary>

<br>

If you want to clone and run ClubEvents on your local machine:

```powershell
# 1. Clone repository
git clone https://github.com/yashsejuro/EventManaging.git
cd EventManaging

# 2. Create and activate virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1   # On macOS/Linux: source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Migrate database and seed demo events
python manage.py migrate
python manage.py seed_demo

# 5. Start development server
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

</details>

---

<div align="center">

Made with 💛 for the people who make campus happen.

</div>
