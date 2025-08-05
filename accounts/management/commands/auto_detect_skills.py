from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from accounts.models import Skill

User = get_user_model()


class Command(BaseCommand):
    help = 'Auto-detect and assign skills to existing users based on their activity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Update skills for a specific user ID'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update skills even if user already has skills assigned'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        force = options.get('force', False)
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                users = [user]
                self.stdout.write(f'Processing user: {user.username}')
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with ID {user_id} does not exist')
                )
                return
        else:
            # Get all users
            if force:
                users = User.objects.filter(role='volunteer')
                self.stdout.write('Processing all users (force mode)')
            else:
                # Only process users without skills
                users = User.objects.filter(role='volunteer', skills__isnull=True).distinct()
                self.stdout.write('Processing users without assigned skills')
        
        total_users = users.count()
        self.stdout.write(f'Found {total_users} users to process')
        
        updated_count = 0
        skills_created = 0
        
        for user in users:
            initial_skills_count = user.skills.count()
            
            # Auto-detect skills
            user.auto_detect_skills()
            
            final_skills_count = user.skills.count()
            new_skills = final_skills_count - initial_skills_count
            
            if new_skills > 0:
                updated_count += 1
                skills_created += new_skills
                self.stdout.write(
                    f'✓ {user.username}: Added {new_skills} skill(s)'
                )
            else:
                self.stdout.write(
                    f'- {user.username}: No new skills detected'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! '
                f'Updated {updated_count} users, '
                f'created {skills_created} skill assignments.'
            )
        )
        
        # Show summary of most common skills
        self.stdout.write('\nMost common auto-detected skills:')
        common_skills = Skill.objects.filter(
            description__icontains='auto-detected'
        ).annotate(
            user_count=models.Count('user')
        ).order_by('-user_count')[:10]
        
        for skill in common_skills:
            self.stdout.write(f'  - {skill.name}: {skill.user_count} users')
