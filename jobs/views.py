from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from .models import Job, JobApplication, JobCategory, SavedJob, JobReview, ReviewHelpful, ReviewReport
from .forms import JobCreateForm, JobUpdateForm, JobApplicationForm, JobSearchForm, JobReviewForm, QuickReviewForm, ReviewReportForm
from .utils import send_application_notification, send_new_application_notification


class JobListView(ListView):
    """List all published jobs with search and filtering"""
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Job.objects.filter(status='published', event_date__gte=timezone.now().date())
        
        # Get search parameters
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        location = self.request.GET.get('location')
        min_pay = self.request.GET.get('min_pay')
        max_pay = self.request.GET.get('max_pay')
        pay_type = self.request.GET.get('pay_type')
        experience_level = self.request.GET.get('experience_level')
        event_date_from = self.request.GET.get('event_date_from')
        event_date_to = self.request.GET.get('event_date_to')
        urgent_only = self.request.GET.get('urgent_only')
        sort = self.request.GET.get('sort', '-created_at')
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        if min_pay:
            queryset = queryset.filter(pay_rate__gte=min_pay)
        
        if max_pay:
            queryset = queryset.filter(pay_rate__lte=max_pay)
        
        if pay_type:
            queryset = queryset.filter(pay_type=pay_type)
        
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        
        if event_date_from:
            queryset = queryset.filter(event_date__gte=event_date_from)
        
        if event_date_to:
            queryset = queryset.filter(event_date__lte=event_date_to)
        
        if urgent_only:
            queryset = queryset.filter(is_urgent=True)
        
        # Apply sorting
        if sort:
            queryset = queryset.order_by(sort)
        
        return queryset.select_related('category', 'poster').prefetch_related('required_skills')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm(self.request.GET)
        context['total_jobs'] = self.get_queryset().count()
        context['categories'] = JobCategory.objects.annotate(job_count=Count('jobs')).filter(job_count__gt=0)
        return context


def job_list(request):
    """Enhanced function-based view for job listing with advanced search"""
    from .forms import AdvancedJobSearchForm
    from django.db.models import Q
    
    # Get search form
    search_form = AdvancedJobSearchForm(request.GET)
    
    # Base queryset
    jobs = Job.objects.filter(status='published').select_related('category', 'poster').prefetch_related('required_skills')
    
    # Apply filters if form is valid
    if search_form.is_valid():
        data = search_form.cleaned_data
        
        # Text search
        if data.get('search'):
            search_query = data['search']
            jobs = jobs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(requirements__icontains=search_query)
            )
        
        # Location search with smart matching
        if data.get('location'):
            location = data['location']
            location_parts = location.lower().split(',')
            location_queries = Q()
            for part in location_parts:
                part = part.strip()
                if part:
                    location_queries |= Q(location__icontains=part)
            jobs = jobs.filter(location_queries)
        
        # Category filter
        if data.get('category'):
            jobs = jobs.filter(category=data['category'])
        
        # Pay range filters
        if data.get('min_pay'):
            jobs = jobs.filter(pay_rate__gte=data['min_pay'])

        if data.get('max_pay'):
            jobs = jobs.filter(pay_rate__lte=data['max_pay'])

        if data.get('pay_type'):
            jobs = jobs.filter(pay_type=data['pay_type'])
        
        # Handle quick filter pay ranges
        pay_range = request.GET.get('pay_range')
        if pay_range:
            if pay_range == '0-500':
                jobs = jobs.filter(pay_rate__gte=0, pay_rate__lte=500)
            elif pay_range == '500-1000':
                jobs = jobs.filter(pay_rate__gte=500, pay_rate__lte=1000)
            elif pay_range == '1000-2000':
                jobs = jobs.filter(pay_rate__gte=1000, pay_rate__lte=2000)
            elif pay_range == '2000+':
                jobs = jobs.filter(pay_rate__gte=2000)        # Experience level
        if data.get('experience_level'):
            jobs = jobs.filter(experience_level=data['experience_level'])
        
        # Date range
        if data.get('event_date_from'):
            jobs = jobs.filter(event_date__gte=data['event_date_from'])
        
        if data.get('event_date_to'):
            jobs = jobs.filter(event_date__lte=data['event_date_to'])
        
        # Additional filters
        if data.get('urgent_only'):
            jobs = jobs.filter(is_urgent=True)
        
        if data.get('available_only'):
            # Only show jobs with available positions
            jobs = jobs.extra(
                where=["required_workers > (SELECT COUNT(*) FROM jobs_jobapplication WHERE job_id = jobs_job.id AND status = 'accepted')"]
            )
    
    # Handle additional quick filters from navbar
    if request.GET.get('urgent_only'):
        jobs = jobs.filter(is_urgent=True)
    
    if request.GET.get('available_only'):
        jobs = jobs.extra(
            where=["required_workers > (SELECT COUNT(*) FROM jobs_jobapplication WHERE job_id = jobs_job.id AND status = 'accepted')"]
        )
    
    if request.GET.get('featured_only'):
        jobs = jobs.filter(is_featured=True)
        
        # Sorting
        sort_option = data.get('sort', '-created_at')
        # Handle empty sort option
        if not sort_option or sort_option.strip() == '':
            sort_option = '-created_at'
        jobs = jobs.order_by(sort_option)
    else:
        # Default sorting for non-filtered view
        jobs = jobs.order_by('-is_urgent', '-created_at')
    
    # Personalized recommendations for logged-in users
    recommended_jobs = []
    if request.user.is_authenticated:
        recommended_jobs = request.user.get_recommended_jobs(limit=3)
        # Exclude recommended jobs from main list to avoid duplicates
        recommended_job_ids = [job.id for job in recommended_jobs]
        jobs = jobs.exclude(id__in=recommended_job_ids)
    
    # Pagination
    paginator = Paginator(jobs, 12)  # Show 12 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique locations for filter dropdown
    unique_locations = Job.objects.filter(status='published').values_list('location', flat=True).distinct().order_by('location')
    
    # Get saved job IDs for current user
    saved_job_ids = []
    if request.user.is_authenticated and request.user.is_volunteer:
        saved_job_ids = list(request.user.saved_jobs.values_list('job_id', flat=True))
    
    context = {
        'jobs': page_obj,
        'search_form': search_form,
        'total_jobs': jobs.count(),
        'categories': JobCategory.objects.annotate(job_count=Count('jobs')).filter(job_count__gt=0),
        'recommended_jobs': recommended_jobs,
        'has_filters': any(request.GET.values()),
        'unique_locations': unique_locations,
        'saved_job_ids': saved_job_ids,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
    }
    
    return render(request, 'jobs/job_list_clean.html', context)


