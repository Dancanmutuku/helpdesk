import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from accounts.models import Department
from tickets.models import Ticket, TicketReply, Category

User = get_user_model()

# ── Sample data pools ────────────────────────────────────────

FIRST_NAMES = ['James', 'Emily', 'Michael', 'Sarah', 'David',
               'Jessica', 'Daniel', 'Laura', 'Chris', 'Amanda']
LAST_NAMES  = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones',
               'Garcia', 'Miller', 'Davis', 'Wilson', 'Taylor']
JOB_TITLES  = ['Software Engineer', 'Accountant', 'HR Coordinator',
               'Sales Executive', 'Marketing Analyst', 'Operations Lead',
               'Finance Manager', 'Product Manager', 'Data Analyst', 'Designer']

TICKET_DATA = [
    # (title, description, category_slug, priority)
    ('Cannot connect to VPN from home',
     'I am unable to connect to the company VPN since yesterday. I get error code 800 when trying to connect. I have tried restarting my router and reinstalling the VPN client but it still fails.',
     'network', 'high'),

    ('Laptop screen flickering randomly',
     'My Dell laptop screen has been flickering on and off since this morning. It happens every few minutes and makes it hard to work. The issue persists even when connected to external monitor.',
     'hardware', 'medium'),

    ('Cannot open Microsoft Excel files',
     'When I double click any .xlsx file I get the error "Excel cannot open the file because the file format or extension is not valid." This started after the Windows update last night.',
     'software', 'high'),

    ('Password reset request',
     'I have been locked out of my account after too many failed login attempts. I need my password reset urgently as I have a client presentation in 2 hours.',
     'account', 'critical'),

    ('Printer on 3rd floor not working',
     'The HP LaserJet printer in the 3rd floor kitchen area is showing "offline" status for everyone in the department. Last worked fine on Friday. We have checked the power and network cable.',
     'hardware', 'medium'),

    ('Suspicious email received — possible phishing',
     'I received an email claiming to be from our IT department asking me to click a link and enter my login credentials. The sender address looks fake. I have not clicked the link. Please advise.',
     'security', 'critical'),

    ('Slow internet connection in conference room B',
     'The WiFi in conference room B has been extremely slow for the past week. Video calls keep dropping and file uploads take forever. Other rooms seem fine.',
     'network', 'medium'),

    ('Need access to SharePoint project folder',
     'I have recently joined the Product team and need access to the SharePoint folder "Product Roadmap 2025". My manager James Wilson has approved this request.',
     'account', 'low'),

    ('Microsoft Teams not loading on Mac',
     'Microsoft Teams crashes immediately on launch on my MacBook Pro (M2, macOS Ventura). I have uninstalled and reinstalled twice but it still crashes. I need Teams for daily standups.',
     'software', 'high'),

    ('New employee laptop setup request',
     'We have a new team member starting Monday — Alex Thompson. They will need a laptop configured with the standard software suite, company email, and VPN access.',
     'hardware', 'medium'),

    ('Cannot access company email on mobile',
     'My work email stopped syncing on my iPhone after I updated iOS yesterday. The Outlook app keeps saying "Authentication required" but my password is correct.',
     'account', 'medium'),

    ('Blue screen of death on workstation',
     'My desktop PC crashed with a blue screen showing "MEMORY_MANAGEMENT" error. It has happened 3 times today. I have important work that I cannot access. Error code: 0x0000001A.',
     'hardware', 'critical'),

    ('Request for Adobe Creative Cloud license',
     'I need Adobe Photoshop and Illustrator for a new design project approved by my manager. Could you please provision an Adobe Creative Cloud license for my account?',
     'software', 'low'),

    ('Two-factor authentication not working',
     'The 2FA code I receive via SMS is being rejected when I try to log into the company portal. I have tried multiple times over the past hour. My phone number is correct in my profile.',
     'security', 'high'),

    ('Keyboard and mouse unresponsive after sleep',
     'After my laptop wakes from sleep mode, the USB keyboard and mouse stop responding. I have to unplug and replug them every time. Happens about 5 times a day.',
     'hardware', 'low'),

    ('Need to reset another employee account',
     'Our team member Maria Santos is on maternity leave and we urgently need access to her email to retrieve a client contract. Please advise on the process.',
     'account', 'high'),

    ('Company website down — cannot access internally',
     'Our internal staff portal at portal.company.com is returning a 503 error for everyone in the office. External access also seems affected. This is impacting all departments.',
     'network', 'critical'),

    ('Zoom audio not working during calls',
     'Other participants cannot hear me during Zoom meetings even though my microphone works fine in other applications. Zoom shows my mic is active but no audio is transmitted.',
     'software', 'medium'),

    ('Request for additional monitor',
     'I work with large spreadsheets and multiple applications simultaneously. Could I please get an additional monitor? My desk has space and I have the necessary HDMI ports.',
     'hardware', 'low'),

    ('Ransomware warning message appeared',
     'A popup appeared on my screen saying my files have been encrypted and demanding payment. I immediately disconnected from the network. My files in Documents folder show strange extensions.',
     'security', 'critical'),
]

