''' Decorators '''
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.http.response import JsonResponse
from contracts.models import ContractsModel

def anonymous_only(redirect_to=None):
    ''' 
    Anonymous Decorator Function 
    '''

    def decorator(view_func):
        ''' Decorator '''
        def wrapper(request, *args, **kwargs):
            ''' Wrapper '''
            redirect_url = kwargs.get('redirect_to', reverse_lazy('accounts:dashboard'))
            if not request.user.is_anonymous and request.method == 'GET':
                redirect_to = redirect(redirect_url)
            else:
                redirect_to = view_func(request, *args, **kwargs)
            return redirect_to
        return wrapper
    return decorator

def anonymous_view(cls=None, **function_args):
    ''' 
    Anonymous View Dispatch
    '''
    if cls is not None:
        if not hasattr(cls, 'dispatch'):
            raise TypeError(('View class is not valid: %r.  Class-based views '
                             'must have a dispatch method.') % cls)
        original = cls.dispatch
        modified = method_decorator(
            anonymous_only(**function_args))(original)
        cls.dispatch = modified
        return cls
    else:
        def inner_decorator(inner_cls):
            ''' Inner Decorator '''
            return anonymous_view(inner_cls, **function_args)
        return inner_decorator


def check_user_response(request, next_url, redirect_to):
    '''
    Decorator
    Check User Response
    '''
    response = None
    new_next_url = request.path_info
    if request.user.is_anonymous:
        redirect_url = redirect_to if redirect_to else reverse('home')
        redirect_url = '%s?next_url=%s' % (
            redirect_url, new_next_url) if new_next_url else redirect_url
        response = JsonResponse(data={'login': True, 'next': redirect_url}) if request.is_ajax() else redirect(
            redirect_url)
    return response

def logged_only(redirect_to=None, next_url=None):
    ''' Logged User View Only
    if request is not from logged in user it redirect
    to the url provided in redirect_to parameters'''

    def decorator(view_func):
        ''' Decorator '''
        def wrapper(request, *args, **kwargs):
            ''' Wrapper '''
            response = check_user_response(request, next_url, redirect_to)
            if not response:
                response = view_func(request, *args, **kwargs)
            return response
        return wrapper

    return decorator

def logged_user_view(cls=None, **function_args):
    '''
    Logged User View
    '''
    if cls is not None:
        if not hasattr(cls, 'dispatch'):
            raise TypeError(('View class is not valid: %r.  Class-based views '
                             'must have a dispatch method.') % cls)

        original = cls.dispatch
        modified = method_decorator(
            logged_only(**function_args))(original)
        cls.dispatch = modified
        return cls
    else:
        def inner_decorator(inner_cls):
            '''
            Inner Decorators
            '''
            return logged_user_view(inner_cls, **function_args)

        return inner_decorator


class PermissionRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        contract = ContractsModel.objects.filter(id=self.kwargs.get('id'))
        if contract.first().created_with == self.request.user or contract.first().created_by == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        else:
            redirect_url = reverse('accounts:dashboard')
            return redirect(redirect_url)
