# 🎉 EventPortal - Modern Event Management Platform

<div align="center">

![EventPortal Logo](https://img.shields.io/badge/EventPortal-Modern%20Event%20Management-0066ff?style=for-the-badge)

[![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1.3-7952B3?style=flat&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)

**A sophisticated Django-based web platform that connects volunteers with event opportunities through a modern, professional interface.**

[Live Demo](#) • [Documentation](#) • [Report Bug](#) • [Request Feature](#)

</div>

## ✨ Features

### 🎯 **Core Functionality**
- **Role-Based System**: Volunteers, Event Managers, and Admins with distinct permissions
- **Smart Matching**: Advanced filtering and search for opportunities
- **Verification System**: Comprehensive user and document verification
- **Real-time Communication**: Integrated messaging between users
- **Rating & Reviews**: Build trust through transparent feedback

### 🎨 **Modern Design**
- **Dark Theme**: Professional dark UI with glassmorphism effects
- **Responsive Design**: Mobile-first approach with Bootstrap 5.1.3
- **Inter Font**: Clean, modern typography
- **Smooth Animations**: Hover effects and smooth transitions
- **Accessible**: WCAG 2.1 compliant design

### 🔒 **Security & Trust**
- **User Verification**: ID verification for all users
- **Secure Payments**: Integrated payment processing (planned)
- **Data Protection**: GDPR compliant with comprehensive privacy controls
- **Admin Dashboard**: Complete platform management tools

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 4.2+
- Node.js (for frontend assets)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/event-portal.git
cd event-portal
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database**
```bash
python manage.py migrate
python manage.py collectstatic
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see the application!

## 📱 Screenshots

<div align="center">

### Homepage
![Homepage](https://via.placeholder.com/800x400/0a0a0a/ffffff?text=Modern+Dark+Homepage)

### Opportunities
![Opportunities](https://via.placeholder.com/800x400/141414/ffffff?text=Job+Opportunities+Page)

### Dashboard
![Dashboard](https://via.placeholder.com/800x400/1a1a1a/ffffff?text=User+Dashboard)

</div>

## 🏗️ Project Structure

```
event_portal/
├── 📁 accounts/           # User management & authentication
│   ├── models.py         # Custom User model with roles
│   ├── views.py          # Registration, login, profile
│   └── forms.py          # User forms and validation
├── 📁 core/              # Core functionality
│   ├── views.py          # Home, about, how it works
│   └── templates/        # Core page templates
├── 📁 jobs/              # Job/Event management
│   ├── models.py         # Job, Application, Review models
│   ├── views.py          # CRUD operations for jobs
│   └── filters.py        # Advanced filtering system
├── 📁 templates/         # HTML templates
│   ├── base.html         # Base template with modern navbar
│   ├── core/             # Core page templates
│   ├── accounts/         # Authentication templates
│   └── jobs/             # Job-related templates
├── 📁 static/            # Static assets
│   ├── css/              # Custom stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Images and icons
└── 📁 event_portal/      # Django project settings
    ├── settings.py       # Configuration
    ├── urls.py           # URL routing
    └── wsgi.py           # WSGI configuration
```

## 👥 User Roles

### 🙋‍♀️ **Volunteers**
- Browse and apply for event opportunities
- Build comprehensive profiles with skills
- Receive ratings and build reputation
- Track application history

### 👨‍💼 **Event Managers**
- Post event opportunities
- Manage applications and select volunteers
- Rate and review volunteers
- Access analytics dashboard

### 🛡️ **Administrators**
- Platform management and oversight
- User verification and moderation
- System analytics and reporting
- Content management

## 🛠️ Tech Stack

<div align="center">

| Category | Technologies |
|----------|-------------|
| **Backend** | ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) |
| **Frontend** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) |
| **Design** | ![Inter](https://img.shields.io/badge/Inter%20Font-000000?style=flat&logoColor=white) ![Font Awesome](https://img.shields.io/badge/Font%20Awesome-528DD7?style=flat&logo=fontawesome&logoColor=white) |
| **Tools** | ![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white) ![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=flat&logo=visualstudiocode&logoColor=white) |

</div>

## 🎨 Design System

### Color Palette
```css
:root {
    --primary-dark: #0a0a0a;     /* Main background */
    --secondary-dark: #1a1a1a;   /* Section backgrounds */
    --accent-blue: #0066ff;      /* Primary actions */
    --accent-green: #00ff88;     /* Success states */
    --text-light: #ffffff;       /* Primary text */
    --text-gray: #a0a0a0;        /* Secondary text */
    --card-dark: #141414;        /* Card backgrounds */
    --border-subtle: rgba(255, 255, 255, 0.1); /* Borders */
}
```

### Typography
- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700, 800
- **Modern Design**: Clean, readable, professional

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Community** for the amazing framework
- **Bootstrap Team** for the responsive framework
- **Font Awesome** for the beautiful icons
- **Inter Font** for the modern typography

## 📞 Support

- 📧 Email: support@eventportal.com
- 💬 Discord: [Join our community](#)
- 📖 Documentation: [docs.eventportal.com](#)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/event-portal/issues)

---

<div align="center">

**Made with ❤️ by the EventPortal Team**

⭐ **Star this repo if you find it helpful!** ⭐

</div>
# Force redeploy