AGENT_REPLIES = [
    'Thank you for contacting IT support. I have received your ticket and am investigating the issue now. I will update you shortly.',
    'I have looked into this and have a solution ready. Please follow the steps I have outlined and let me know if it resolves the issue.',
    'Could you please provide some additional information? Specifically, which operating system version are you running and when exactly did this issue first occur?',
    'I have escalated this to our senior engineer who specialises in this area. You should hear back within the next 2 hours.',
    'I have remotely accessed your machine and applied the fix. Please restart your computer and test again.',
    'This is a known issue affecting a few users after the recent update. Our team is working on a patch. Expected resolution: today by 5pm.',
    'I have reset the relevant settings on our end. Please try again and confirm if the issue is resolved.',
    'Thank you for your patience. The issue has been identified and resolved. Please let me know if you experience any further problems.',
]

USER_REPLIES = [
    'Thank you, I will try that now.',
    'Still not working unfortunately. I followed all the steps but the same error appears.',
    'That worked! Thank you so much for the quick response.',
    'I have restarted as suggested but the problem persists. Same error message.',
    'I can confirm the issue is now resolved. Thanks for your help.',
    'Quick update — the issue came back this morning after I restarted my laptop.',
]


class Command(BaseCommand):
    help = 'Creates 6 demo users and 20 demo tickets with replies'

    def add_arguments(self, parser):
        parser.add_argument('--users',   type=int, default=6,  help='Number of end users to create (default: 6)')
        parser.add_argument('--tickets', type=int, default=20, help='Number of tickets to create (default: 20)')
        parser.add_argument('--clear',   action='store_true',  help='Delete existing demo tickets and users first')

    def handle(self, *args, **options):
        num_users   = options['users']
        num_tickets = options['tickets']
        clear       = options['clear']

        if clear:
            deleted_t, _ = Ticket.objects.filter(title__in=[t[0] for t in TICKET_DATA]).delete()
            deleted_u, _ = User.objects.filter(username__startswith='demouser').delete()
            self.stdout.write(self.style.WARNING(f'  ✗ Cleared {deleted_t} tickets and {deleted_u} demo users'))

        self.stdout.write(self.style.HTTP_INFO('\n🚀 Creating demo data...\n'))

        # ── 1. Ensure we have agents to assign to ────────────
        agents = list(User.objects.filter(role__in=['agent', 'manager']))
        if not agents:
            self.stdout.write(self.style.ERROR(
                '  ✗ No agents found. Run python manage.py seed_data first.'
            ))
            return

        # ── 2. Fetch categories & departments ────────────────
        categories  = list(Category.objects.filter(is_active=True))
        departments = list(Department.objects.all())

        if not categories:
            self.stdout.write(self.style.ERROR(
                '  ✗ No categories found. Run python manage.py seed_data first.'
            ))
            return

        # ── 3. Create end users ───────────────────────────────
        created_users = []
        self.stdout.write('👤 Creating users...')

        for i in range(1, num_users + 1):
            username = f'demouser{i}'
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(f'   → {username} already exists, reusing')
            else:
                first = random.choice(FIRST_NAMES)
                last  = random.choice(LAST_NAMES)
                dept  = random.choice(departments) if departments else None
                user  = User.objects.create_user(
                    username   = username,
                    email      = f'{username}@helpdesk.local',
                    password   = 'Demo@123',
                    first_name = first,
                    last_name  = last,
                    role       = 'end_user',
                    job_title  = random.choice(JOB_TITLES),
                    department = dept,
                )
                self.stdout.write(self.style.SUCCESS(
                    f'   ✓ {username} ({first} {last}) — Demo@123'
                ))
            created_users.append(user)

        # ── 4. Create tickets ─────────────────────────────────
        self.stdout.write(f'\n🎫 Creating {num_tickets} tickets...')

        ticket_pool = TICKET_DATA[:num_tickets]
        # If more tickets requested than pool, cycle through
        while len(ticket_pool) < num_tickets:
            ticket_pool += TICKET_DATA[:num_tickets - len(ticket_pool)]

        statuses  = ['open', 'in_progress', 'in_progress', 'pending', 'resolved', 'closed']
        created_tickets = []

        for i, (title, description, cat_slug, priority) in enumerate(ticket_pool):
            # Spread creation dates over the last 30 days
            days_ago    = random.randint(0, 30)
            created_at  = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

            submitter   = random.choice(created_users)
            status      = random.choice(statuses)
            assigned_to = random.choice(agents) if random.random() > 0.2 else None

            # Find matching category or fallback to random
            cat = Category.objects.filter(slug=cat_slug).first() or random.choice(categories)

            # Compute SLA based on priority
            from django.conf import settings
            sla_hours   = getattr(settings, 'SLA_RESPONSE_TIMES', {}).get(priority, 24)
            sla_due_at  = created_at + timedelta(hours=sla_hours)
            sla_breached = timezone.now() > sla_due_at and status not in ['resolved', 'closed']

            resolved_at = None
            closed_at   = None
            if status == 'resolved':
                resolved_at = created_at + timedelta(hours=random.randint(1, sla_hours))
            if status == 'closed':
                closed_at = created_at + timedelta(hours=random.randint(2, sla_hours + 5))

            csat_score   = None
            csat_comment = ''
            if status in ['resolved', 'closed'] and random.random() > 0.4:
                csat_score   = random.choices([3, 4, 4, 5, 5, 5], k=1)[0]
                csat_comment = random.choice([
                    'Very quick response, thank you!',
                    'Issue resolved efficiently.',
                    'Took a while but was sorted in the end.',
                    'Great support as always.',
                    '',
                ])

            ticket = Ticket(
                title        = title,
                description  = description,
                category     = cat,
                priority     = priority,
                status       = status,
                source       = random.choice(['web', 'web', 'email', 'chat']),
                submitted_by = submitter,
                assigned_to  = assigned_to,
                sla_due_at   = sla_due_at,
                sla_breached = sla_breached,
                resolved_at  = resolved_at,
                closed_at    = closed_at,
                csat_score   = csat_score,
                csat_comment = csat_comment,
            )

            # Bypass auto-save logic that would overwrite sla_due_at/ticket_id
            ticket.ticket_id = ticket._generate_ticket_id()
            Ticket.objects.bulk_create([ticket])
            ticket = Ticket.objects.get(ticket_id=ticket.ticket_id)

            # Fix created_at (bulk_create ignores auto_now_add)
            Ticket.objects.filter(pk=ticket.pk).update(created_at=created_at, updated_at=created_at)

            created_tickets.append(ticket)
            self.stdout.write(self.style.SUCCESS(
                f'   ✓ [{ticket.ticket_id}] {title[:55]}... [{priority.upper()}] [{status}]'
            ))

            # ── 5. Add replies ────────────────────────────────
            num_replies = random.randint(0, 3)
            reply_time  = created_at

            for r in range(num_replies):
                reply_time = reply_time + timedelta(hours=random.randint(1, 8))
                is_agent_reply = r % 2 == 0  # agent first, then user alternates

                author = random.choice(agents) if is_agent_reply else submitter
                body   = random.choice(AGENT_REPLIES if is_agent_reply else USER_REPLIES)

                reply = TicketReply(
                    ticket      = ticket,
                    author      = author,
                    body        = body,
                    is_internal = False,
                )
                TicketReply.objects.bulk_create([reply])
                TicketReply.objects.filter(ticket=ticket, body=body).update(created_at=reply_time)

        # ── Summary ───────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(f'''
╔══════════════════════════════════════════╗
║         Demo Data Created! ✅            ║
╠══════════════════════════════════════════╣
║  Users created   : {num_users:<23}║
║  Tickets created : {num_tickets:<23}║
╠══════════════════════════════════════════╣
║  User logins     : demouser1–{str(num_users):<14}║
║  Password        : Demo@123              ║
╚══════════════════════════════════════════╝
'''))

        # Ticket status breakdown
        from django.db.models import Count
        breakdown = Ticket.objects.values('status').annotate(count=Count('id')).order_by('status')
        self.stdout.write('  Ticket breakdown:')
        for row in breakdown:
            self.stdout.write(f"    {row['status']:<15} {row['count']} tickets")
        self.stdout.write('')
