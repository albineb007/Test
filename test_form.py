#!/usr/bin/env python
"""
Quick test script to validate the new job posting form
"""
import os
import sys
import django

# Add the project directory to Python path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_portal.settings')
django.setup()

from jobs.forms import JobCreateForm
from jobs.models import Job

def test_form():
    """Test the new JobCreateForm"""
    print("Testing JobCreateForm...")
    
    # Test form creation
    form = JobCreateForm()
    print(f"✓ Form created successfully")
    print(f"✓ Form fields: {list(form.fields.keys())}")
    
    # Test with sample data
    test_data = {
        'title': 'Event Staff Needed',
        'description': 'Looking for reliable event staff',
        'location_input': 'Mumbai, Maharashtra',
        'venue_name': 'Event Hall',
        'event_date': '2024-12-25',
        'duration_days': 1,
        'volunteers_needed': 5,
        'pay_amount': 500,
        'pay_type': 'per_day',
        'benefits': 'Free meals',
        'dress_code': 'Formal',
        'requirements_checkboxes': ['be_15_minutes_early', 'proper_haircut'],
        'contact_preference': ['whatsapp', 'call']
    }
    
    form = JobCreateForm(data=test_data)
    if form.is_valid():
        print("✓ Form validation passed")
        print(f"✓ Auto-detected category: {form.cleaned_data.get('category', 'None detected')}")
    else:
        print("✗ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
    
    print("\nForm test completed!")

if __name__ == '__main__':
    test_form()
