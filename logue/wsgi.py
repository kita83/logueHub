"""
WSGI config for logue project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import threading
import requests
import time

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logue.settings")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)

def awake():
    while True:
        try:
            print("Start Awaking")
            requests.get("https://loguehub.herokuapp.com/")
            print("End")
        except:
            print("error")
        time.sleep(300)

t = threading.Thread(target=awake)
t.start()