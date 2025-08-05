from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_application_notification(application, action):
    """Send email notification for application status changes"""
    
    if not application.volunteer.email:
        return False
    
    try:
        subject_map = {
            'accepted': f'Application Accepted - {application.job.title}',
            'rejected': f'Application Update - {application.job.title}',
            'under_review': f'Application Under Review - {application.job.title}'
        }
        
        template_map = {
            'accepted': 'emails/application_accepted.html',
            'rejected': 'emails/application_rejected.html', 
            'under_review': 'emails/application_under_review.html'
        }
        
        if action not in subject_map:
            return False
            
        subject = subject_map[action]
        template_name = template_map[action]
        
        # Render email content
        html_message = render_to_string(template_name, {
            'application': application,
            'job': application.job,
            'volunteer': application.volunteer,
            'poster': application.job.poster,
        })
        
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@eventportal.com'),
            recipient_list=[application.volunteer.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        return True
        
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_new_application_notification(application):
    """Notify job poster about new application"""
    
    if not application.job.poster.email:
        return False
        
    try:
        subject = f'New Application Received - {application.job.title}'
        
        html_message = render_to_string('emails/new_application_notification.html', {
            'application': application,
            'job': application.job,
            'volunteer': application.volunteer,
            'poster': application.job.poster,
        })
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@eventportal.com'),
            recipient_list=[application.job.poster.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        return True
        
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
