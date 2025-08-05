from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Custom User model with role-based system"""
    
    ROLE_CHOICES = [
        ('volunteer', 'Volunteer'),
        ('admin', 'Admin'),
    ]
    
    # Basic Information
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='volunteer')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Verification Status
    is_phone_verified = models.BooleanField(default=False)
    is_profile_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False, help_text="Overall verification status")
    verification_type = models.CharField(max_length=50, blank=True, choices=[
        ('government_id', 'Government ID'),
        ('business_license', 'Business License'),
        ('email_verified', 'Email Verified'),
        ('phone_verified', 'Phone Verified'),
        ('manual_review', 'Manual Review'),
    ])
    verification_details = models.TextField(blank=True, help_text="Details about verification")
    
    # Profile Information
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Additional fields for workers
    skills = models.ManyToManyField('Skill', blank=True)
    availability_status = models.BooleanField(default=True)
    
    # Verification Documents
    government_id = models.ImageField(upload_to='documents/', blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_user'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_volunteer(self):
        return self.role == 'volunteer'
    
    @property
    def is_admin_user(self):
        return self.role in ['admin'] or self.is_superuser
    
    @property
    def can_post_jobs(self):
        """All volunteers and admins can post jobs (including legacy roles)"""
        return self.role in ['volunteer', 'admin', 'worker', 'poster', 'manager']
    
    @property
    def can_apply_for_jobs(self):
        """All volunteers and admins can apply for jobs (including legacy roles)"""
        return self.role in ['volunteer', 'admin', 'worker', 'poster', 'manager']
    
    @property
    def can_manage_users(self):
        """Only Admins can manage other users"""
        return self.role == 'admin'
    
    def auto_detect_skills(self):
        """Auto-detect skills based on application history and job experience"""
        from jobs.models import JobApplication, Job
        
        # Get all accepted applications
        accepted_apps = JobApplication.objects.filter(
            volunteer=self, 
            status='accepted'
        ).select_related('job')
        
        # Get all jobs posted by this user
        posted_jobs = Job.objects.filter(poster=self)
        
        detected_skills = set()
        
        # Extract skills from job titles and descriptions
        skill_keywords = {
            'photography': ['photo', 'camera', 'shoot', 'photographer'],
            'event_management': ['manage', 'organize', 'coordinate', 'planning'],
            'customer_service': ['customer', 'service', 'reception', 'front desk'],
            'technical_support': ['technical', 'tech', 'computer', 'it', 'sound'],
            'sales': ['sales', 'sell', 'marketing', 'promotion'],
            'security': ['security', 'guard', 'safety'],
            'catering': ['food', 'catering', 'kitchen', 'serve'],
            'decoration': ['decor', 'decoration', 'design', 'setup'],
            'transportation': ['driver', 'transport', 'delivery'],
            'communication': ['presenter', 'mc', 'anchor', 'speaking']
        }
        
        # Analyze job applications
        for app in accepted_apps:
            job_text = f"{app.job.title} {app.job.description} {app.relevant_experience or ''}".lower()
            for skill_name, keywords in skill_keywords.items():
                if any(keyword in job_text for keyword in keywords):
                    detected_skills.add(skill_name)
        
        # Analyze posted jobs
        for job in posted_jobs:
            job_text = f"{job.title} {job.description}".lower()
            for skill_name, keywords in skill_keywords.items():
                if any(keyword in job_text for keyword in keywords):
                    detected_skills.add(skill_name)
        
        # Create or get skill objects and add to user
        for skill_name in detected_skills:
            skill, created = Skill.objects.get_or_create(
                name=skill_name.replace('_', ' ').title(),
                defaults={'description': f'Auto-detected from user activity'}
            )
            self.skills.add(skill)
    
    def get_recommended_jobs(self, limit=6):
        """Get recommended jobs based on user profile"""
        from jobs.models import Job
        from django.utils import timezone
        
        recommended_jobs = Job.objects.filter(
            status='published',
            event_date__gte=timezone.now().date()
        ).select_related('category', 'poster')
        
        # Filter by user skills if they have any
        if self.skills.exists():
            recommended_jobs = recommended_jobs.filter(
                required_skills__in=self.skills.all()
            ).distinct()
        
        # Filter by location if user has location
        if self.location:
            user_location_parts = self.location.lower().split(',')
            location_queries = Q()
            for part in user_location_parts:
                part = part.strip()
                if part:
                    location_queries |= Q(location__icontains=part)
            
            recommended_jobs = recommended_jobs.filter(location_queries)
        
        # Order by relevance (urgent jobs first, then by date)
        return recommended_jobs.order_by('-is_urgent', '-created_at')[:limit]

    @property
    def average_rating(self):
        """Calculate user's average rating from reviews"""
        from jobs.models import JobReview
        reviews = JobReview.objects.filter(reviewee=self)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0.0
    
    @property
    def total_reviews_count(self):
        """Get total number of reviews received"""
        from jobs.models import JobReview
        return JobReview.objects.filter(reviewee=self).count()
    
    @property
    def reviews_given_count(self):
        """Get total number of reviews given"""
        from jobs.models import JobReview
        return JobReview.objects.filter(reviewer=self).count()
    
    @property
    def rating_distribution(self):
        """Get distribution of ratings (1-5 stars)"""
        from jobs.models import JobReview
        distribution = {}
        for i in range(1, 6):
            count = JobReview.objects.filter(reviewee=self, rating=i).count()
            distribution[i] = count
        return distribution
    
    @property
    def positive_review_percentage(self):
        """Get percentage of positive reviews (4-5 stars)"""
        from jobs.models import JobReview
        total = JobReview.objects.filter(reviewee=self).count()
        if total == 0:
            return 0
        positive = JobReview.objects.filter(reviewee=self, rating__gte=4).count()
        return round((positive / total) * 100, 1)
    
    @property
    def reputation_score(self):
        """Calculate reputation score based on various factors"""
        # Base score from average rating (0-50 points)
        rating_score = (self.average_rating / 5) * 50
        
        # Bonus for number of reviews (0-20 points)
        review_count_score = min(self.total_reviews_count * 2, 20)
        
        # Bonus for verification status (0-15 points)
        verification_score = 15 if self.is_verified else 0
        
        # Bonus for profile completeness (0-10 points)
        profile_score = self._calculate_profile_completeness() * 10
        
        # Bonus for activity (0-5 points)
        activity_score = min(self.jobs_completed * 0.5, 5)
        
        total_score = rating_score + review_count_score + verification_score + profile_score + activity_score
        return min(round(total_score), 100)  # Cap at 100
    
    @property
    def reputation_level(self):
        """Get reputation level based on score"""
        score = self.reputation_score
        if score >= 90:
            return {'level': 'Elite', 'color': 'warning', 'icon': 'fas fa-crown'}
        elif score >= 75:
            return {'level': 'Excellent', 'color': 'success', 'icon': 'fas fa-star'}
        elif score >= 60:
            return {'level': 'Good', 'color': 'info', 'icon': 'fas fa-thumbs-up'}
        elif score >= 40:
            return {'level': 'Fair', 'color': 'secondary', 'icon': 'fas fa-user'}
        else:
            return {'level': 'New', 'color': 'light', 'icon': 'fas fa-seedling'}
    
    def _calculate_profile_completeness(self):
        """Calculate profile completeness as a decimal (0-1)"""
        fields_to_check = [
            'first_name', 'last_name', 'bio', 'location', 
            'phone_number', 'profile_picture'
        ]
        completed_fields = sum(1 for field in fields_to_check if getattr(self, field))
        return completed_fields / len(fields_to_check)
    
    def can_leave_review_for(self, user, job):
        """Check if this user can leave a review for another user on a specific job"""
        from jobs.models import JobApplication, JobReview
        
        # Check if they worked together on this job
        if self == job.poster:
            # User is job poster, can review accepted volunteers
            worked_together = JobApplication.objects.filter(
                job=job, volunteer=user, status='accepted'
            ).exists()
        elif user == job.poster:
            # User is volunteer, can review job poster if they were accepted
            worked_together = JobApplication.objects.filter(
                job=job, volunteer=self, status='accepted'
            ).exists()
        else:
            worked_together = False
        
        if not worked_together:
            return False, "You haven't worked together on this job"
        
        # Check if job is completed
        if job.status != 'completed':
            return False, "Job must be completed before leaving reviews"
        
        # Check if review already exists
        existing_review = JobReview.objects.filter(
            job=job, reviewer=self, reviewee=user
        ).exists()
        
        if existing_review:
            return False, "You have already reviewed this person for this job"
        
        return True, "Can leave review"
    
    def get_recent_reviews(self, limit=5):
        """Get recent reviews received by this user"""
        from jobs.models import JobReview
        return JobReview.objects.filter(reviewee=self).order_by('-created_at')[:limit]
    
    def get_featured_reviews(self, limit=3):
        """Get featured/highlighted reviews"""
        from jobs.models import JobReview
        return JobReview.objects.filter(
            reviewee=self, 
            is_featured=True
        ).order_by('-created_at')[:limit]


class Skill(models.Model):
    """Skills that workers can have"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Rating and Trust Score
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    trust_score = models.PositiveIntegerField(default=0)
    
    # Statistics
    jobs_completed = models.PositiveIntegerField(default=0)
    jobs_posted = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Social Links
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class VerificationRequest(models.Model):
    """Model to track verification requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verification_type = models.CharField(max_length=20, choices=[
        ('phone', 'Phone Verification'),
        ('profile', 'Profile Verification'),
        ('document', 'Document Verification'),
    ])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_requests'
    )
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.verification_type} - {self.status}"
