import os
import django
from django.core.management import call_command

# Step 1: Set the DJANGO_SETTINGS_MODULE to your settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # adjust if your settings file is in a different path

# Step 2: Initialize Django
django.setup()

# Step 3: Dump data to UTF-8 JSON
with open('db.json', 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        '--natural-primary',
        '--natural-foreign',
        '--exclude', 'auth.permission',
        '--exclude', 'contenttypes',
        stdout=f
    )

print("Data successfully exported to db.json (UTF-8)!")