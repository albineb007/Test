from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Fieldset
from crispy_forms.bootstrap import Field
from .models import Job, JobApplication, JobCategory, JobReview, ReviewReport

User = get_user_model()


class JobCreateForm(forms.ModelForm):
    """Super simple form matching WhatsApp group format"""
    
    # Simple location input
    location_input = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address or paste Google Maps link'
        })
    )
    
    # Number of days for multi-day events
    number_of_days = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 2',
            'min': 1,
            'max': 30
        })
    )
    
    # Pay type dropdown
    PAY_TYPE_CHOICES = [
        ('per_day', 'Per Day'),
        ('per_hour', 'Per Hour'),
        ('total', 'Total'),
    ]
    
    pay_type = forms.ChoiceField(
        choices=PAY_TYPE_CHOICES,
        initial='per_day',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Start date for multi-day events
    event_start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    # Reporting time as simple text
    reporting_time = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 10:00 AM to 8:00 PM'
        })
    )
    
    # Contact person name
    contact_person = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Manju'
        })
    )
    
    # WhatsApp only preference (default checked)
    whatsapp_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput()
    )
    
    # Simple requirements as checkboxes
    REQUIREMENT_CHOICES = [
        ('be_early', 'Be 15 minutes early'),
        ('grooming', 'Grooming is Mandatory'),
        ('gps_photos', 'GPS Login/Logout photos required'),
        ('follow_rules', 'Follow all rules & regulations'),
        ('payment_deduction', 'Payment deduction for rule violations'),
    ]
    
    requirements = forms.MultipleChoiceField(
        choices=REQUIREMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    # Additional notes
    additional_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Any additional requirements or notes...'
        }),
        required=False
    )

    class Meta:
        model = Job
        fields = [
            'title', 'description', 'required_workers', 'pay_rate', 
            'event_date', 'event_end_date', 'venue_name', 'dress_code', 
            'whatsapp_number'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Wedding Reception, Mall Activity'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g. Mall activity, Event assistance'
            }),
            'required_workers': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 02',
                'min': 1
            }),
            'pay_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 800',
                'min': 0
            }),
            'event_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'event_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'venue_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Shoba Mall, Hotel Taj'
            }),
            'dress_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Blue jeans and sports shoes'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 9742845679'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Handle multi-day events
        number_of_days = cleaned_data.get('number_of_days')
        event_start_date = cleaned_data.get('event_start_date')
        event_end_date = cleaned_data.get('event_end_date')
        event_date = cleaned_data.get('event_date')
        
        if number_of_days and number_of_days > 1:
            # Multi-day event - use start and end dates
            if not event_start_date:
                self.add_error('event_start_date', 'Start date is required for multi-day events')
            if not event_end_date:
                self.add_error('event_end_date', 'End date is required for multi-day events')
            
            # Set the main event_date to start_date
            if event_start_date:
                cleaned_data['event_date'] = event_start_date
            if event_end_date:
                cleaned_data['event_end_date'] = event_end_date
        else:
            # Single day event - clear end date
            if not event_date:
                self.add_error('event_date', 'Event date is required')
            cleaned_data['event_end_date'] = None
        
        # Auto-categorize based on title/description
        title = cleaned_data.get('title', '').lower()
        description = cleaned_data.get('description', '').lower()
        
        category_keywords = {
            'wedding': ['wedding', 'marriage', 'bride', 'groom'],
            'corporate': ['corporate', 'conference', 'meeting'],
            'mall': ['mall', 'shopping', 'retail'],
            'party': ['party', 'birthday', 'celebration'],
            'exhibition': ['exhibition', 'expo', 'fair'],
        }
        
        detected_category = 'general'
        text_to_check = f"{title} {description}"
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_to_check for keyword in keywords):
                detected_category = category
                break
        
        # Get or create category
        from .models import JobCategory
        category, created = JobCategory.objects.get_or_create(
            name=detected_category.title(),
            defaults={'description': f'Auto-categorized {detected_category} events'}
        )
        cleaned_data['category'] = category
        
        # Process location
        location_input = cleaned_data.get('location_input', '')
        if location_input:
            if 'maps.google.com' in location_input or 'goo.gl' in location_input:
                cleaned_data['google_maps_url'] = location_input
                cleaned_data['location'] = 'Google Maps Location'
            else:
                cleaned_data['location'] = location_input
        
        # Process requirements
        requirements_list = []
        selected_requirements = cleaned_data.get('requirements', [])
        requirement_mapping = dict(self.REQUIREMENT_CHOICES)
        
        for req_key in selected_requirements:
            if req_key in requirement_mapping:
                requirements_list.append(f"• {requirement_mapping[req_key]}")
        
        # Add additional notes if provided
        additional_notes = cleaned_data.get('additional_notes', '')
        if additional_notes:
            requirements_list.append(f"• {additional_notes}")
        
        if requirements_list:
            cleaned_data['requirements'] = '\n'.join(requirements_list)
        
        # Set WhatsApp preferences
        cleaned_data['enable_whatsapp'] = True
        cleaned_data['enable_call'] = not cleaned_data.get('whatsapp_only', True)
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set processed data
        if hasattr(self, 'cleaned_data'):
            cd = self.cleaned_data
            
            if 'category' in cd:
                instance.category = cd['category']
            if 'location' in cd:
                instance.location = cd['location']
            if 'google_maps_url' in cd:
                instance.google_maps_url = cd['google_maps_url']
            if 'requirements' in cd:
                instance.requirements = cd['requirements']
            if 'pay_type' in cd:
                instance.pay_type = cd['pay_type']
            if 'enable_whatsapp' in cd:
                instance.enable_whatsapp = cd['enable_whatsapp']
            if 'enable_call' in cd:
                instance.enable_call = cd['enable_call']
        
        if commit:
            instance.save()
        return instance


