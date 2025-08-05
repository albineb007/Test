from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from crispy_forms.bootstrap import Field
from .models import User, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form for volunteers"""
    
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=17, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'username',
            'email',
            'phone_number',
            'password1',
            'password2',
            Submit('submit', 'Register', css_class='btn btn-primary btn-block')
        )
        
        # Update placeholders and help text
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.role = 'volunteer'  # All new users are volunteers
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with better styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            HTML('<div class="form-group form-check">'
                 '<input type="checkbox" class="form-check-input" id="remember_me" name="remember_me">'
                 '<label class="form-check-label" for="remember_me">Remember me</label>'
                 '</div>'),
            Submit('submit', 'Login', css_class='btn btn-primary btn-block')
        )
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class EnhancedUserProfileForm(forms.ModelForm):
    """Enhanced form for updating user profile with smart features"""
    
    # Add custom fields for better location handling
    city = forms.CharField(
        max_length=100, 
        required=False,
        help_text="Your city (used for job recommendations)"
    )
    state = forms.CharField(
        max_length=100, 
        required=False,
        help_text="Your state"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio', 
                 'date_of_birth', 'profile_picture', 'availability_status']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself, your experience, and interests...'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate city and state from location field
        if self.instance and self.instance.location:
            location_parts = self.instance.location.split(',')
            if len(location_parts) >= 1:
                self.fields['city'].initial = location_parts[0].strip()
            if len(location_parts) >= 2:
                self.fields['state'].initial = location_parts[1].strip()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'email',
            'phone_number',
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('state', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'date_of_birth',
            'bio',
            'profile_picture',
            Field('availability_status', template='custom_checkbox.html'),
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name not in ['availability_status']:
                field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Combine city and state into location field
        city = self.cleaned_data.get('city', '').strip()
        state = self.cleaned_data.get('state', '').strip()
        
        if city and state:
            user.location = f"{city}, {state}"
        elif city:
            user.location = city
        elif state:
            user.location = state
        
        if commit:
            user.save()
            # Auto-detect and update skills after saving
            user.auto_detect_skills()
        
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio', 'location', 
                 'date_of_birth', 'profile_picture', 'skills']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'skills': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('phone_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'bio',
            Row(
                Column('location', css_class='form-group col-md-6 mb-0'),
                Column('date_of_birth', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'profile_picture',
            'skills',
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )
        
        for field_name, field in self.fields.items():
            if field_name != 'skills':
                field.widget.attrs['class'] = 'form-control'


class DocumentVerificationForm(forms.ModelForm):
    """Form for document verification"""
    
    class Meta:
        model = User
        fields = ['government_id', 'id_number']
        widgets = {
            'government_id': forms.FileInput(attrs={'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'id_number',
            'government_id',
            HTML('<small class="form-text text-muted">Upload a clear photo of your government ID (Aadhaar, PAN, Driving License, etc.)</small>'),
            Submit('submit', 'Submit for Verification', css_class='btn btn-primary')
        )
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
