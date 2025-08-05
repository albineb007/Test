from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class JobCategory(models.Model):
    """Categories for different types of jobs"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    
    class Meta:
        verbose_name_plural = "Job Categories"
    
    def __str__(self):
        return self.name


class Job(models.Model):
    """Main job posting model"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level'),
        ('intermediate', 'Intermediate'),
        ('experienced', 'Experienced'),
        ('expert', 'Expert'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='jobs')
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    
    # Location & Timing
    location = models.CharField(max_length=200)
    venue_name = models.CharField(max_length=200, blank=True, help_text="Hotel/venue name")
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_maps_url = models.URLField(blank=True, help_text="Google Maps location URL")
    
    # Event Details
    event_date = models.DateField()
    event_end_date = models.DateField(null=True, blank=True, help_text="For multi-day events")
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.PositiveIntegerField(help_text="Expected duration in hours")
    event_duration_days = models.PositiveIntegerField(default=1, help_text="Number of days the event takes place")
    
    # Requirements
    required_workers = models.PositiveIntegerField(default=1)
    required_skills = models.ManyToManyField('accounts.Skill', blank=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='entry')
    min_age = models.PositiveIntegerField(default=18, validators=[MinValueValidator(16), MaxValueValidator(65)])
    
    # Payment
    pay_rate = models.DecimalField(max_digits=8, decimal_places=2)
    pay_type = models.CharField(max_length=20, choices=[
        ('hourly', 'Per Hour'),
        ('fixed', 'Fixed Amount'),
        ('daily', 'Per Day'),
    ], default='hourly')
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional Information
    requirements = models.TextField(blank=True, help_text="Additional requirements or instructions")
    benefits = models.TextField(blank=True, help_text="Benefits or perks offered")
    dress_code = models.CharField(max_length=200, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=17, blank=True)
    
    # Contact Options
    enable_whatsapp = models.BooleanField(default=True, help_text="Allow WhatsApp contact")
    enable_call = models.BooleanField(default=True, help_text="Allow phone calls")
    whatsapp_number = models.CharField(max_length=17, blank=True, help_text="WhatsApp number (can be different from contact phone)")
    
    # Analytics
    whatsapp_clicks = models.PositiveIntegerField(default=0)
    call_clicks = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Status & Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_urgent = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    application_deadline = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'event_date']),
            models.Index(fields=['location', 'event_date']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.location} - {self.event_date}"
    
    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'pk': self.pk})
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def is_expired(self):
        if self.application_deadline:
            return timezone.now() > self.application_deadline
        return self.event_date < timezone.now().date()
    
    @property
    def applications_count(self):
        return self.applications.count()
    
    @property
    def selected_workers_count(self):
        return self.applications.filter(status='accepted').count()
    
    @property
    def pending_applications_count(self):
        return self.applications.filter(status='pending').count()
    
    @property
    def remaining_positions(self):
        return max(0, self.required_workers - self.selected_workers_count)
    
    @property
    def fill_percentage(self):
        """Calculate percentage of positions filled"""
        if self.required_workers == 0:
            return 0
        return int((self.selected_workers_count / self.required_workers) * 100)
    
    @property
    def is_multi_day_event(self):
        """Check if event spans multiple days"""
        return self.event_duration_days > 1 or (self.event_end_date and self.event_end_date > self.event_date)
    
    @property
    def event_duration_display(self):
        """Display event duration in a user-friendly format"""
        if self.is_multi_day_event:
            if self.event_end_date:
                return f"{self.event_date.strftime('%b %d')} - {self.event_end_date.strftime('%b %d, %Y')}"
            else:
                return f"{self.event_duration_days} days starting {self.event_date.strftime('%b %d, %Y')}"
        else:
            return f"{self.event_date.strftime('%b %d, %Y')} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"
    
    @property
    def verification_status(self):
        """Get verification status of the poster"""
        return {
            'is_verified': self.poster.is_verified if hasattr(self.poster, 'is_verified') else False,
            'verification_type': getattr(self.poster, 'verification_type', 'None'),
            'verification_details': getattr(self.poster, 'verification_details', 'Not verified')
        }
    
    @property
    def google_maps_embed_url(self):
        """Generate Google Maps embed URL"""
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps/embed/v1/place?key=YOUR_API_KEY&q={self.latitude},{self.longitude}"
        elif self.google_maps_url:
            # Extract place info from Google Maps URL
            return self.google_maps_url.replace('google.com/maps', 'google.com/maps/embed/v1/place')
        return None
    
    def increment_view_count(self):
        """Increment view count for analytics"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_whatsapp_clicks(self):
        """Increment WhatsApp click count"""
        self.whatsapp_clicks += 1
        self.save(update_fields=['whatsapp_clicks'])
    
    def increment_call_clicks(self):
        """Increment call click count"""
        self.call_clicks += 1
        self.save(update_fields=['call_clicks'])
    
    def get_whatsapp_url(self, message=None):
        """Generate WhatsApp URL with pre-filled message"""
        phone = self.whatsapp_number or self.contact_phone
        if not phone:
            return None
        
        # Clean phone number (remove non-digits)
        phone = ''.join(filter(str.isdigit, phone))
        
        if not message:
            message = f"Hi! I'm interested in the {self.title} event on {self.event_date.strftime('%B %d, %Y')} at {self.location}. Pay: ₹{self.pay_rate}/{self.get_pay_type_display().lower()}. Please let me know if positions are still available."
        
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{phone}?text={encoded_message}"
    
    def calculate_total_budget(self):
        """Calculate total budget based on pay rate and requirements"""
        if self.pay_type == 'hourly':
            return self.pay_rate * self.duration_hours * self.required_workers
        elif self.pay_type == 'daily':
            return self.pay_rate * self.required_workers
        else:  # fixed
            return self.pay_rate
    
    def save(self, *args, **kwargs):
        # Auto-calculate total budget if not set
        if not self.total_budget:
            self.total_budget = self.calculate_total_budget()
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)


class JobApplication(models.Model):
    """Model for job applications"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='volunteer_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Application Details
    cover_letter = models.TextField(blank=True, help_text="Why are you interested in this job?")
    availability_confirmed = models.BooleanField(default=True)
    expected_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Experience & Skills
    relevant_experience = models.TextField(blank=True)
    additional_skills = models.TextField(blank=True)
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('job', 'volunteer')
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.volunteer.username} - {self.job.title} - {self.status}"


