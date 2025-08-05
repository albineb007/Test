from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from jobs.models import Job, JobApplication


def home(request):
    """Home page view with smart recommendations"""
    # Calculate impressive statistics
    today = timezone.now().date()
    
    context = {}
    
    # Show statistics only to admins
    if request.user.is_authenticated and request.user.is_admin_user:
        context.update({
            'total_jobs': Job.objects.filter(status='published').count(),
            'total_volunteers': User.objects.filter(role='volunteer').count(),
            'total_applications': JobApplication.objects.count(),
            'successful_placements': JobApplication.objects.filter(status='accepted').count(),
            'show_stats': True
        })
    
    # Smart job recommendations
    if request.user.is_authenticated:
        # Get personalized recommendations for logged-in users
        featured_jobs = request.user.get_recommended_jobs(limit=8)
        context['user_role'] = request.user.role
        
        # Personalized data for logged-in volunteers
        if request.user.role == 'volunteer':
            context.update({
                'my_applications': JobApplication.objects.filter(
                    volunteer=request.user
                ).count(),
                'pending_applications': JobApplication.objects.filter(
                    volunteer=request.user,
                    status='pending'
                ).count(),
                'my_jobs': Job.objects.filter(poster=request.user).count(),
                'my_posted_applications': JobApplication.objects.filter(
                    job__poster=request.user
                ).count()
            })
        
        # Auto-detect skills for user if they don't have any
        if not request.user.skills.exists():
            request.user.auto_detect_skills()
            
    else:
        # For anonymous users, show latest jobs from different categories
        featured_jobs = Job.objects.filter(
            status='published',
            event_date__gte=today
        ).select_related('category', 'poster').order_by('-created_at')
        
        # Get diverse jobs from different categories
        categories = list(Job.objects.filter(
            status='published',
            event_date__gte=today
        ).values_list('category', flat=True).distinct())
        
        diverse_jobs = []
        for category_id in categories[:6]:  # Limit to 6 categories
            category_jobs = featured_jobs.filter(category_id=category_id)[:2]
            diverse_jobs.extend(category_jobs)
        
        featured_jobs = diverse_jobs[:8] if diverse_jobs else featured_jobs[:8]
    
    context.update({
        'featured_jobs': featured_jobs,
        'urgent_jobs': Job.objects.filter(
            status='published',
            is_urgent=True,
            event_date__gte=today
        ).count(),
        'jobs_this_week': Job.objects.filter(
            status='published',
            event_date__range=[today, today + timedelta(days=7)]
        ).count(),
        'popular_categories': Job.objects.filter(
            status='published'
        ).values(
            'category__name'
        ).annotate(
            job_count=Count('id')
        ).order_by('-job_count')[:6]
    })
    
    return render(request, 'core/home_linkedin.html', context)


def about(request):
    """About page view"""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page view"""
    return render(request, 'core/contact.html')


def how_it_works(request):
    """How it works page"""
    return render(request, 'core/how_it_works.html')


def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'core/privacy_policy.html')


def terms_of_service(request):
    """Terms of service page"""
    return render(request, 'core/terms_of_service.html')
