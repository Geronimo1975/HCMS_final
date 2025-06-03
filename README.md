# Salon Management System

A comprehensive salon management platform for the German market, supporting multiple languages and featuring advanced booking, payment, and communication capabilities.

## 🌟 Features

### Salon Partner Portal
- Secure registration and authentication
- Business profile management
- Service and schedule management
- Calendar view for bookings
- Subscription-based features

### Customer Portal
- Service discovery by location and category
- Online booking and payment
- Email/SMS confirmations
- Real-time chat with providers

### Advanced Features
- Live chat system
- Automated workflows
- Geolocation services
- Multilingual support (DE, EN, ES)

## 🛠 Tech Stack

- **Backend**: Django 5.0
- **Database**: PostgreSQL
- **Frontend**: HTML + Tailwind CSS
- **Task Queue**: Celery + Redis
- **Payment**: Stripe
- **Real-time**: Django Channels
- **PDF**: WeasyPrint
- **Maps**: OpenCage + Leaflet.js

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis
- Node.js 18+ (for Tailwind)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/salon-management.git
cd salon-management
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## 📁 Project Structure

```
salon_management/
├── apps/
│   ├── accounts/          # User management
│   ├── bookings/          # Booking system
│   ├── businesses/        # Salon profiles
│   ├── chat/             # Live chat
│   ├── payments/         # Payment processing
│   └── services/         # Service management
├── config/               # Project settings
├── static/              # Static files
├── templates/           # HTML templates
└── locale/             # Translation files
```

## 🔒 Security

- JWT authentication
- Role-based access control
- Data encryption
- HIPAA compliance for medical data
- Regular security audits

## 🌍 Internationalization

Supported languages:
- German (DE) - Primary
- English (EN)
- Spanish (ES)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support, email support@salonmanagement.de or join our Slack channel.
# HCMS_final
