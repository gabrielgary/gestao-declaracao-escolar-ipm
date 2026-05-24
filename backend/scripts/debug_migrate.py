
import os
import sys
import django
from django.core.management import call_command
import traceback

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

try:
    print("Setting up Django...")
    django.setup()
    print("Django setup complete.")
    
    print("Calling makemigrations...")
    call_command('makemigrations', 'apis')
    print("makemigrations finished.")
    
except Exception as e:
    print("AN ERROR OCCURRED:")
    print(str(e))
    traceback.print_exc()
