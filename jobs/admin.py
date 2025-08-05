from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import JobCategory, Job, JobApplication, JobReview, SavedJob


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'job_count')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def job_count(self, obj):
        return obj.jobs.count()
    job_count.short_description = 'Total Jobs'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'poster', 'category', 'location', 'event_date', 'status', 'pay_rate', 'applications_count', 'created_at')
    list_filter = ('status', 'category', 'experience_level', 'pay_type', 'is_urgent', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'location', 'poster__username', 'poster__first_name', 'poster__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'published_at', 'total_budget_calculated')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'poster', 'status')
        }),
        ('Location & Timing', {
            'fields': ('location', 'address', 'latitude', 'longitude', 'event_date', 'start_time', 'end_time', 'duration_hours')
        }),
        ('Requirements', {
            'fields': ('required_workers', 'required_skills', 'experience_level', 'min_age', 'requirements', 'dress_code')
        }),
        ('Payment', {
            'fields': ('pay_rate', 'pay_type', 'total_budget', 'total_budget_calculated')
        }),
        ('Additional Information', {
            'fields': ('benefits', 'contact_person', 'contact_phone', 'application_deadline')
        }),
        ('Metadata', {
            'fields': ('is_urgent', 'is_featured', 'created_at', 'updated_at', 'published_at')
        }),
    )
    
    filter_horizontal = ('required_skills',)
    
    def applications_count(self, obj):
        count = obj.applications.count()
        if count > 0:
            url = reverse('admin:jobs_jobapplication_changelist') + f'?job__id__exact={obj.id}'
            return format_html('<a href="{}">{} applications</a>', url, count)
        return '0 applications'
    applications_count.short_description = 'Applications'
    
    def total_budget_calculated(self, obj):
        return f"₹{obj.calculate_total_budget():,.2f}"
    total_budget_calculated.short_description = 'Calculated Budget'
    
    actions = ['mark_as_published', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_published(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} jobs marked as published.')
    mark_as_published.short_description = "Mark selected jobs as published"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} jobs marked as completed.')
    mark_as_completed.short_description = "Mark selected jobs as completed"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} jobs marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected jobs as cancelled"


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'worker_name', 'status', 'applied_at', 'reviewed_at')
    list_filter = ('status', 'applied_at', 'job__category')
    search_fields = ('job__title', 'volunteer__username', 'volunteer__first_name', 'volunteer__last_name')
    ordering = ('-applied_at',)
    readonly_fields = ('applied_at', 'reviewed_at')
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'volunteer', 'status', 'applied_at', 'reviewed_at')
        }),
        ('Application Details', {
            'fields': ('cover_letter', 'availability_confirmed', 'expected_rate')
        }),
        ('Experience', {
            'fields': ('relevant_experience', 'additional_skills')
        }),
    )
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'
    
    def worker_name(self, obj):
        return obj.volunteer.get_full_name() or obj.volunteer.username
    worker_name.short_description = 'Volunteer'
    
    actions = ['accept_applications', 'reject_applications']
    
    def accept_applications(self, request, queryset):
        updated = queryset.update(status='accepted', reviewed_at=timezone.now())
        self.message_user(request, f'{updated} applications accepted.')
    accept_applications.short_description = "Accept selected applications"
    
    def reject_applications(self, request, queryset):
        updated = queryset.update(status='rejected', reviewed_at=timezone.now())
        self.message_user(request, f'{updated} applications rejected.')
    reject_applications.short_description = "Reject selected applications"


@admin.register(JobReview)
class JobReviewAdmin(admin.ModelAdmin):
    list_display = ('job', 'reviewer', 'reviewee', 'rating', 'would_recommend', 'created_at')
    list_filter = ('rating', 'would_recommend', 'created_at')
    search_fields = ('job__title', 'reviewer__username', 'reviewee__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'job__title')
    ordering = ('-saved_at',)
