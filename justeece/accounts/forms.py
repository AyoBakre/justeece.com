from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.contrib import messages as flash_messages
from accounts import messages
from accounts.models import User, UserSecurityToken, LanguageModel, CountryModel,\
     CityModel, Reference, ReferenceRequestId
from app.validations import validate_password
from app.decorators import anonymous_only, anonymous_view
from app.email import Email
from django.conf import settings
from contracts.models import ContractsModel
import re


# function to remove special characters from form fields
def deEmojify(text):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', text)


class SignupForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    terms = forms.BooleanField(required=True,error_messages={'required': messages.TERMS_VALIDATION},widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ('first_name','last_name', 'email','password','terms') 

    def __init__(self, request=None, *args, **kwargs):
        self._token = None
        self._user_cache = None
        self.request = request

        super(SignupForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        try:
            get_user_model().objects.get(
                email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(messages.USER_WITH_THIS_MAIL_ALREADY_EXISTS,code='already_exist')

    def has_number(self, name):
        return any(char.isdigit() for char in name)

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if self.has_number(first_name):
            raise forms.ValidationError(messages.LETTERS_ONLY,code='integer_exists')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if self.has_number(last_name):
            raise forms.ValidationError(messages.LETTERS_ONLY,code='integer_exists')
        return last_name

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(SignupForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        self.request.session['user_email'] = user.email
        if commit:
            user.save()

                       
        self._token = UserSecurityToken.create_activation_token(
            user.email,user)
        self._token.send_verify_token_email(self.request)

        user.set_password(self.cleaned_data['password'])
        user.save()

        return user        


class LoginForm(forms.ModelForm):

    email = forms.EmailField(label=("Email"),
                             required=True,
                             error_messages={
                                 'required': messages.USER_EMPTY_EMAIL_VALIDATION,
                                 'invalid': messages.INVALID_EMAIL_ADDRESS})    

    password = forms.CharField(
        label=("Password"),
        widget=forms.PasswordInput,
        error_messages={'required': messages.USER_EMPTY_PASSWORD_VALIDATION})

        
    error_messages = {
        'invalid_login': messages.USER_INVALID_EMAIL_PASSWORD,
        'inactive': messages.USER_ACCOUNT_NOT_ACTIVE,
        'not_verified' :messages.USER_ACCOUNT_NOT_VERIFIED
    }

    class Meta:
        model = User
        fields = ('email', 'password')

    def __init__(self, request=None, *args, **kwargs):
        '''
        Initiatizes form with request and user_cache objects
        '''
        self.request = request
        self.user_cache = None
        super(LoginForm, self).__init__(*args, **kwargs)
        user_model = get_user_model()
        self.username_field = user_model._meta.get_field(
            user_model.USERNAME_FIELD)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            user_model = get_user_model()
            try:
                user = user_model._default_manager.get(email__iexact=email)
                if user.check_password(password):
                    self.user_cache = user
                if user.is_superuser or user.is_staff:
                    self.user_cache = None
            except user_model.DoesNotExist:
                self.user_cache = None
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'email': self.username_field.verbose_name},
                )
            # elif not self.user_cache.is_verified:
            #     raise forms.ValidationError(
            #         self.error_messages['not_verified'],
            #         code="not_active")
            else:
                self.confirm_login_allowed(self.user_cache)
        flash_messages.success(
            self.request,
            messages.LOGIN_SUCCESSFULL
             )      
        return self.cleaned_data 

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

class PersonalInfoForm(forms.ModelForm):
    """A form for creating Registered users personal details"""

    profile_photo = forms.ImageField(required=True)
    phone_number = forms.IntegerField(required=True)
    about_me = forms.CharField(min_length= 50, required=True)
    ig_username = forms.CharField(required=True)
    twitter_handle = forms.CharField(required=False)
    occupation = forms.CharField(required=True)
    country = forms.CharField(required=False)
    city = forms.CharField(required = False)

    class Meta:
        model = User
        fields = ('profile_photo','phone_number', 'about_me', 'ig_username', 'twitter_handle', 'occupation', 'country', 'city') 

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(PersonalInfoForm, self).__init__(*args, **kwargs)

    
    def save(self):
        
        user = User.objects.get(id=self.request.user.id)
        user.profile_photo = self.cleaned_data.get('profile_photo')
        user.phone_number = self.cleaned_data.get('phone_number')
        user.about_me = deEmojify(self.cleaned_data.get('about_me'))
        user.ig_username = deEmojify(self.cleaned_data.get('ig_username'))
        user.twitter_handle = deEmojify(self.cleaned_data.get('twitter_handle'))
        user.occupation = deEmojify(self.cleaned_data.get('occupation'))
        user.country = self.cleaned_data.get('country')
        user.city = self.cleaned_data.get('city')
        user.profile_added = True
        user.save()
        try:
            save_contract = ContractsModel.objects.get(created_with_email=user.email)
            print(save_contract)
            if save_contract:
                save_contract.created_with = user
                save_contract.save()
        except:
            pass
        return self


class ForgotPasswordRequestForm(forms.Form):
    '''
    Forgot password form
    '''
    email = forms.EmailField(
        label=("Email"),
        required=True,
        error_messages={
            'required': messages.FIELD_REQUIRED,
            'invalid': messages.FORGOT_PASSWORD_INVALID_EMAIL
        })

    def __init__(self, request=None, *args, **kwargs):
        self._token = None
        self._user_cache = None
        self.request = request

        super(ForgotPasswordRequestForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        '''
        Validate Email
        '''
        user_model = get_user_model()
        try:
            self._user_cache = user_model.objects.get(
                email__iexact=self.cleaned_data['email'])
            email=self.cleaned_data['email']
            success_message= messages.PASSWORD_RESET_MAIL_SUCCESS % {'email':email}
            flash_messages.success(
            self.request,
             success_message
             )            
            if not self._user_cache.is_active:
                raise forms.ValidationError(messages.USER_ACCOUNT_NOT_ACTIVE)
        except user_model.DoesNotExist :
            email=self.cleaned_data['email']
            flash_messages.success(
                self.request,
                messages.PASSWORD_RESET_MAIL_SUCCESS % {'email':email}
            )
            raise forms.ValidationError('')
        return self.cleaned_data['email']

    def save(self):
        '''
        Saves the current instance by controlling the saving process.
        '''
        self._token = UserSecurityToken.create_forgot_password_token(
            self._user_cache)
        emailtype = 'updated-password-confirmation.html'
        self._token.send_forgot_password_email(self.request, emailtype)
        self.request.session['forgot_email'] = self._user_cache.email
        return self

    def get_encoded_token(self):
        return self._token.encoded_token


class ResetPasswordForm(forms.Form):
    '''
    Reset password form
    '''
    error_messages = {'password_mismatch': messages.PASSWORD_MISMATCH_FIELDS}

    password = forms.CharField(
        label=('Password'),
        validators=[
            validate_password,
        ])

    confirm_password = forms.CharField(
        label=('Confirm Password'),
        )

    class Meta(object):
        model = get_user_model()
        fields = ('password', 'confirm_password')

    def __init__(self, request=None, token=None, *args, **kwargs):
        self._token_cache = token
        self.request = request
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        '''
        Validate Password
        '''
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')
        if (password1 and password2) and (password1 != password2):
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return self.cleaned_data



    def save(self):
        '''
        Saves the current instance by controlling the saving process.
        '''
        if not isinstance(self._token_cache, str):
            self._token_cache.user.set_password(self.cleaned_data['password'])
            self._token_cache.expire_date = timezone.now()
            self._token_cache.user.is_verified = True
            self._token_cache.user.save()
            self._token_cache.expire_date = timezone.now()
            self._token_cache.user.save()
            self._token_cache.save()

        return self

class SendCoverLetterForm(forms.Form):
    email = forms.EmailField(label=("Email"),
                             required=True,
                             error_messages={
                                 'required': messages.USER_EMPTY_EMAIL_VALIDATION,
                                 'invalid': messages.INVALID_EMAIL_ADDRESS})    
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(SendCoverLetterForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        user = User.objects.get(email=self.cleaned_data.get('email'))
        Email(self.cleaned_data.get('email'), messages.SUBJECT_ACCOUNT_ACTIVATION).message_from_template('accounts/email/send_cover_letter.html',
                                                                                {'first_name': user.first_name,
                                                                                'last_name': user.last_name,
                                                                                'user_email': self.request.user.email, 
                                                                                'cover_letter': self.request.user.cover_letter},
                                                                                self.request).send()
        return self  


class SendReferenceEmailForm(forms.Form):
    email = forms.EmailField(label=("Email"),
                             required=True,
                             error_messages={
                                 'required': messages.USER_EMPTY_EMAIL_VALIDATION,
                                 'invalid': messages.INVALID_EMAIL_ADDRESS})    
    
    name = forms.CharField(label=("Name"),
                             required=True,
                             error_messages={
                                 'required': "The Reference Name is required"})

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(SendReferenceEmailForm, self).__init__(*args, **kwargs)
    def save(self, commit=True):
        user = User.objects.get(id=self.request.user.id)
        reference_request_id = ReferenceRequestId.objects.create(name = self.cleaned_data.get('name'), 
                                email=self.cleaned_data.get('email'), user=user)
        link = settings.SITE_URL + '/accounts/add_reference/' + str(reference_request_id.pk)
        Email(self.cleaned_data.get('email'), 'Reference on Justeece.com').message_from_template('accounts/email/reference.html',
                                                                                {'reference_name': self.cleaned_data.get('name'),
                                                                                'user_first_name': self.request.user.first_name,
                                                                                'user_last_name': self.request.user.last_name,
                                                                                'user_email': self.request.user.email,
                                                                                'link': link},
                                                                                self.request).send()
        return self  

class ReferenceForm(forms.ModelForm):
    """A form for creating Registered users personal details"""

    profile_photo = forms.ImageField(required=True)
    phone_number = forms.IntegerField(required=True)

    class Meta:
        model = Reference
        fields = ( 'profile_photo','phone_number',) 
