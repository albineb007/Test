from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from .models import User, UserProfile, VerificationRequest
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, DocumentVerificationForm

# Import dashboard views from jobs app
from jobs.views import volunteer_dashboard, poster_dashboard


class CustomLoginView(LoginView):
    """Custom login view"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        if self.request.user.is_admin_user:
            return reverse_lazy('admin:index')
        else:
            return reverse_lazy('accounts:volunteer_dashboard')


class RegisterView(CreateView):
    """User registration view"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login.')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ProfileView(DetailView):
    """User profile view"""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['user_profile'], created = UserProfile.objects.get_or_create(user=user)
        context['verification_requests'] = VerificationRequest.objects.filter(user=user)
        return context


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    """Update user profile"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


@login_required
def document_verification(request):
    """Document verification view"""
    if request.method == 'POST':
        form = DocumentVerificationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            
            # Create verification request
            VerificationRequest.objects.create(
                user=request.user,
                verification_type='document'
            )
            
            messages.success(request, 'Documents submitted for verification!')
            return redirect('accounts:profile')
    else:
        form = DocumentVerificationForm(instance=request.user)
    
    return render(request, 'accounts/document_verification.html', {'form': form})


@login_required
def phone_verification(request):
    """Phone verification view (placeholder for OTP implementation)"""
    if request.method == 'POST':
        # In a real implementation, you would:
        # 1. Generate and send OTP
        # 2. Verify OTP
        # 3. Mark phone as verified
        
        # For now, we'll just mark as verified (REMOVE IN PRODUCTION)
        request.user.is_phone_verified = True
        request.user.save()
        
        messages.success(request, 'Phone number verified successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/phone_verification.html')


def role_selection(request):
    """Role selection for new users"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    # Only show volunteer and manager roles for registration
    available_roles = [
        ('volunteer', 'Volunteer'),
        ('manager', 'Manpower/Event Manager'),
    ]
    
    return render(request, 'accounts/role_selection.html', {
        'roles': available_roles
    })


@login_required
def dashboard(request):
    """Dashboard redirect - all users go to volunteer dashboard since all are volunteers"""
    return redirect('accounts:volunteer_dashboard')


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = reverse_lazy('core:home')
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)
