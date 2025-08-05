from django.core.management.base import BaseCommand
from accounts.models import Skill


class Command(BaseCommand):
    help = 'Create initial skills data'

    def handle(self, *args, **options):
        skills_data = [
            # Event Management
            {'name': 'Event Coordination', 'category': 'Event Management', 'description': 'Planning and coordinating event activities'},
            {'name': 'Crowd Management', 'category': 'Event Management', 'description': 'Managing large groups of people at events'},
            {'name': 'Setup & Breakdown', 'category': 'Event Management', 'description': 'Setting up and dismantling event equipment'},
            
            # Catering
            {'name': 'Food Service', 'category': 'Catering', 'description': 'Serving food and beverages to guests'},
            {'name': 'Kitchen Helper', 'category': 'Catering', 'description': 'Assisting in food preparation and kitchen tasks'},
            {'name': 'Bartending', 'category': 'Catering', 'description': 'Preparing and serving alcoholic and non-alcoholic beverages'},
            
            # Hospitality
            {'name': 'Guest Relations', 'category': 'Hospitality', 'description': 'Interacting with and assisting event guests'},
            {'name': 'Reception & Registration', 'category': 'Hospitality', 'description': 'Managing guest check-in and registration'},
            {'name': 'Hostess Services', 'category': 'Hospitality', 'description': 'Providing professional hosting services'},
            
            # Technical
            {'name': 'Audio/Visual Setup', 'category': 'Technical', 'description': 'Setting up sound and visual equipment'},
            {'name': 'Photography', 'category': 'Technical', 'description': 'Event photography and documentation'},
            {'name': 'Live Streaming', 'category': 'Technical', 'description': 'Managing live broadcast of events'},
            
            # Security & Safety
            {'name': 'Event Security', 'category': 'Security', 'description': 'Providing security services at events'},
            {'name': 'First Aid', 'category': 'Safety', 'description': 'Basic first aid and medical assistance'},
            
            # Administrative
            {'name': 'Data Entry', 'category': 'Administrative', 'description': 'Recording and managing event data'},
            {'name': 'Customer Service', 'category': 'Administrative', 'description': 'Providing excellent customer support'},
            
            # Specialized
            {'name': 'Decoration', 'category': 'Creative', 'description': 'Event decoration and styling'},
            {'name': 'Translation', 'category': 'Language', 'description': 'Language translation services'},
            {'name': 'Entertainment', 'category': 'Performance', 'description': 'Providing entertainment services'},
            {'name': 'Sales & Promotion', 'category': 'Marketing', 'description': 'Product promotion and sales at events'},
        ]

        created_count = 0
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults={
                    'category': skill_data['category'],
                    'description': skill_data['description']
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} skills')
        )
