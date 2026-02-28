# Investment Platform with User Management and Referral System

This is a fully functional investment platform built with Flask, where users can:
- Register and log in securely
- Make deposits ($50-$5000)
- Earn daily returns (2% per day)
- Submit and track withdrawal requests
- View their dashboard with financial statistics
- Participate in a 3-level referral program (5%, 2%, 1%)
- Receive notifications from admin
- Update profile and security settings

## Features

- **User Authentication System**: Secure email and password-based login
- **Deposit Management**: Process and track deposits
- **Daily Earnings**: Automatic calculation of daily returns (2% per day)
- **Withdrawal System**: Request and track withdrawals
- **3-Level Referral System**: Earn commissions from referrals
- **User Dashboard**: View all account statistics and activities
- **Profile Management**: Update profile information
- **Notification Center**: Receive system and admin notifications
- **Admin Panel**: Full admin control for managing users, deposits, and withdrawals
- **Mobile Responsive Design**: Google-inspired clean UI design

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite (default) or other database supported by SQLAlchemy

### Installation Steps

1. Clone the repository
```bash
git clone <repository-url>
cd investment-platform
```

2. Create a virtual environment
```bash
python -m venv venv
```

3. Activate the virtual environment
```bash
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

4. Install required packages
```bash
pip install -r requirements.txt
```

5. Create a .env file in the root directory with the following content:
```
SECRET_KEY=your_secret_key_here
DATABASE_URI=sqlite:///investment.db
```

6. Initialize the database
```bash
python app.py
```

7. Create an admin account
```
# Access the application in your browser
# Register a new account (this will be user ID 1, which is the admin)
```

## Usage

1. Start the application
```bash
python app.py
```

2. Access the application in your web browser at `http://127.0.0.1:5000`

3. Register for a new account or log in

4. Explore the dashboard and features

## Admin Features

- Access admin panel at `/admin` route
- Manage user accounts
- Approve/reject deposits and withdrawals
- Send global notifications
- View system statistics
- Add bonuses or penalties to user accounts

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy ORM with SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login
- **Form Handling**: Flask-WTF
- **Scheduler**: APScheduler (for daily earnings)
- **Security**: Werkzeug Security for password hashing

## Project Structure

```
investment-platform/
├── app.py              # Main application file
├── models.py           # Database models
├── routes.py           # User routes
├── admin_routes.py     # Admin routes
├── requirements.txt    # Python dependencies
├── static/             # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
└── templates/          # HTML templates
    ├── admin/          # Admin templates
    └── partials/       # Reusable template parts
```

## Security Considerations

- Passwords are hashed using Werkzeug's security functions
- CSRF protection for forms
- Input validation on all forms
- User session management with Flask-Login

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application is intended for demonstration purposes only. It is not intended for use with real money. The creators take no responsibility for any financial loss or legal issues arising from using this software for actual investments. 