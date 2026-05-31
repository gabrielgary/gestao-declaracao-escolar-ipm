
# 🎓 SIGE-Doc | Automated Academic Document Management System

![Project Status](https://img.shields.io/badge/Status-In_Development-blue?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Clean_/_Layered-orange?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Digital_Signature-red?style=for-the-badge)

**SIGE-Doc** is an enterprise-grade software solution designed to completely digitalize and automate the academic document issuance workflow (Enrollment Certificates, Transcripts, and official Declarations) in educational institutions. 

By eliminating physical queues and bureaucracy, the platform enables students to request, pay for, and receive authenticated digital documents securely from anywhere.

---

## 🎯 The Problem vs. The Engineering Solution

*   **The Bureaucracy (Old Way):** Massive physical lines at the school registry, manual data verification, 7-15 days processing time, and vulnerability to document forgery.
*   **The SIGE-Doc Way:** On-demand request via Student Portal, instant payment processing via **Angolan Multicaixa Express / RUP**, automated PDF generation with an unforgeable cryptographic **Digital Signature and QR Code Validation**.

---

## 🚀 Core Features

### 📄 Document Generation Engine
*   **Dynamic Templating:** Seamless generation of official transcripts and school certificates using strict database records.
*   **Anti-Forgery Security:** Every generated PDF is embedded with a unique cryptographic hash and a verification watermarking layer.
*   **Public Validator Endpoint:** A secure, public-facing portal where third-party entities (employers or other universities) can scan the document's QR Code to verify its authenticity in real-time.

### 🏦 Financial Gateway & Automation
*   **Local Payment Integration:** Support for **Multicaixa Express** API and **RUP** (Referência Única de Pagamento) generation.
*   **Asynchronous Verification:** The system automatically unlocks the document download link immediately after the banking webhook confirms the transaction.

### 🧠 Intelligent Virtual Assistant (Yasmin)
*   An integrated NLP-driven chatbot acting as a 24/7 helpdesk to assist students and parents with document requirements and application statuses.

---

## 🏗️ Architecture & Tech Stack

The system is built on **Clean Architecture** and **Layered Design** principles, ensuring strict separation of concerns, high testability, and independence from external frameworks.

*   **Backend:** Django & Django REST Framework (Python) - Robust business logic, security middleware, and secure ORM.
*   **Frontend:** React.js & TypeScript - Premium, highly accessible UI/UX inspired by dark/light data-dense dashboards.
*   **Database:** PostgreSQL - Advanced relational schema modeling for complex academic history and audit logs.
*   **Infrastructure:** Linux (Ubuntu Server 24.04 LTS) - Virtualized environment managed with custom automated Bash scripts.

---

## 📂 Project Structure (Clean Pattern)

```bash
gestao-escolar-fim-course/
├── backend/                # Server-Side API & Domain Logic
│   ├── apis/               # Interface Adapters (Serializers, ViewSets, Endpoints)
│   ├── services/           # Pure Business Logic Layer (Clean Code execution)
│   ├── models/             # Database Schemas & PostgreSQL Entities
│   └── core/               # Framework Configurations (Settings, Routing)
├── frontend/               # Client-Side Interface (React.js)
│   ├── src/Components/     # Reusable UI Design System
│   ├── src/Context/        # Global State (Auth RBAC, Theme management)
│   └── src/Services/       # API Consumer Layer (Axios configuration)
└── Yasmin/                 # Autonomous AI Assistant Module

```

---

## 🔧 Local Development Quickstart

### Prerequisites

* Node.js (v18+)
* Python (3.10+)
* PostgreSQL Server running on Ubuntu/Local machine

### 1. Spin up the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

```

### 2. Launch the Frontend

```bash
cd frontend
npm install
npm run dev

```

---

## 🔒 Security Compliance

* **RBAC (Role-Based Access Control):** Granular permission layers ensuring only authorized registrars can approve critical requests.
* **Full Audit Trail:** Immutable system logs tracking exactly who generated, approved, or revoked any document.
* **Data Protection:** Password hashing utilizing advanced PBKDF2 algorithms and strict CORS/CSRF configurations.

---

## 👨‍💻 Author

**Gabriel Pedro Aurélio**
*Back-End Engineer | Clean Architecture & Linux Enthusiast*

---

*Developed with technical rigor to solve real-world educational infrastructure bottlenecks.*

```

```
