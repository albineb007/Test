<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Event Portal - Django Project Instructions

## Project Overview
This is a Django-based web platform that connects students and individuals to verified part-time event jobs. The platform supports three user roles: Workers, Job Posters, and Admins.

## Architecture & Structure
- **Backend Framework**: Django 4.2+ with Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: Bootstrap 5 with custom CSS/JS
- **Authentication**: Custom User model with role-based permissions

## Key Apps & Components

### accounts/
- Custom User model with role-based system (worker, poster, admin)
- User authentication, registration, and profile management
- Verification system for users and documents
- Skills model for worker capabilities

### jobs/ (In Development)
- Job posting and management
- Application system
- Dashboard for workers and posters

### core/
- Base templates and static files
- Common utilities and shared components
- Home page and informational pages

## User Roles
1. **Worker**: Find and apply for event jobs
2. **Poster**: Post jobs and manage workers
3. **Admin**: Platform management and verification

## Development Guidelines
- Use Django's built-in features whenever possible
- Follow Django REST Framework patterns for APIs
- Implement proper user permissions and security
- Use Bootstrap components for consistent UI
- Add proper validation and error handling

## Key Features to Implement
- Job posting system with filters
- Application and selection workflow
- Payment integration (future)
- Rating and review system
- Mobile-responsive design
- WhatsApp integration (future)

## Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for complex functions
- Use Django's class-based views where appropriate
- Implement proper error handling and logging

## Security Considerations
- Validate all user inputs
- Use Django's CSRF protection
- Implement proper user permissions
- Secure file upload handling
- Regular security updates