class JobReview(models.Model):
    """Reviews for completed jobs with comprehensive rating system"""
    
    REVIEW_TYPE_CHOICES = [
        ('volunteer_review', 'Review of Volunteer'),
        ('poster_review', 'Review of Job Poster'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE_CHOICES, default='volunteer_review')
    
    # Overall Rating (Required)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall rating from 1 to 5 stars"
    )
    
    # Review Content
    title = models.CharField(max_length=200, blank=True, help_text="Brief review title")
    comment = models.TextField(help_text="Detailed review comment")
    
    # Detailed Rating Categories (Optional but recommended)
    punctuality = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True,
        help_text="Timeliness and reliability"
    )
    quality = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True,
        help_text="Quality of work or job posting"
    )
    communication = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True,
        help_text="Communication skills and responsiveness"
    )
    professionalism = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True,
        help_text="Professional behavior and attitude"
    )
    
    # Additional Rating Categories for Different Review Types
    job_accuracy = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True,
        help_text="Accuracy of job description (for poster reviews)"
    )
    payment_timeliness = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True,
        help_text="Timeliness of payment (for poster reviews)"
    )
    work_environment = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True,
        help_text="Quality of work environment (for poster reviews)"
    )
    skill_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True,
        help_text="Skill level and competence (for volunteer reviews)"
    )
    reliability = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True,
        help_text="Reliability and dependability (for volunteer reviews)"
    )
    
    # Recommendation and Feedback
    would_recommend = models.BooleanField(default=True, help_text="Would you recommend this person?")
    would_work_again = models.BooleanField(default=True, help_text="Would you work with them again?")
    
    # Review Metadata
    is_verified = models.BooleanField(default=False, help_text="Verified by admin as legitimate")
    is_featured = models.BooleanField(default=False, help_text="Featured review")
    helpful_count = models.PositiveIntegerField(default=0, help_text="Number of users who found this helpful")
    
    # Response from reviewee
    response_comment = models.TextField(blank=True, help_text="Response from the reviewed person")
    response_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('job', 'reviewer', 'reviewee')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reviewee', 'rating']),
            models.Index(fields=['reviewer', 'created_at']),
            models.Index(fields=['job', 'review_type']),
        ]
    
    def __str__(self):
        return f"{self.reviewer.username} → {self.reviewee.username} ({self.rating}★) - {self.job.title}"
    
    @property
    def average_detailed_rating(self):
        """Calculate average of detailed ratings"""
        ratings = [
            self.punctuality, self.quality, self.communication, 
            self.professionalism, self.job_accuracy, self.payment_timeliness,
            self.work_environment, self.skill_level, self.reliability
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        return self.rating
    
    @property
    def star_display(self):
        """Return star display string"""
        return "★" * self.rating + "☆" * (5 - self.rating)
    
    def save(self, *args, **kwargs):
        # Auto-determine review type if not set
        if not self.review_type:
            if self.reviewee.role == 'volunteer':
                self.review_type = 'volunteer_review'
            else:
                self.review_type = 'poster_review'
        
        super().save(*args, **kwargs)


class ReviewHelpful(models.Model):
    """Track which users found reviews helpful"""
    review = models.ForeignKey(JobReview, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='helpful_reviews')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('review', 'user')
    
    def __str__(self):
        return f"{self.user.username} found review helpful"


class ReviewReport(models.Model):
    """Report inappropriate reviews"""
    
    REPORT_REASONS = [
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake Review'),
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('irrelevant', 'Irrelevant Content'),
        ('personal_info', 'Contains Personal Information'),
        ('other', 'Other'),
    ]
    
    review = models.ForeignKey(JobReview, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True, help_text="Additional details about the report")
    
    # Report Status
    is_resolved = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='resolved_reports'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('review', 'reporter')
    
    def __str__(self):
        return f"Report: {self.review} - {self.reason}"


class SavedJob(models.Model):
    """Model for users to save jobs for later"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'job')
    
    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
