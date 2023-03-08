'''
verification steps
'''
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View
from django.urls import reverse_lazy
from django.http.response import HttpResponseRedirect, JsonResponse
from app.string import Hash
from app import messages
from accounts.models import UserSecurityToken

class ResendVerificationToken(View):
    ''' 
    Resend Verification Token 
    '''

    def get(self, *args, **kwargs):
        user = get_user_model().objects.filter(email__iexact=kwargs['email']).get()
        try:
            ''' filtering email from UserSecurityToken '''
            user_token = UserSecurityToken.objects.filter(
                extras=kwargs['email'], token_type=UserSecurityToken.ACCOUNT_ACTIVATION_TOKEN).last()
            ''' user token validate'''
            if user_token:
                user_token.expire_date = timezone.now()
                user_token.save()
            token = UserSecurityToken.create_activation_token(
                kwargs['email'],user )
            token.send_verify_token_email(self.request)

            '''only for ajax request'''
            if self.request.is_ajax():
                data = {'success': False,
                        'message': messages.VERIFICATION_EMAIL_SENT}
                data['success'] = True


        except UserSecurityToken.DoesNotExist:
            data = {}
            data['success'] = False
            data['message'] = messages.USER_DOESNOT_EXIST


        if self.request.is_ajax():
            return JsonResponse(data)

        else:
            return HttpResponseRedirect(reverse_lazy('accounts:email_verification_confirmation'))

class VerificationView(View):
    '''
    Verify user account and redirects to profile's page
    '''
    template_name = 'accounts/email/email-verification-success-message.html'

    def get(self, request, *args, **kwargs):
        valid_link, email = self._is_valid_link(*args, **kwargs)

        validity = 'valid_token'
        if valid_link == 'expired':
            validity = 'expired-token'
            self.template_name = 'accounts/email/link-expired.html'
        return render(request, self.template_name, {'validity': validity, 'email': email})

    def get_context_data(self, **kwargs):
        context = super(VerificationView, self).get_context_data(**kwargs)
        context.update({'title': 'Verification'})
        return context

    def _is_valid_link(self, *args, **kwargs):
        '''Check if change password link is valid '''
        email = Hash.decrypt_string(kwargs['id'].encode('utf-8'))
        email = email.decode('utf-8')
        validlink = None
        user_email = ''
        try:
            user = get_user_model().objects.filter(email__iexact=email).get()
            try:
                token = kwargs['token']
                user_token = UserSecurityToken.objects.filter(token=token,
                                                              extras=email).get()
                ''' checking the expiry date of user token '''                  
                if user_token.expire_date > timezone.now():
                    user_token.expire_date = timezone.now()
                    user_token.save()
                    user.verified_date = timezone.now()
                    user.is_verified = True 
                    user.is_active = True
                    user.save()
                    validlink = True
                else:
                    validlink = 'expired'
                    user_email = user_token.user.email

            except UserSecurityToken.DoesNotExist:
                validlink = 'invalid'
        except get_user_model().DoesNotExist:
            validlink = 'invalid'
        return validlink, user_email