class JobDetailView(DetailView):
    """Detailed view of a job"""
    model = Job
    template_name = 'jobs/job_detail_final.html'
    context_object_name = 'job'
    
    def get_queryset(self):
        return Job.objects.select_related('category', 'poster').prefetch_related('required_skills', 'applications')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()
        
        # Increment view count
        job.increment_view_count()
        
        # Check if user has already applied
        if self.request.user.is_authenticated:
            context['has_applied'] = JobApplication.objects.filter(
                job=job, volunteer=self.request.user
            ).exists()
            
            context['is_saved'] = SavedJob.objects.filter(
                job=job, user=self.request.user
            ).exists()
            
            context['can_apply'] = (
                self.request.user.can_apply_for_jobs and 
                not context['has_applied'] and 
                job.remaining_positions > 0 and
                not job.is_expired
            )
        
        # Related jobs
        context['related_jobs'] = Job.objects.filter(
            category=job.category,
            status='published'
        ).exclude(pk=job.pk)[:3]
        
        return context


def job_detail(request, pk):
    """Function-based view for job detail (keeping for compatibility)"""
    view = JobDetailView.as_view()
    return view(request, pk=pk)


@require_http_methods(["POST"])
def track_contact_click(request, pk):
    """Track WhatsApp and call clicks for analytics"""
    import json
    
    try:
        job = get_object_or_404(Job, pk=pk, status='published')
        data = json.loads(request.body)
        contact_type = data.get('contact_type')
        
        if contact_type == 'whatsapp':
            job.increment_whatsapp_clicks()
        elif contact_type == 'call':
            job.increment_call_clicks()
        else:
            return JsonResponse({'success': False, 'error': 'Invalid contact type'})
        
        return JsonResponse({
            'success': True,
            'whatsapp_clicks': job.whatsapp_clicks,
            'call_clicks': job.call_clicks
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def toggle_save_job(request, pk):
    """Toggle save/unsave job for authenticated users"""
    try:
        job = get_object_or_404(Job, pk=pk, status='published')
        saved_job, created = SavedJob.objects.get_or_create(
            user=request.user,
            job=job
        )
        
        if not created:
            # Job was already saved, so unsave it
            saved_job.delete()
            saved = False
        else:
            # Job was just saved
            saved = True
        
        return JsonResponse({
            'success': True,
            'saved': saved,
            'message': 'Job saved successfully!' if saved else 'Job removed from saved jobs!'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


class JobCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new job posting"""
    model = Job
    form_class = JobCreateForm
    template_name = 'jobs/job_form_simple.html'
    
    def test_func(self):
        return self.request.user.can_post_jobs
    
    def form_valid(self, form):
        form.instance.poster = self.request.user
        messages.success(self.request, 'Job posted successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('jobs:job_detail', kwargs={'pk': self.object.pk})


def job_create(request):
    """Function-based view for job creation (keeping for compatibility)"""
    view = JobCreateView.as_view()
    return view(request)


class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing job"""
    model = Job
    form_class = JobUpdateForm
    template_name = 'jobs/job_form.html'
    
    def test_func(self):
        job = self.get_object()
        return job.poster == self.request.user or self.request.user.is_admin_user
    
    def form_valid(self, form):
        messages.success(self.request, 'Job updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('jobs:job_detail', kwargs={'pk': self.object.pk})


def job_update(request, pk):
    """Function-based view for job update (keeping for compatibility)"""
    view = JobUpdateView.as_view()
    return view(request, pk=pk)


class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a job"""
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('jobs:job_list')
    
    def test_func(self):
        job = self.get_object()
        return job.poster == self.request.user or self.request.user.is_admin_user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Job deleted successfully!')
        return super().delete(request, *args, **kwargs)


def job_delete(request, pk):
    """Function-based view for job deletion (keeping for compatibility)"""
    view = JobDeleteView.as_view()
    return view(request, pk=pk)


@login_required
def job_apply(request, pk):
    """Apply for a job"""
    job = get_object_or_404(Job, pk=pk, status='published')
    
    # Check if user can apply
    if not request.user.can_apply_for_jobs:
        messages.error(request, 'Only volunteers can apply for jobs.')
        return redirect('jobs:job_detail', pk=pk)
    
    if JobApplication.objects.filter(job=job, volunteer=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', pk=pk)
    
    if job.remaining_positions <= 0:
        messages.error(request, 'This job has no remaining positions.')
        return redirect('jobs:job_detail', pk=pk)
    
    if job.is_expired:
        messages.error(request, 'The application deadline for this job has passed.')
        return redirect('jobs:job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, job=job)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.volunteer = request.user
            application.save()
            
            # Send notification to job poster
            send_new_application_notification(application)
            
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('jobs:job_detail', pk=pk)
    else:
        form = JobApplicationForm(job=job)
    
    return render(request, 'jobs/job_apply_new.html', {
        'job': job,
        'form': form
    })


@login_required
def my_applications(request):
    """View user's job applications"""
    if not request.user.can_apply_for_jobs:
        messages.error(request, 'This page is only for volunteers.')
        return redirect('core:home')
    
    applications = JobApplication.objects.filter(volunteer=request.user).select_related('job', 'job__category').order_by('-applied_at')
    
    # Calculate stats
    total_applications = applications.count()
    pending_count = applications.filter(status='pending').count()
    accepted_count = applications.filter(status='accepted').count()
    rejected_count = applications.filter(status='rejected').count()
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/my_applications.html', {
        'applications': page_obj,
        'total_applications': total_applications,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
    })


@login_required
def volunteer_dashboard(request):
    """Dashboard for volunteers"""
    if not request.user.can_apply_for_jobs:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    # Get user statistics
    applications = JobApplication.objects.filter(volunteer=request.user)
    context = {
        'total_applications': applications.count(),
        'pending_applications': applications.filter(status='pending').count(),
        'accepted_applications': applications.filter(status='accepted').count(),
        'recent_applications': applications.select_related('job')[:5],
        'suggested_jobs': Job.objects.filter(
            status='published',
            event_date__gte=timezone.now().date(),
            required_skills__in=request.user.skills.all()
        ).distinct()[:6],
        'saved_jobs': SavedJob.objects.filter(user=request.user).select_related('job')[:5]
    }
    
    return render(request, 'accounts/volunteer_dashboard.html', context)


@login_required
def poster_dashboard(request):
    """Dashboard for managers and admins"""
    if not request.user.can_post_jobs:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    # Get poster statistics
    jobs = Job.objects.filter(poster=request.user)
    context = {
        'total_jobs': jobs.count(),
        'published_jobs': jobs.filter(status='published').count(),
        'draft_jobs': jobs.filter(status='draft').count(),
        'completed_jobs': jobs.filter(status='completed').count(),
        'recent_jobs': jobs.order_by('-created_at')[:5],
        'total_applications': JobApplication.objects.filter(job__poster=request.user).count(),
        'pending_applications': JobApplication.objects.filter(
            job__poster=request.user, status='pending'
        ).count(),
    }
    
    return render(request, 'accounts/poster_dashboard.html', context)


@login_required
def save_job(request, pk):
    """Save/unsave a job"""
    if request.method == 'POST':
        job = get_object_or_404(Job, pk=pk)
        saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        
        if created:
            return JsonResponse({'saved': True, 'message': 'Job saved successfully!'})
        else:
            saved_job.delete()
            return JsonResponse({'saved': False, 'message': 'Job removed from saved list!'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def job_applications_manage(request, pk):
    """Manage applications for a job (for posters)"""
    job = get_object_or_404(Job, pk=pk)
    
    # Check permissions
    if job.poster != request.user and not request.user.is_admin_user:
        messages.error(request, 'You do not have permission to manage this job.')
        return redirect('jobs:job_detail', pk=pk)
    
    applications = job.applications.select_related('volunteer').order_by('-applied_at')
    
    return render(request, 'jobs/manage_applications.html', {
        'job': job,
        'applications': applications
    })


@login_required
def application_action(request, pk, action):
    """Accept, reject, or update application status"""
    application = get_object_or_404(JobApplication, pk=pk)
    job = application.job
    
    # Check permissions
    if job.poster != request.user and not request.user.is_admin_user:
        messages.error(request, 'You do not have permission to manage this application.')
        return redirect('jobs:job_detail', pk=job.pk)
    
    if action == 'accept':
        application.status = 'accepted'
        application.reviewed_at = timezone.now()
        application.save()
        messages.success(request, f'Application from {application.volunteer.get_full_name()} has been accepted.')
        
        # Send email notification to applicant
        send_application_notification(application, 'accepted')
        
    elif action == 'reject':
        application.status = 'rejected'
        application.reviewed_at = timezone.now()
        application.save()
        messages.success(request, f'Application from {application.volunteer.get_full_name()} has been rejected.')
        
        # Send email notification to applicant
        send_application_notification(application, 'rejected')
        
    elif action == 'review':
        application.status = 'under_review'
        application.reviewed_at = timezone.now()
        application.save()
        messages.success(request, f'Application from {application.volunteer.get_full_name()} is now under review.')
        
        # Send email notification to applicant
        send_application_notification(application, 'under_review')
    
    return redirect('jobs:manage_applications', pk=job.pk)


@login_required
def bulk_application_action(request, pk):
    """Bulk action on multiple applications"""
    job = get_object_or_404(Job, pk=pk)
    
    # Check permissions
    if job.poster != request.user and not request.user.is_admin_user:
        messages.error(request, 'You do not have permission to manage this job.')
        return redirect('jobs:job_detail', pk=pk)
    
    if request.method == 'POST':
        selected_apps = request.POST.getlist('selected_applications')
        action = request.POST.get('bulk_action')
        
        if selected_apps and action:
            applications = JobApplication.objects.filter(
                id__in=selected_apps, 
                job=job
            )
            
            if action == 'accept':
                applications.update(status='accepted', reviewed_at=timezone.now())
                messages.success(request, f'{len(selected_apps)} applications accepted.')
            elif action == 'reject':
                applications.update(status='rejected', reviewed_at=timezone.now())
                messages.success(request, f'{len(selected_apps)} applications rejected.')
            elif action == 'review':
                applications.update(status='under_review', reviewed_at=timezone.now())
                messages.success(request, f'{len(selected_apps)} applications moved to under review.')
    
    return redirect('jobs:manage_applications', pk=job.pk)


@login_required
def leave_review(request, job_id, user_id):
    """Leave a review for a user after working together on a job"""
    job = get_object_or_404(Job, id=job_id)
    reviewee = get_object_or_404(Job._meta.get_field('poster').remote_field.model, id=user_id)
    
    # Check if user can leave review
    can_review, message = request.user.can_leave_review_for(reviewee, job)
    if not can_review:
        messages.error(request, message)
        return redirect('jobs:job_detail', pk=job.pk)
    
    if request.method == 'POST':
        form = JobReviewForm(request.POST, reviewer=request.user, reviewee=reviewee, job=job)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewee = reviewee
            review.job = job
            review.save()
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobReviewForm(reviewer=request.user, reviewee=reviewee, job=job)
    
    context = {
        'form': form,
        'job': job,
        'reviewee': reviewee,
    }
    return render(request, 'jobs/leave_review.html', context)


@login_required
def quick_review(request, job_id, user_id):
    """Submit a quick review"""
    job = get_object_or_404(Job, id=job_id)
    reviewee = get_object_or_404(Job._meta.get_field('poster').remote_field.model, id=user_id)
    
    # Check if user can leave review
    can_review, message = request.user.can_leave_review_for(reviewee, job)
    if not can_review:
        messages.error(request, message)
        return redirect('jobs:job_detail', pk=job.pk)
    
    if request.method == 'POST':
        form = QuickReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewee = reviewee
            review.job = job
            review.title = f"Review for {reviewee.get_full_name() or reviewee.username}"
            
            # Set review type
            if request.user == job.poster:
                review.review_type = 'volunteer_review'
            else:
                review.review_type = 'poster_review'
            
            # Set default detailed ratings based on overall rating
            default_rating = review.rating
            review.punctuality = default_rating
            review.quality = default_rating
            review.communication = default_rating
            review.professionalism = default_rating
            review.job_accuracy = default_rating
            review.payment_timeliness = default_rating
            review.work_environment = default_rating
            review.skill_level = default_rating
            review.reliability = default_rating
            
            review.save()
            
            messages.success(request, 'Quick review submitted successfully!')
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = QuickReviewForm()
    
    context = {
        'form': form,
        'job': job,
        'reviewee': reviewee,
        'is_quick_review': True,
    }
    return render(request, 'jobs/leave_review.html', context)


class ReviewListView(ListView):
    """List reviews for a user"""
    model = JobReview
    template_name = 'jobs/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return JobReview.objects.filter(reviewee_id=user_id).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        context['reviewee'] = get_object_or_404(Job._meta.get_field('poster').remote_field.model, id=user_id)
        
        # Get review statistics
        reviews = self.get_queryset()
        context['avg_rating'] = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        context['total_reviews'] = reviews.count()
        context['rating_distribution'] = {
            i: reviews.filter(rating=i).count() for i in range(1, 6)
        }
        
        return context


class ReviewDetailView(DetailView):
    """Detailed view of a single review"""
    model = JobReview
    template_name = 'jobs/review_detail.html'
    context_object_name = 'review'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = self.get_object()
        
        # Check if current user has marked this review as helpful
        if self.request.user.is_authenticated:
            context['user_marked_helpful'] = ReviewHelpful.objects.filter(
                review=review, user=self.request.user
            ).exists()
        
        return context


@login_required
@require_http_methods(["POST"])
def mark_review_helpful(request, review_id):
    """Mark a review as helpful or remove helpful mark"""
    review = get_object_or_404(JobReview, id=review_id)
    
    helpful, created = ReviewHelpful.objects.get_or_create(
        review=review, user=request.user
    )
    
    if not created:
        # User already marked as helpful, so remove it
        helpful.delete()
        action = 'removed'
    else:
        action = 'added'
    
    # Update helpful count
    review.helpful_count = review.helpful_votes.count()
    review.save()
    
    return JsonResponse({
        'success': True,
        'action': action,
        'helpful_count': review.helpful_count
    })


@login_required
def report_review(request, review_id):
    """Report a review as inappropriate"""
    review = get_object_or_404(JobReview, id=review_id)
    
    # Check if user already reported this review
    existing_report = ReviewReport.objects.filter(
        review=review, reported_by=request.user
    ).first()
    
    if existing_report:
        messages.warning(request, 'You have already reported this review.')
        return redirect('jobs:review_detail', pk=review.pk)
    
    if request.method == 'POST':
        form = ReviewReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.review = review
            report.reported_by = request.user
            report.save()
            
            messages.success(request, 'Review reported successfully. Our team will review it.')
            return redirect('jobs:review_detail', pk=review.pk)
    else:
        form = ReviewReportForm()
    
    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'jobs/report_review.html', context)


@login_required
def user_reviews(request, user_id):
    """View all reviews for a specific user"""
    user = get_object_or_404(Job._meta.get_field('poster').remote_field.model, id=user_id)
    
    reviews = JobReview.objects.filter(reviewee=user).order_by('-created_at')
    
    # Filter by review type if specified
    review_type = request.GET.get('type')
    if review_type in ['volunteer_review', 'poster_review']:
        reviews = reviews.filter(review_type=review_type)
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    reviews_page = paginator.get_page(page_number)
    
    # Statistics
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = reviews.count()
    positive_reviews = reviews.filter(rating__gte=4).count()
    positive_percentage = (positive_reviews / total_reviews * 100) if total_reviews > 0 else 0
    
    # Rating distribution
    rating_distribution = {
        i: reviews.filter(rating=i).count() for i in range(1, 6)
    }
    
    # Featured reviews
    featured_reviews = reviews.filter(is_featured=True)[:3]
    
    context = {
        'reviewee': user,
        'reviews': reviews_page,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'positive_percentage': round(positive_percentage, 1),
        'rating_distribution': rating_distribution,
        'featured_reviews': featured_reviews,
        'review_type_filter': review_type,
    }
    
    return render(request, 'jobs/user_reviews.html', context)
