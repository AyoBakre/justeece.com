from django.views.generic import FormView, TemplateView
from django.shortcuts import redirect,render
from django.contrib.auth import logout as auth_logout,login as auth_login
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.utils import timezone
from accounts.forms import ForgotPasswordRequestForm, ResetPasswordForm
from accounts.models import UserSecurityToken
from app.decorators import anonymous_only,anonymous_view
from app.string import Hash


@anonymous_view(redirect_to='/accounts/success')
class ForgotPasswordRequestView(FormView):
    ''' 
    ForgotPassword Request View 
    '''
    form_class = ForgotPasswordRequestForm
    template_name = 'accounts/forgot_password.html'

    def get(self, request, *args, **kwargs):
        '''
        get request
        '''
        auth_logout(request)
        return super(ForgotPasswordRequestView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        ''' get form kwargs '''
        data = super(ForgotPasswordRequestView, self).get_form_kwargs()
        data.update({'request': self.request})
        return data

    def form_valid(self, form):
        '''form valid'''
        _ = self.__class__
        form.save() 
        return redirect(reverse('accounts:forgot-password'))

@anonymous_view(redirect_to='/accounts/success')
class ResetPasswordView(FormView):
    '''
    Reset Password form
    '''
    template_name = 'accounts/reset_password.html'
    form_class = ResetPasswordForm
    valid_token = ''

    def get(self, request, *args, **kwargs):
        '''get request'''
        valid_link= self._is_valid_link(*args)
        if valid_link == 'expired':
            self.template_name = 'forgot_password_link_expired.html'
            return render(request, self.template_name)
        return super(ResetPasswordView, self).get(request, *args, **kwargs)

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(ResetPasswordView, self).dispatch(request, *args, **kwargs)
        except UserSecurityToken.DoesNotExist:
            return HttpResponseRedirect(reverse('login'))

    def get_form_kwargs(self):
        '''update form args '''
        data = super(ResetPasswordView, self).get_form_kwargs()
        self.valid_token = self._is_valid_link()
        data.update({'request': self.request,
                     'token': self.valid_token
                     })
        return data

    def form_valid(self, form):
        ''' form valid '''
        form.save()
        return super(ResetPasswordView, self).form_valid(form)

    def get_success_url(self):
        '''get succcess url '''
        _ = self.__class__
        return reverse('accounts:reset_password_success')

    def get_context_data(self, **kwargs):
        context = super(ResetPasswordView, self).get_context_data(**kwargs)
        email = Hash.decrypt_string(self.kwargs['id'].encode('utf-8'))
        email = email.decode('utf-8')
        context.update({'title': 'Reset Password',
                        'validity': self.valid_token,
                        'emailtype': self.kwargs['emailtype'],
                        'email': email})
        return context

    def _is_valid_link(self):
        '''check if change password link is valid '''
        email = Hash.decrypt_string(self.kwargs['id'].encode('utf-8'))
        email = email.decode('utf-8')
        valid_token = None

        try:
            user = get_user_model().objects.filter(email__iexact=email).get()
            try:
                user_token = UserSecurityToken.objects.filter(token=self.kwargs['token'],
                                                              extras=email,
                                                              token_type=UserSecurityToken.FORGOT_PASSWORD).get()
                if not user.is_active:
                    valid_token = 'not-active'
                elif user_token.expire_date > timezone.now():
                    valid_token = user_token
                else:
                    valid_token = 'expired'
            except UserSecurityToken.DoesNotExist:
                valid_token = 'invalid'
        except get_user_model().DoesNotExist:
            valid_token = 'invalid'
        return valid_token

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

class ResetPasswordSuccessView(TemplateView):
    """
    View shows success page post successful forgot password form.
    """
    
    template_name   = 'accounts/updated-password-confirmation.html'
