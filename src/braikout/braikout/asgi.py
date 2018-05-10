import os

import channels.asgi
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "braikout.settings")
django.setup()
channel_layer = channels.asgi.get_channel_layer()