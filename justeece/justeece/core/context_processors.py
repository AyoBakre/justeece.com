'''
Context Processor
A context processor has a very simple interface:
It’s just a Python function that takes one argument,
an HttpRequest object, and returns a dictionary that
gets added to the template context. Each context
processor must return a dictionary.
'''
from django.conf import settings
from django.utils import timezone
from django.urls import reverse, reverse_lazy

def site_config(request):
    ''' 
    Site configurations
    it returns various constants ,
    price filters and site languages,
    and media config keys containing default image
    and image path of stored media in aws bucket
    '''
    login_url = reverse_lazy('accounts:login')
    login_url = '%s://%s/%s' % (request.scheme, request.get_host(), login_url[1:])
    return {
        'login_url': login_url,
    }
       