import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "flights.settings"
django.setup()


from django.contrib.auth.models import User

# Apply is_staff=True to User.pk = 1 (Ziv Attias)
user = User.objects.get(pk=1)
user.is_staff = True
user.save()
