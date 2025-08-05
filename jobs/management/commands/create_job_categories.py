from django.core.management.base import BaseCommand
from jobs.models import JobCategory


class Command(BaseCommand):
    help = 'Create initial job categories'

    def handle(self, *args, **options):
        categories_data = [
            {
                'name': 'Event Management',
                'description': 'Event planning, coordination, and management roles',
                'icon': 'fas fa-calendar-alt'
            },
            {
                'name': 'Catering & Food Service',
                'description': 'Food service, kitchen assistance, and beverage service',
                'icon': 'fas fa-utensils'
            },
            {
                'name': 'Hospitality & Guest Services',
                'description': 'Guest relations, hostess services, and customer service',
                'icon': 'fas fa-concierge-bell'
            },
            {
                'name': 'Technical & AV',
                'description': 'Audio/visual setup, photography, and technical support',
                'icon': 'fas fa-video'
            },
            {
                'name': 'Security & Safety',
                'description': 'Event security, crowd control, and safety management',
                'icon': 'fas fa-shield-alt'
            },
            {
                'name': 'Marketing & Promotion',
                'description': 'Product promotion, sales, and marketing activities',
                'icon': 'fas fa-bullhorn'
            },
            {
                'name': 'Setup & Logistics',
                'description': 'Event setup, breakdown, and logistics support',
                'icon': 'fas fa-boxes'
            },
            {
                'name': 'Entertainment & Performance',
                'description': 'Entertainment, performance, and artistic roles',
                'icon': 'fas fa-music'
            },
            {
                'name': 'Administrative',
                'description': 'Administrative support, data entry, and coordination',
                'icon': 'fas fa-clipboard'
            },
            {
                'name': 'Volunteer & Community',
                'description': 'Volunteer work and community service events',
                'icon': 'fas fa-hands-helping'
            }
        ]

        created_count = 0
        for category_data in categories_data:
            category, created = JobCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon']
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} job categories')
        )
