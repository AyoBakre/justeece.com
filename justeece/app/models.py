from django.db import models
from justeece.core.utils import TimestampedModel
from django.conf import settings
from tinymce.models import HTMLField
from storages.backends.s3boto3 import S3Boto3Storage

# Create your models here.

class S3ImageField(models.FileField):

    def __init__(self, *args, **kwargs):
        super(S3ImageField, self).__init__(*args, **kwargs)
        self.storage = kwargs.get('storage',None)
        if not self.storage:
            self.storage = S3Boto3Storage()

class EmailMessage(TimestampedModel):

    PENDING = 1
    INPROGRESS = 2
    SENT = 3
    ERROR = 4

    STATUS_TYPE = ((PENDING, ('Pending')), (INPROGRESS, ('In-Progress')),
                   (SENT, ('Sent')), (ERROR, ('Error')))

    from_email = models.CharField(max_length=500, default=settings.EMAIL_DEFAULT)
    to_email = models.CharField(max_length=500, blank=True, null=True)
    cc = models.CharField(max_length=500, blank=True, null=True)
    bcc = models.CharField(max_length=500, blank=True, null=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    html_message = HTMLField()
    tries = models.PositiveSmallIntegerField(default=0)
    error_detail = models.CharField(max_length=255, null=True, blank=True)
    sent_status = models.SmallIntegerField(
        choices=STATUS_TYPE, default=PENDING)
    sent_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return u'%s' % self.id

class TestimonialModel(TimestampedModel):
    feedback = models.CharField(max_length=250)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True, on_delete=models.CASCADE, related_name='testimonial_user')

    def __str__(self):
        return u'%s' % self.user


class MaillMessage(TimestampedModel):
    
    INCOMPLETE_REGISTRANT = 1
    COMPLETE_REGISTRANT_WITH_REFERENCE = 2
    COMPLETE_REGISTRANT_WITHOUT_REFERENCE = 3
    REFERENCE_EMAIL_REMINDER = 4

    GROUP = ((INCOMPLETE_REGISTRANT, ('INCOMPLETE_REGISTRANT')), (COMPLETE_REGISTRANT_WITH_REFERENCE, ('COMPLETE_REGISTRANT_WITH_REFERENCE')),
                   (COMPLETE_REGISTRANT_WITHOUT_REFERENCE, ('COMPLETE_REGISTRANT_WITHOUT_REFERENCE')), (REFERENCE_EMAIL_REMINDER, ('REFERENCE_EMAIL_REMINDER')))

    title = models.CharField(max_length=80)
    subject = models.CharField(max_length=250)
    body = models.TextField(max_length=1050)
    group = models.SmallIntegerField(choices=GROUP, null=True, blank=True)
    send_it = models.BooleanField(default=False) #check it if you want to send your email

    def save(self, *args, **kwargs):
        from accounts.models import User, ReferenceRequestId
        from .email import Email
        from django.conf import settings
        
        if self.send_it:
            if self.group == 1:
                users = User.objects.filter(profile_added=False, subscribed=True)

                for user in users:
                    link = settings.SITE_URL + '/accounts/unsubscribe/' + str(user.pk)
                    try: 
                        Email(user.email, self.subject).message_from_template_schedule('accounts/email/email_reminder.html',
                                                        {'body': self.body, 'first_name': user.first_name, 'last_name': user.last_name, 'link': link}).send()

                        print('email sent**********************')
                    except Exception as e:
                        print(e)

            elif self.group == 2:
                users = User.objects.filter(profile_added=True, subscribed=True,)

                for user in users:
                    if user.reference_for_user.count():
                        link = settings.SITE_URL + '/accounts/unsubscribe/' + str(user.pk)
                        try: 
                            Email(user.email, self.subject).message_from_template_schedule('accounts/email/email_reminder.html',
                                                        {'body': self.body, 'first_name': user.first_name, 'last_name': user.last_name, 'link': link}).send()

                            print('email sent**********************')
                        except Exception as e:
                            print(e)

            elif self.group == 3:
                users = User.objects.filter(profile_added=True, subscribed=True,)

                for user in users:
                    if not user.reference_for_user.count():
                        link = settings.SITE_URL + '/accounts/unsubscribe/' + str(user.pk)
                        try: 
                            Email(user.email, self.subject).message_from_template_schedule('accounts/email/email_reminder.html',
                                                        {'body': self.body, 'first_name': user.first_name, 'last_name': user.last_name, 'link': link}).send()

                            print('email sent**********************')
                        except Exception as e:
                            print(e)

            elif self.group == 4:
                references_not_added = ReferenceRequestId.objects.filter(reference_added=False)
                for referee in references_not_added:
                    try: 
                        link = settings.SITE_URL + '/accounts/add_reference/' + str(referee.pk)
                        Email(referee.email, self.subject).message_from_template_schedule('accounts/email/reference.html',
                                                                                {'reference_name': referee.name,
                                                                                'user_first_name': referee.user.first_name,
                                                                                'user_last_name':  referee.user.last_name,
                                                                                'link': link}).send()
                    except Exception as e:
                        print(e)

        super(MaillMessage, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class AllSearches(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="search_by_user", null=True, blank=True)
    search = models.CharField(max_length=100, null=True, blank=True)