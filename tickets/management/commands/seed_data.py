import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Department
from tickets.models import Category, CannedResponse
from knowledge.models import KBCategory, Article
from django.utils.text import slugify

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with initial demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Departments
        depts = ['IT', 'HR', 'Finance', 'Operations', 'Sales', 'Marketing', 'Engineering']
        for name in depts:
            Department.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('  ✓ Departments created'))

        # Ticket Categories
        categories = [
            {'name': 'Hardware', 'slug': 'hardware', 'type': 'hardware', 'icon': 'pc-display', 'color': 'primary'},
            {'name': 'Network & Connectivity', 'slug': 'network', 'type': 'network', 'icon': 'wifi', 'color': 'info'},
            {'name': 'Software & Applications', 'slug': 'software', 'type': 'software', 'icon': 'app-indicator', 'color': 'success'},
            {'name': 'Account & Access', 'slug': 'account', 'type': 'account', 'icon': 'person-lock', 'color': 'warning'},
            {'name': 'Security', 'slug': 'security', 'type': 'security', 'icon': 'shield-check', 'color': 'danger'},
            {'name': 'Other', 'slug': 'other', 'type': 'other', 'icon': 'tag', 'color': 'secondary'},
        ]
        for cat in categories:
            Category.objects.get_or_create(slug=cat['slug'], defaults=cat)
        self.stdout.write(self.style.SUCCESS('  ✓ Ticket categories created'))

        # KB Categories
        kb_cats = [
            {'name': 'Getting Started', 'slug': 'getting-started', 'icon': 'rocket', 'order': 1, 'description': 'New user guides and onboarding'},
            {'name': 'Hardware', 'slug': 'kb-hardware', 'icon': 'pc-display', 'order': 2, 'description': 'Device setup and troubleshooting'},
            {'name': 'Network', 'slug': 'kb-network', 'icon': 'wifi', 'order': 3, 'description': 'VPN, WiFi, and connectivity'},
            {'name': 'Software', 'slug': 'kb-software', 'icon': 'app-indicator', 'order': 4, 'description': 'Application guides and fixes'},
            {'name': 'Security', 'slug': 'kb-security', 'icon': 'shield-check', 'order': 5, 'description': 'Password and security policies'},
            {'name': 'Account Management', 'slug': 'kb-account', 'icon': 'person-gear', 'order': 6, 'description': 'Account access and permissions'},
        ]
        for kbc in kb_cats:
            KBCategory.objects.get_or_create(slug=kbc['slug'], defaults=kbc)
        self.stdout.write(self.style.SUCCESS('  ✓ KB categories created'))

        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin', email='admin@helpdesk.local',
                password='Admin@123', first_name='IT', last_name='Administrator',
                role='manager', job_title='IT Manager'
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Admin user created (admin / Admin@123)'))

        # Create demo agent
        if not User.objects.filter(username='agent1').exists():
            it_dept = Department.objects.filter(name='IT').first()
            agent = User.objects.create_user(
                username='agent1', email='agent@helpdesk.local',
                password='Agent@123', first_name='Sarah', last_name='Connor',
                role='agent', job_title='IT Support Analyst', department=it_dept
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Demo agent created (agent1 / Agent@123)'))

        # Create demo end user
        if not User.objects.filter(username='user1').exists():
            User.objects.create_user(
                username='user1', email='user@helpdesk.local',
                password='User@123', first_name='John', last_name='Doe',
                role='end_user', job_title='Sales Representative'
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Demo user created (user1 / User@123)'))

        # Sample article
        admin_user = User.objects.filter(username='admin').first()
        kb_start = KBCategory.objects.filter(slug='getting-started').first()
        if admin_user and kb_start and not Article.objects.exists():
            Article.objects.create(
                title='How to Submit a Support Ticket',
                slug='how-to-submit-support-ticket',
                category=kb_start,
                author=admin_user,
                summary='Step-by-step guide to submitting your first IT support ticket.',
                content="""1. Click "New Ticket" in the top navigation or sidebar.

2. Fill in the Ticket Title — be specific about your issue.

3. Select the appropriate Category (Hardware, Software, Network, etc.).

4. Set the Priority level:
   - Low: Minor inconvenience, no urgency
   - Medium: Affecting your work but you have a workaround
   - High: Significantly impacting your work
   - Critical: Complete outage or security incident

5. Write a detailed Description including:
   - What you were trying to do
   - What happened instead
   - Any error messages you see
   - When the issue started

6. Attach screenshots or files if they help illustrate the problem.

7. Click Submit Ticket.

You will receive a confirmation with your ticket ID. You can track the status at any time from the My Tickets page.""",
                is_published=True
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Sample article created'))

        # Canned responses
        if admin_user and not CannedResponse.objects.exists():
            CannedResponse.objects.create(
                title='Acknowledge & Investigating',
                body='Thank you for contacting IT support. I have received your ticket and am currently investigating the issue. I will update you within the hour.',
                created_by=admin_user
            )
            CannedResponse.objects.create(
                title='Need More Information',
                body='Thank you for your ticket. To help resolve your issue faster, could you please provide:\n\n1. The exact error message (if any)\n2. Which device/computer you are using\n3. What steps lead to the issue\n\nPlease reply with these details and we will proceed.',
                created_by=admin_user
            )
            CannedResponse.objects.create(
                title='Issue Resolved - Please Confirm',
                body='I believe the issue has been resolved. Could you please test and confirm that everything is working as expected? If you continue to experience problems, please let me know and I will continue investigating.',
                created_by=admin_user
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Canned responses created'))

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeding complete!\n'))
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin/Manager: admin / Admin@123')
        self.stdout.write('  IT Agent:      agent1 / Agent@123')
        self.stdout.write('  End User:      user1 / User@123')
