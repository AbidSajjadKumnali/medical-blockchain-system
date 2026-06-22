# ⚕️ MedChain EMR — Blockchain-Based Electronic Medical Records

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/Database-SQLite-green?logo=sqlite)
![Blockchain](https://img.shields.io/badge/Blockchain-SHA256-orange)
![AES](https://img.shields.io/badge/Encryption-AES--256--GCM-purple)
![JWT](https://img.shields.io/badge/Auth-JWT-yellow)

A **production-grade, secure blockchain-based Electronic Medical Record (EMR) management system** built with Python and Streamlit.

---

## 🏗️ Architecture

```
medical-blockchain-system/
├── app.py                  # Main Streamlit entry point
├── requirements.txt
├── README.md
├── .env                    # Environment variables
├── Dockerfile
├── docker-compose.yml
│
├── blockchain/             # Blockchain logic
│   ├── block.py            # Block data structure
│   ├── blockchain.py       # Chain management & persistence
│   ├── proof.py            # Proof-of-Integrity mechanism
│   └── validator.py        # Chain validation & tamper detection
│
├── crypto/                 # Cryptography
│   ├── encrypt.py          # AES-256-GCM encryption
│   ├── decrypt.py          # AES-256-GCM decryption
│   ├── hash_util.py        # SHA-256 utilities
│   └── key_manager.py      # Key derivation (PBKDF2)
│
├── database/               # Data layer
│   ├── db.py               # SQLite connection manager
│   ├── models.py           # User, Patient, Record, Audit models
│   ├── migrations.py       # Schema creation
│   └── seed.py             # Demo data seeding
│
├── auth/                   # Authentication
│   ├── auth.py             # Login / register / logout
│   ├── jwt_handler.py      # JWT create/verify
│   ├── password_utils.py   # bcrypt hashing
│   └── roles.py            # RBAC permissions
│
├── modules/                # UI Modules
│   ├── add_record.py
│   ├── view_records.py
│   ├── update_record.py
│   ├── delete_record.py
│   ├── upload_reports.py
│   ├── patient_dashboard.py
│   ├── doctor_dashboard.py
│   ├── admin_dashboard.py
│   ├── analytics.py
│   └── audit_logs.py
│
├── utils/                  # Utilities
│   ├── helpers.py
│   ├── validators.py
│   ├── logger.py
│   ├── constants.py
│   └── session_manager.py
│
├── data/                   # Runtime data (gitignored)
│   ├── blockchain.json
│   ├── database.db
│   ├── uploads/
│   └── logs/
│
├── static/
│   └── style.css
│
└── tests/
    ├── test_blockchain.py
    ├── test_auth.py
    ├── test_database.py
    └── test_crypto.py
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### 1. Clone and Install

```bash
git clone https://github.com/yourname/medical-blockchain-system.git
cd medical-blockchain-system

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env .env.local
# Edit .env — change SECRET_KEY and AES_KEY for production
```

### 3. Run the Application

```bash
streamlit run app.py
```

Visit: **http://localhost:8501**

---

## 🐳 Docker Deployment

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

---

## 🔑 Demo Credentials

| Role    | Username        | Password       |
|---------|-----------------|----------------|
| Admin   | `admin`         | `Admin@1234`   |
| Doctor  | `dr_smith`      | `Doctor@1234`  |
| Doctor  | `dr_patel`      | `Doctor@1234`  |
| Patient | `patient_john`  | `Patient@1234` |
| Patient | `patient_sara`  | `Patient@1234` |

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Individual test suites
python -m pytest tests/test_blockchain.py -v
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_database.py -v
python -m pytest tests/test_crypto.py -v
```

---

## 🔐 Security Features

| Feature | Implementation |
|---------|---------------|
| Password Hashing | bcrypt (12 rounds) |
| Data Encryption | AES-256-GCM |
| Key Derivation | PBKDF2-HMAC-SHA256 |
| Authentication | JWT (HS256, 8hr expiry) |
| Access Control | Role-Based (Admin/Doctor/Patient) |
| Blockchain | SHA-256, Proof-of-Integrity |
| SQL Injection | Parameterized queries |
| Input Validation | Regex + sanitization |
| Activity Tracking | Full audit log |

---

## ⛓️ Blockchain Design

Each medical record creates a new blockchain block containing:

```json
{
  "index": 5,
  "timestamp": "2024-01-15T10:30:00+00:00",
  "encrypted_data": "<AES-256-GCM ciphertext>",
  "previous_hash": "<SHA-256 of previous block>",
  "doctor_id": "<UUID>",
  "patient_id": "<UUID>",
  "nonce": 12,
  "hash": "<SHA-256 of this block>"
}
```

Tampering with any block breaks the cryptographic hash chain, which is detected instantly during validation.

---

## 📊 Features by Role

### 🛡️ Admin
- System analytics dashboard
- User management (activate/deactivate)
- Full audit log access
- Blockchain monitoring & validation
- Record deletion

### 🩺 Doctor
- Add medical records (creates blockchain block)
- Update diagnosis/prescriptions
- Upload patient reports/files
- View patient history
- Analytics & audit logs

### 👤 Patient
- View own records
- Download uploaded reports
- Blockchain verification
- Health profile overview

---

## 📦 Tech Stack

- **Frontend**: Streamlit 1.32
- **Blockchain**: Python (custom SHA-256 chain)
- **Database**: SQLite (via parameterized queries)
- **Encryption**: AES-256-GCM (cryptography lib)
- **Auth**: JWT (PyJWT) + bcrypt
- **Charts**: Plotly
- **Containerization**: Docker + docker-compose

---

## 📝 License

MIT License — Free for educational and research use.

---

*Built as an  project demonstrating blockchain integration in healthcare systems BY Abid and Manshi Team *
