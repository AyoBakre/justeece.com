from apscheduler.schedulers.background import BackgroundScheduler
# from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
# from django_apscheduler.models import DjangoJobExecution
import sys
from .models import MaillMessage
from .email import Email
from accounts.models import User
from django.conf import settings


# This is the function you want to schedule - add as many as you want and then register them in the start() function below
def send_email_complete_registrant():
    users = User.objects.filter(profile_added=True, subscribed=True,)
    
    for user in users:
        link = settings.SITE_URL + '/accounts/unsubscribe/' + str(user.pk)
        if user.reference_for_user.count():
            mail = MaillMessage.objects.filter(title='Complete Registrant With Reference').first()
        else:
            mail = MaillMessage.objects.filter(title='Complete Registrant Without Reference').first()
        
        try: 
            Email(user.email, mail.subject).message_from_template_schedule('accounts/email/email_reminder.html',
                                                        {'body': mail.body, 'first_name': user.first_name, 'last_name': user.last_name, 'link': link}).send()
        except Exception as e:
            print(e)


def send_email_incomplete_registrant():
    users = User.objects.filter(profile_added=False, subscribed=True)
    mail = MaillMessage.objects.filter(title='Incomplete Registrant').first()

    for user in users:
        link = settings.SITE_URL + '/accounts/unsubscribe/' + str(user.pk)
        try: 
            Email(user.email, mail.subject).message_from_template_schedule('accounts/email/email_reminder.html',
                                                        {'body': mail.body, 'first_name': user.first_name, 'last_name': user.last_name, 'link': link}).send()

            print('email sent**********************')
        except Exception as e:
            print(e)


def start():
    scheduler = BackgroundScheduler(timezone="Europe/Berlin")
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 24 hours
    scheduler.add_job(send_email_complete_registrant, 'cron', day_of_week='mon', hour='12', minute='10', second='00', name='email_complete_registrant', jobstore='default')
    scheduler.add_job(send_email_incomplete_registrant, 'cron', day_of_week='mon', hour='12', minute='12', second='00', name='email_incomplete_registrant', jobstore='default')
    
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...-------------------", file=sys.stdout)
