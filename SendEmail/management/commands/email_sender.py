__author__ = 'Muhammad Ahmad'

from django.core.management import BaseCommand
from SendEmail.views import *
from Users.models import *


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    help = "to run this command, type: python manage.py email_sender"

    def handle(self, *args, **options):
        try:
            users = UserInfo.objects.filter(confirmed_signup_for_newsletter=1)
            for u in users:
                try:
                    if u.is_active:
                        userId = u.id
                        sendEmail(userId)
                except Exception as ex:
                    print('error')
            print('done')
        except Exception as e:
            print(str(e))
