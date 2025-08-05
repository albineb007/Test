import random
import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import Skill, UserProfile
from jobs.models import Job, JobCategory, JobApplication

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with fake data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of users to create'
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=15,
            help='Number of jobs to create'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting to populate database with fake data...')
        )

        # Create fake users
        self.create_fake_users(options['users'])
        
        # Create fake jobs
        self.create_fake_jobs(options['jobs'])
        
        # Create fake applications
        self.create_fake_applications()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with fake data!')
        )

    def create_fake_users(self, count):
        """Create fake volunteers - all users are volunteers now"""
        
        # Sample data
        volunteer_names = [
            ('Arjun', 'Sharma'), ('Priya', 'Patel'), ('Rahul', 'Kumar'), 
            ('Sneha', 'Singh'), ('Vikram', 'Gupta'), ('Anita', 'Verma'),
            ('Rohit', 'Agarwal'), ('Kavya', 'Reddy'), ('Amit', 'Joshi'),
            ('Pooja', 'Nair'), ('Siddharth', 'Mehta'), ('Riya', 'Shah'),
            ('Karan', 'Malhotra'), ('Neha', 'Chopra'), ('Varun', 'Kapoor'),
            ('Deepika', 'Management'), ('Ashok', 'Solutions'), ('Meera', 'Events'),
            ('Suresh', 'Productions'), ('Nisha', 'Organizers'), ('Rajesh', 'Kumar'),
            ('Sunita', 'Gupta'), ('Manoj', 'Singh'), ('Kavitha', 'Reddy'),
            ('Anil', 'Verma')
        ]
        
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata', 'Ahmedabad']
        
        # Create volunteers only
        for i in range(count):
            if i < len(volunteer_names):
                first_name, last_name = volunteer_names[i]
            else:
                first_name, last_name = f"Volunteer{i}", f"User{i}"
            
            username = f"{first_name.lower()}{last_name.lower()}{i}"
            email = f"{username}@example.com"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='testpass123',
                first_name=first_name,
                last_name=last_name,
                role='volunteer',
                phone_number=f"+91{random.randint(7000000000, 9999999999)}",
                location=random.choice(cities),
                is_phone_verified=True,
                is_profile_verified=random.choice([True, False])
            )
            
            # Add skills to volunteers
            all_skills = list(Skill.objects.all())
            if all_skills:
                user_skills = random.sample(all_skills, random.randint(2, 5))
                user.skills.set(user_skills)
            
            self.stdout.write(f'Created volunteer: {username}')

    def create_fake_jobs(self, count):
        """Create fake job postings"""
        
        # Get all volunteers (since all can post jobs now)
        volunteers = User.objects.filter(role='volunteer')
        if not volunteers:
            self.stdout.write(self.style.WARNING('No volunteers found. Skipping job creation.'))
            return
        
        # Sample job data
        job_titles = [
            "Event Registration Assistant", "Sound System Operator", "Stage Decorator",
            "Crowd Management Volunteer", "Photography Assistant", "Catering Helper",
            "Security Guard", "Usher/Guide", "Technical Support", "Setup Crew Member",
            "Cleanup Volunteer", "Ticket Counter Staff", "Audio Visual Technician",
            "Event Coordinator Assistant", "Hospitality Volunteer", "Merchandise Seller",
            "Parking Assistant", "First Aid Volunteer", "Translation Helper",
            "Social Media Live Coverage", "Equipment Handler", "Guest Reception"
        ]
        
        descriptions = [
            "Help manage event registration and check-in process. Friendly attitude required.",
            "Operate sound equipment during the event. Basic audio knowledge preferred.",
            "Assist in decorating the stage and venue. Creative skills appreciated.",
            "Help manage crowds and ensure smooth flow of attendees.",
            "Assist photographer with equipment and crowd management.",
            "Help serve food and manage catering operations during the event.",
            "Provide security services for the event premises.",
            "Guide attendees and provide information about the event.",
            "Provide technical support for event equipment and systems.",
            "Help with event setup including stage, seating, and equipment.",
            "Assist in post-event cleanup and equipment breakdown.",
            "Handle ticket sales and verification at entry points.",
            "Manage audio visual equipment and presentations.",
            "Support event coordinator with various organizational tasks.",
            "Welcome guests and provide hospitality services.",
            "Sell event merchandise and manage inventory.",
            "Direct vehicles and manage parking arrangements.",
            "Provide basic first aid support during the event.",
            "Help with language translation for international guests.",
            "Cover event on social media platforms with live updates.",
            "Handle and transport heavy equipment safely.",
            "Welcome VIP guests and manage reception area."
        ]
        
        locations = [
            "Mumbai, Maharashtra", "Delhi, NCR", "Bangalore, Karnataka", 
            "Chennai, Tamil Nadu", "Hyderabad, Telangana", "Pune, Maharashtra",
            "Kolkata, West Bengal", "Ahmedabad, Gujarat", "Jaipur, Rajasthan",
            "Lucknow, Uttar Pradesh", "Bhopal, Madhya Pradesh", "Kochi, Kerala"
        ]
        
        categories = list(JobCategory.objects.all())
        
        for i in range(count):
            title = random.choice(job_titles)
            
            # Generate random future dates
            start_date = timezone.now().date() + datetime.timedelta(days=random.randint(1, 60))
            
            job = Job.objects.create(
                title=title,
                description=random.choice(descriptions),
                category=random.choice(categories),
                poster=random.choice(volunteers),
                location=random.choice(locations),
                address=f"Event Venue Address {i+1}, {random.choice(locations)}",
                event_date=start_date,
                start_time=datetime.time(random.randint(8, 14), random.choice([0, 30])),
                end_time=datetime.time(random.randint(15, 22), random.choice([0, 30])),
                duration_hours=random.randint(4, 12),
                required_workers=random.randint(1, 8),
                experience_level=random.choice(['entry', 'intermediate', 'experienced']),
                min_age=random.choice([18, 21, 25]),
                pay_rate=Decimal(str(random.randint(200, 1500))),
                pay_type=random.choice(['hourly', 'fixed']),
                requirements=f"Requirements for {title}: Good communication skills, punctuality, team player.",
                benefits="Food provided, certificate of participation, networking opportunity.",
                dress_code=random.choice(['Casual', 'Formal', 'Uniform Provided', 'Smart Casual']),
                contact_person=f"{random.choice(['Mr.', 'Ms.'])} {random.choice(['Sharma', 'Patel', 'Kumar', 'Singh'])}",
                contact_phone=f"+91{random.randint(7000000000, 9999999999)}",
                status='published',
                is_urgent=random.choice([True, False]),
                application_deadline=timezone.now() + datetime.timedelta(days=random.randint(1, 30))
            )
            
            # Add random skills to jobs
            all_skills = list(Skill.objects.all())
            if all_skills:
                job_skills = random.sample(all_skills, random.randint(1, 3))
                job.required_skills.set(job_skills)
            
            self.stdout.write(f'Created job: {title}')

    def create_fake_applications(self):
        """Create fake job applications"""
        
        volunteers = User.objects.filter(role='volunteer')
        jobs = Job.objects.filter(status='published')
        
        if not volunteers or not jobs:
            self.stdout.write(self.style.WARNING('No volunteers or jobs found. Skipping applications.'))
            return
        
        cover_letters = [
            "I am very interested in this opportunity and believe my skills would be valuable for this event.",
            "Looking forward to contributing to this event and gaining experience in the field.",
            "I have relevant experience in similar events and would love to be part of your team.",
            "This seems like a great opportunity to volunteer and make a positive impact.",
            "I am available for the entire duration and excited to participate in this event."
        ]
        
        # Create random applications
        for _ in range(min(len(volunteers) * 2, len(jobs) * 3)):
            volunteer = random.choice(volunteers)
            job = random.choice(jobs)
            
            # Check if application already exists
            if not JobApplication.objects.filter(volunteer=volunteer, job=job).exists():
                application = JobApplication.objects.create(
                    job=job,
                    volunteer=volunteer,
                    cover_letter=random.choice(cover_letters),
                    availability_confirmed=True,
                    expected_rate=job.pay_rate + Decimal(str(random.randint(-100, 200))),
                    relevant_experience=f"I have {random.randint(0, 5)} years of experience in similar roles.",
                    status=random.choice(['pending', 'accepted', 'rejected']),
                    applied_at=timezone.now() - datetime.timedelta(days=random.randint(0, 20))
                )
                
                self.stdout.write(f'Created application: {volunteer.username} -> {job.title}')