class JobUpdateForm(JobCreateForm):
    """Form for updating existing jobs"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change submit button text
        self.helper.layout[-1] = Submit('submit', 'Update Job', css_class='btn btn-primary btn-lg')


class JobApplicationForm(forms.ModelForm):
    """Form for job applications"""
    
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'availability_confirmed', 'expected_rate', 'relevant_experience', 'additional_skills']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us why you are interested in this job...'}),
            'relevant_experience': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe any relevant experience...'}),
            'additional_skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional skills or qualifications...'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'cover_letter',
            Row(
                Column('availability_confirmed', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            'expected_rate',
            'relevant_experience',
            'additional_skills',
            Submit('submit', 'Submit Application', css_class='btn btn-success btn-lg')
        )
        
        # Set placeholders and help text
        if self.job:
            self.fields['expected_rate'].help_text = f"Job offers: ₹{self.job.pay_rate} {self.job.get_pay_type_display()}"
        
        for field_name, field in self.fields.items():
            if field_name != 'availability_confirmed':
                field.widget.attrs['class'] = 'form-control'


class JobSearchForm(forms.Form):
    """Form for searching and filtering jobs"""
    
    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('event_date', 'Event Date (Earliest)'),
        ('-event_date', 'Event Date (Latest)'),
        ('-pay_rate', 'Highest Pay'),
        ('pay_rate', 'Lowest Pay'),
    ]
    
    search = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search jobs by title, location, or description...',
            'class': 'form-control'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter location...',
            'class': 'form-control'
        })
    )
    
    min_pay = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min pay rate',
            'class': 'form-control'
        })
    )
    
    max_pay = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max pay rate',
            'class': 'form-control'
        })
    )
    
    pay_type = forms.ChoiceField(
        choices=[('', 'Any Pay Type')] + Job._meta.get_field('pay_type').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    experience_level = forms.ChoiceField(
        choices=[('', 'Any Experience')] + Job.EXPERIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    event_date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    event_date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        initial='-created_at',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    urgent_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-12 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('category', css_class='form-group col-md-4 mb-0'),
                Column('location', css_class='form-group col-md-4 mb-0'),
                Column('sort', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('min_pay', css_class='form-group col-md-3 mb-0'),
                Column('max_pay', css_class='form-group col-md-3 mb-0'),
                Column('pay_type', css_class='form-group col-md-3 mb-0'),
                Column('experience_level', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('event_date_from', css_class='form-group col-md-4 mb-0'),
                Column('event_date_to', css_class='form-group col-md-4 mb-0'),
                Column('urgent_only', css_class='form-group col-md-4 mb-0 d-flex align-items-end'),
                css_class='form-row'
            ),
            Submit('submit', 'Search Jobs', css_class='btn btn-primary')
        )


class AdvancedJobSearchForm(forms.Form):
    """Advanced search form with skills and location-based filtering"""
    
    EXPERIENCE_CHOICES = [
        ('', 'Any Experience'),
        ('entry', 'Entry Level'),
        ('intermediate', 'Intermediate'),
        ('experienced', 'Experienced'),
    ]
    
    PAY_TYPE_CHOICES = [
        ('', 'Any Pay Type'),
        ('hourly', 'Hourly'),
        ('fixed', 'Fixed'),
    ]
    
    SORT_CHOICES = [
        ('-created_at', 'Latest'),
        ('event_date', 'Event Date'),
        ('-pay_rate', 'Highest Pay'),
        ('pay_rate', 'Lowest Pay'),
        ('-is_urgent', 'Urgent First'),
    ]
    
    # Basic search
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search jobs by title, description...',
            'class': 'form-control'
        })
    )
    
    # Location with radius
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'City, State',
            'class': 'form-control'
        })
    )
    
    distance = forms.ChoiceField(
        choices=[
            ('', 'Any Distance'),
            ('5', 'Within 5 km'),
            ('10', 'Within 10 km'),
            ('25', 'Within 25 km'),
            ('50', 'Within 50 km'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Category and skills
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.all(),
        empty_label="All Categories",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Pay range
    min_pay = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min Pay',
            'class': 'form-control'
        })
    )
    
    max_pay = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max Pay',
            'class': 'form-control'
        })
    )
    
    pay_type = forms.ChoiceField(
        choices=PAY_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Experience and other filters
    experience_level = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Date range
    event_date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    event_date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    # Additional filters
    urgent_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    available_only = forms.BooleanField(
        required=False,
        label="Positions available",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        initial='-created_at',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'advanced-search-form'
        self.helper.layout = Layout(
            HTML('<div class="search-section">'),
            Row(
                Column('search', css_class='form-group col-md-12 mb-3'),
                css_class='form-row'
            ),
            HTML('</div>'),
            
            HTML('<div class="filter-section">'),
            Row(
                Column('category', css_class='form-group col-md-6 mb-0'),
                Column('sort', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h6 class="mt-3 mb-2">Location</h6>'),
            Row(
                Column('location', css_class='form-group col-md-8 mb-0'),
                Column('distance', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h6 class="mt-3 mb-2">Pay Range</h6>'),
            Row(
                Column('min_pay', css_class='form-group col-md-4 mb-0'),
                Column('max_pay', css_class='form-group col-md-4 mb-0'),
                Column('pay_type', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h6 class="mt-3 mb-2">Experience & Date</h6>'),
            Row(
                Column('experience_level', css_class='form-group col-md-4 mb-0'),
                Column('event_date_from', css_class='form-group col-md-4 mb-0'),
                Column('event_date_to', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<h6 class="mt-3 mb-2">Additional Filters</h6>'),
            Row(
                Column(
                    HTML('<div class="form-check">'
                         '<input type="checkbox" class="form-check-input" id="id_urgent_only" name="urgent_only">'
                         '<label class="form-check-label" for="id_urgent_only">Urgent jobs only</label>'
                         '</div>'),
                    css_class='form-group col-md-6 mb-0'
                ),
                Column(
                    HTML('<div class="form-check">'
                         '<input type="checkbox" class="form-check-input" id="id_available_only" name="available_only">'
                         '<label class="form-check-label" for="id_available_only">Positions available</label>'
                         '</div>'),
                    css_class='form-group col-md-6 mb-0'
                ),
                css_class='form-row'
            ),
            HTML('</div>'),
            
            HTML('<div class="search-actions mt-4">'),
            Row(
                Column(
                    Submit('submit', 'Search Jobs', css_class='btn btn-primary me-2'),
                    HTML('<a href="?" class="btn btn-outline-secondary">Clear Filters</a>'),
                    css_class='form-group col-md-12 text-center'
                ),
                css_class='form-row'
            ),
            HTML('</div>'),
        )


class JobReviewForm(forms.ModelForm):
    """Form for submitting job reviews"""
    class Meta:
        model = JobReview
        fields = [
            'review_type', 'rating', 'title', 'comment',
            'punctuality', 'quality', 'communication', 'professionalism',
            'job_accuracy', 'payment_timeliness', 'work_environment',
            'skill_level', 'reliability', 'would_recommend', 'would_work_again'
        ]
        widgets = {
            'review_type': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)], 
                                 attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your detailed experience...'
            }),
            'punctuality': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)], 
                                      attrs={'class': 'form-select form-select-sm'}),
            'quality': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)], 
                                  attrs={'class': 'form-select form-select-sm'}),
            'communication': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)], 
                                        attrs={'class': 'form-select form-select-sm'}),
            'professionalism': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)], 
                                          attrs={'class': 'form-select form-select-sm'}),
            'job_accuracy': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)], 
                                       attrs={'class': 'form-select form-select-sm'}),
            'payment_timeliness': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)], 
                                             attrs={'class': 'form-select form-select-sm'}),
            'work_environment': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)], 
                                           attrs={'class': 'form-select form-select-sm'}),
            'skill_level': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)], 
                                      attrs={'class': 'form-select form-select-sm'}),
            'reliability': forms.Select(choices=[(i, f'{i}') for i in range(1, 6)], 
                                      attrs={'class': 'form-select form-select-sm'}),
            'would_recommend': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'would_work_again': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.reviewer = kwargs.pop('reviewer', None)
        self.reviewee = kwargs.pop('reviewee', None)
        self.job = kwargs.pop('job', None)
        super().__init__(*args, **kwargs)
        
        # Set review type based on reviewer role
        if self.reviewer and self.job:
            if self.reviewer == self.job.poster:
                self.fields['review_type'].initial = 'volunteer_review'
                self.fields['review_type'].widget = forms.HiddenInput()
            else:
                self.fields['review_type'].initial = 'poster_review'
                self.fields['review_type'].widget = forms.HiddenInput()
        
        # Setup crispy forms
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('rating', css_class='form-group col-md-6 mb-0'),
                Column('title', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'comment',
            Fieldset(
                'Detailed Ratings',
                Row(
                    Column('punctuality', css_class='form-group col-md-3 mb-0'),
                    Column('quality', css_class='form-group col-md-3 mb-0'),
                    Column('communication', css_class='form-group col-md-3 mb-0'),
                    Column('professionalism', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('job_accuracy', css_class='form-group col-md-3 mb-0'),
                    Column('payment_timeliness', css_class='form-group col-md-3 mb-0'),
                    Column('work_environment', css_class='form-group col-md-3 mb-0'),
                    Column('skill_level', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('reliability', css_class='form-group col-md-6 mb-0'),
                    Column('would_recommend', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Submit('submit', 'Submit Review', css_class='btn btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure all rating fields are provided
        rating_fields = [
            'punctuality', 'quality', 'communication', 'professionalism',
            'job_accuracy', 'payment_timeliness', 'work_environment',
            'skill_level', 'reliability'
        ]
        
        for field in rating_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'This rating is required.')
        
        return cleaned_data


class QuickReviewForm(forms.ModelForm):
    """Simplified form for quick reviews"""
    class Meta:
        model = JobReview
        fields = ['rating', 'comment', 'would_recommend', 'would_work_again']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)], 
                                 attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your experience...'
            }),
            'would_recommend': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'would_work_again': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'rating',
            'comment',
            'would_recommend',
            'would_work_again',
            Submit('submit', 'Submit Quick Review', css_class='btn btn-success')
        )


class ReviewReportForm(forms.ModelForm):
    """Form for reporting inappropriate reviews"""
    class Meta:
        model = ReviewReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please provide details about why you are reporting this review...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = True
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'reason',
            'description',
            Submit('submit', 'Report Review', css_class='btn btn-warning')
        )
