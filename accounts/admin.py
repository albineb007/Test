from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, Skill, UserProfile, VerificationRequest


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_phone_verified', 'is_profile_verified', 'date_joined')
    list_filter = ('role', 'is_phone_verified', 'is_profile_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Verification', {
            'fields': ('role', 'is_phone_verified', 'is_profile_verified')
        }),
        ('Profile Information', {
            'fields': ('phone_number', 'profile_picture', 'bio', 'location', 'date_of_birth')
        }),
        ('Worker Information', {
            'fields': ('skills', 'availability_status')
        }),
        ('Verification Documents', {
            'fields': ('government_id', 'id_number')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'email')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    ordering = ('category', 'name')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'trust_score', 'jobs_completed', 'jobs_posted', 'total_earnings')
    list_filter = ('rating', 'trust_score')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('jobs_completed', 'jobs_posted', 'total_earnings', 'rating', 'total_ratings')


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_type', 'status', 'submitted_at', 'reviewed_by')
    list_filter = ('verification_type', 'status', 'submitted_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-submitted_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'reviewed_by')
    
    actions = ['approve_verification', 'reject_verification']
    
    def approve_verification(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} verification requests approved.')
    approve_verification.short_description = "Approve selected verification requests"
    
    def reject_verification(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} verification requests rejected.')
    reject_verification.short_description = "Reject selected verification requests"
