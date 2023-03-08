'''
Email reusable component
'''

from django.conf import settings
from django.core.mail import EmailMessage as DjangoMail
from django.template.loader import get_template
from . import messages


class Email(object):
    ''' 
    Email Create Object 
    '''

    def __init__(self, to, subject, html_message=None, cc=None, bcc=None, from_addr=None):
        if not isinstance(to, list):
            self.to = [to, ]
        else:            
            self.to = to
        if cc and not isinstance(cc, list) :
            self.cc = [cc, ]
        else:
            self.cc = cc
        if bcc and not isinstance(bcc, list):
            self.bcc = [bcc, ]
        else:
            self.bcc = bcc
        self.subject = subject
        self.html = html_message
        self.from_addr = from_addr

    def html(self, html):
        ''' Html object '''
        self.html = html
        return self

    def from_address(self, from_address):
        ''' From Address '''
        self.from_addr = from_address
        return self

    def message_from_template(self, template_name, context, request=None):
        ''' Message Body '''
        self.html = get_template(template_name).render(context, request)
        return self

    def message_from_template_schedule(self, template_name, context,):
        ''' Message Body '''
        self.html = get_template(template_name).render(context,)
        return self

    def send(self):
        ''' Create mail object '''
        if not self.from_addr:
            self.from_addr = settings.EMAIL_DEFAULT
        if not self.html:
            raise Exception(messages.TEXT_OR_HTML_REQUIRED)
        email_data = {
            'from_email': self.from_addr,
            'to_email': self.to,
            'cc': self.cc,
            'bcc': self.bcc,
            'subject': self.subject,
            'html_message': self.html
        }
        from .models import EmailMessage
        email_obj = EmailMessage.objects.create(**email_data)
        ''' sending email '''
        try:
            if self.cc:
                email = DjangoMail(self.subject, self.html,
                                self.from_addr, to=self.to, cc=self.cc, bcc=self.bcc)
            else:
                email = DjangoMail(self.subject, self.html,
                                self.from_addr, to=self.to)
            email.content_subtype = "html"
            email.send()
            email_obj.status = EmailMessage.SENT
            email_obj.save()
        except Exception:
            pass
