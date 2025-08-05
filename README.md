# Event Portal 🎉

A Django-based web platform that connects students and individuals to verified part-time event jobs in event management, catering, volunteering, and hostess roles.

## 🎯 Goal

Create a trustworthy, easy-to-use job portal where users can discover, apply for, and get paid for event-based gigs — while organizers can post, track, and manage job postings and workers.

## 👥 User Roles

- **Worker** (Student/Helper/Volunteer): Find and apply for event jobs
- **Job Poster** (Organizer/Manager): Post jobs and find qualified workers
- **Admin** (Verification & Support): Manage platform and verify users

## 🔑 Current Features (MVP)

✅ **User Authentication System**
- Custom user model with role-based permissions
- Registration and login with role selection
- Profile management and verification system

✅ **User Interface**
- Responsive Bootstrap 5 design
- Role-based navigation and dashboards
- Mobile-friendly interface

✅ **Verification System**
- Phone number verification (placeholder)
- Document verification for trust building
- Admin approval workflow

✅ **Skills Management**
- 20+ predefined skills across categories
- Worker skill selection and management
- Skill-based filtering (future implementation)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Django 4.2+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd event-portal
   ```

2. **Install dependencies**
   ```bash
   pip install django djangorestframework django-cors-headers python-decouple pillow django-crispy-forms crispy-bootstrap4
   ```

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create initial data**
   ```bash
   python manage.py create_initial_skills
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
event_portal/
├── accounts/                 # User management and authentication
│   ├── models.py            # Custom User, UserProfile, Skills
│   ├── forms.py             # Registration, login, profile forms
│   ├── views.py             # Authentication views
│   ├── admin.py             # Admin customization
│   └── management/          # Custom management commands
├── core/                    # Base app for shared functionality
│   ├── views.py             # Home page and utility views
│   └── urls.py              # Core URL patterns
├── jobs/                    # Job management (placeholder)
│   ├── views.py             # Job-related views (placeholders)
│   └── urls.py              # Job URL patterns
├── templates/               # HTML templates
│   ├── base.html            # Base template with navigation
│   ├── accounts/            # Authentication templates
│   └── core/                # Core page templates
├── static/                  # Static files (CSS, JS, images)
│   ├── css/style.css        # Custom styles
│   └── js/main.js           # Custom JavaScript
├── media/                   # User-uploaded files
├── event_portal/            # Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
└── manage.py                # Django management script
```

## 🔧 Configuration

### Environment Variables (Future)
Create a `.env` file for production settings:
```
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://...
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

### Key Settings
- Custom User Model: `accounts.User`
- Time Zone: Asia/Kolkata
- Static Files: Bootstrap 5 + Custom CSS/JS
- Media Files: Profile pictures and documents

## 👨‍💻 Development Status

### ✅ Completed (Phase 1)
- Django project setup and configuration
- Custom User model with roles (Worker, Poster, Admin)
- User authentication system (register, login, logout)
- Profile management and update functionality
- Document verification system
- Admin panel customization
- Responsive UI with Bootstrap 5
- Initial skills data (20+ skills across categories)
- Base templates and navigation

### 🚧 In Progress
- Job posting system
- Job application workflow
- Dashboard for workers and posters

### 📋 Next Steps (Phase 2)
- Job model and management
- Advanced filtering and search
- Application tracking system
- Rating and review system
- Email notifications
- Enhanced verification

## 🎨 Design System

### Colors
- Primary: #007bff (Bootstrap Blue)
- Success: #28a745 (Green)
- Info: #17a2b8 (Cyan)
- Warning: #ffc107 (Yellow)
- Danger: #dc3545 (Red)

### Components
- Bootstrap 5 framework
- Font Awesome icons
- Custom CSS animations
- Responsive design for mobile/tablet/desktop

## 🔒 Security Features

- Django's built-in CSRF protection
- User input validation and sanitization
- File upload security for profile pictures/documents
- Role-based access control
- Secure password handling

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team

## 🚀 Deployment

### Development
```bash
python manage.py runserver
```

### Production (Basic)
1. Set `DEBUG = False`
2. Configure proper database (PostgreSQL)
3. Set up static file serving
4. Configure email settings
5. Set up SSL certificate
6. Use a proper WSGI server (Gunicorn)

## 📈 Future Roadmap

- **Phase 2**: Job posting and application system
- **Phase 3**: Payment integration with UPI
- **Phase 4**: Mobile app development
- **Phase 5**: WhatsApp integration and automation
- **Phase 6**: Advanced analytics and reporting

---

Built with ❤️ using Django and Bootstrap
