# 🚀 Investment Platform - Professional SaaS Dashboard

A high-performance, secure, and visually stunning investment platform built with **Python Flask** and **SQLAlchemy**. This platform features a modern, responsive design inspired by Google's Material Design, complete with a robust multi-level referral system, 2FA security, and a comprehensive admin control panel.

---

## 💎 Core Features

### 👤 User Features
- **Intuitive Dashboard**: Real-time financial statistics including total balance, active investments, and pending withdrawals.
- **Investment Management**: Seamlessly make deposits ($50 - $5000) and track growth.
- **Daily Profit Collection**: Automated 2% daily returns with manual collection functionality.
- **Withdrawal System**: Secure request submission and status tracking.
- **3-Level Referral Program**: Earn commissions across three tiers (5%, 2%, 1%) with milestone bonuses.
- **Notification Center**: Real-time system updates and direct messages from administration.
- **Profile & Security**: Comprehensive settings to manage account details and security preferences.

### 🛡️ Security & Privacy
- **Two-Factor Authentication (2FA)**: Google Authenticator (TOTP) support with QR code setup.
- **Encrypted Sessions**: Secure session management to prevent unauthorized access.
- **Password Hashing**: Industry-standard Werkzeug security for protecting user credentials.
- **Password Recovery**: Secure email-based token system for resetting forgotten passwords.
- **Account Deletion**: User-initiated account removal with reason tracking.

### ⚙️ Admin Capabilities
- **Global Control Center**: Monitor total system users, deposits, and financial health.
- **User Management**: Search, view details, and manage individual user accounts.
- **Transaction Approval**: Manual review and approval/rejection for all deposits and withdrawals.
- **System Communications**: Send global notifications or targeted messages to specific users.
- **Financial Adjustments**: Ability to add manual bonuses or penalties to any account.
- **Audit Logs**: Track deleted accounts and historical system changes.

---

## 🎨 Design & UI/UX (CSS Theme)

The platform utilizes a **Modern Professional Theme** built on vanilla CSS variables for maximum flexibility and performance.

### 🌈 Color Palette
| Category | Variable | Hex Code | Purpose |
| :--- | :--- | :--- | :--- |
| **Primary** | `--primary-color` | `#2563eb` | Brand identity, primary buttons, active links |
| **Secondary** | `--secondary-color` | `#0891b2` | Success states, secondary accents |
| **Accent** | `--accent-color` | `#7c3aed` | Danger/Alert states, bold highlights |
| **Warning** | `--warning-color` | `#f59e0b` | Cautionary notices and pending status |
| **Neutral** | `--text-dark` | `#111827` | Primary typography and headings |
| **Surface** | `--surface-color` | `#f9fafb` | Backgrounds and card surfaces |

### 🖋️ Typography & Styling
- **Font Family**: [Inter](https://fonts.google.com/specimen/Inter) (sans-serif) for superior readability across all screen sizes.
- **Micro-animations**: Smooth transitions (0.2s - 0.3s) on hover, clicks, and state changes.
- **Material Components**: Ripple effects on buttons, floating labels in forms, and elevated cards with subtle shadows.
- **Fully Responsive**: Adaptive layouts for Mobile, Tablet, and Desktop using advanced media queries.

---

## 💻 Technology Stack

- **Backend**: Python 3.x, Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Security**: Flask-Login, PyOTP, Werkzeug
- **Frontend**: Semantic HTML5, Vanilla CSS3 (Custom Variables), JavaScript (ES6+)
- **Scheduler**: APScheduler for background interest calculations

---

## 🛠️ Installation & Setup

1. **Clone & Navigate**:
   ```bash
   git clone <repository-url>
   cd LAST-TRY
   ```

2. **Environment Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configuration**:
   Create a `.env` file:
   ```env
   SECRET_KEY=your_secure_secret
   DATABASE_URL=sqlite:///investment.db
   ```

4. **Initialize & Run**:
   ```bash
   python init_db.py  # First time setup
   python app.py
   ```

---

## 📂 Project Structure

```text
LAST-TRY/
├── app.py              # Main Entry Point
├── models.py           # Database Schema
├── routes.py           # User Interaction Logic
├── admin_routes.py     # Administrative Backend
├── two_factor_routes.py # Security & 2FA Logic
├── static/
│   ├── css/            # Style.css (Core Theme)
│   ├── js/             # Interactive Components
│   └── images/         # Assets
└── templates/          # Jinja2 HTML Templates
```

---

> [!IMPORTANT]
> This application is a demonstration platform. Ensure all financial integrations are thoroughly tested before production use.
