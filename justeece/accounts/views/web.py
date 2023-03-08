from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, FormView, View
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.http import Http404
from django.db.models import Q
from django.contrib import messages as flash_messages
from accounts.models import User, CityModel, OurPartner, Reference, ReferenceRequestId, ProfileViewModel
from accounts.forms import SignupForm, LoginForm, PersonalInfoForm, SendCoverLetterForm, SendReferenceEmailForm,\
    ReferenceForm
from accounts import messages 
from app.decorators import anonymous_view
from app.decorators import anonymous_only,anonymous_view, logged_user_view
from app.forms import TestimonialForm
from app.models import TestimonialModel
from contracts.models import ContractsModel, ContractCloseFeedback
from django.shortcuts import render, redirect
from app.email import Email
# Create your views here.


@anonymous_view()
class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:email_verification_confirmation')


    def get_form_kwargs(self):
        ''' Form Initialize '''
        data = super(SignupView, self).get_form_kwargs()
        data.update({'request': self.request})
        return data
    
    def get_context_data(self, **kwargs):
        '''get context '''
        context = super(SignupView, self).get_context_data(**kwargs)
        return context

@anonymous_view()
class LoginView(FormView):
    '''Login view '''
    
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next_url')
        if next_url:
            return next_url
        if self.request.user.profile_added == False:
            return reverse_lazy( 'accounts:personal-details')
        elif Reference.objects.filter(reference_for_id=self.request.user).count() < 1:
            return reverse_lazy( 'accounts:send-reference-email')
        else: 
            return reverse_lazy( 'accounts:dashboard')

    def get_form_kwargs(self):
        '''update form args '''
        data = super(LoginView, self).get_form_kwargs()
        request = self.request
        data.update({'request': request})
        return data

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        if self.request.method=="POST":
            form = LoginForm(self.request.POST)
            if form.is_valid:
                context['email'] = self.request.POST['email']
        return context

    def form_valid(self, form):
        user = form.get_user()
        if form.is_valid():
            try:
                auth_login(self.request, user,backend='django.contrib.auth.backends.ModelBackend')
                response = super(LoginView, self).form_valid(form)
                return response
            except Exception:
                pass

@anonymous_view()
class EmailVerificationConfirmationLinkView(TemplateView):
    """
    View shows success page post successful user sign up.
    """
    
    template_name   = 'accounts/email/email-verification-confirmation-link.html'
    
    def get_context_data(self, **kwargs):
        context = super(EmailVerificationConfirmationLinkView, self).get_context_data(**kwargs)
        try:
            context['email'] = self.request.session['user_email']
        except Exception:
            raise Http404()
        return context

class DashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    #function to check if user has filled profile
    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.profile_added
        else:
            return True
        
    #function to redirect if user hasn't filled profile
    def handle_no_permission(self):
        flash_messages.error(self.request, 'You have to fill in your Profile Form to get full access')  
        return redirect('accounts:personal-details')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['all_feedbacks'] = TestimonialModel.objects.all()
        #context['feedback_form'] = TestimonialForm(request=self.request)
        #context['our_partners'] = OurPartner.objects.values_list('Image_url',flat=True)
        service_providers = User.objects.filter(profile_added = True).order_by('-id')[:15]
        context['service_providers']  = service_providers
        return context

@logged_user_view(redirect_to=reverse_lazy('accounts:login'))
class ProfileView(UserPassesTestMixin, TemplateView):
    template_name = 'accounts/profile.html'

     #function to check if user has filled profile
    def test_func(self):
        return self.request.user.profile_added
        
    #function to redirect if user hasn't filled profile
    def handle_no_permission(self):
        flash_messages.error(self.request, 'You have to fill in your Profile Form to get full access')  
        return redirect('accounts:personal-details')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.GET.get('user', None)
        if not user:
            context['user'] = self.request.user
            #context['contracts_inprogress'] = ContractsModel.objects.filter(created_with=self.request.user, status=ContractsModel.IN_PROGRESS)
            #context['contracts_completed'] = ContractsModel.objects.filter(created_with=self.request.user, status=ContractsModel.COMPLETED)
            #context['contracts_canceled'] = ContractsModel.objects.filter(created_with=self.request.user, status=ContractsModel.CANCELED)
            #context['contracts_pending'] = ContractsModel.objects.filter(created_with=self.request.user, status=ContractsModel.PENDING)
            context['cover_letter'] = self.request.user.cover_letter
            #context['contracts_history'] = ContractCloseFeedback.objects.filter(contract__created_with=self.request.user)
            context['reference'] = Reference.objects.filter(reference_for_id=self.request.user)
        else:
            user = User.objects.get(id =user)
            context['user'] = user
            #context['contracts_inprogress'] = ContractsModel.objects.filter(created_with_id=user, status=ContractsModel.IN_PROGRESS)
            #context['contracts_completed'] = ContractsModel.objects.filter(created_with_id=user, status=ContractsModel.COMPLETED)
            #context['contracts_canceled'] = ContractsModel.objects.filter(created_with_id=user, status=ContractsModel.CANCELED)
            #context['contracts_pending'] = ContractsModel.objects.filter(created_with_id=user, status=ContractsModel.PENDING)
            context['cover_letter'] = user.cover_letter
            #context['contracts_history'] = ContractCloseFeedback.objects.filter(contract__created_with__id=user)
            profile_view = ProfileViewModel.objects.create(user_viewed = user, user_viewer = self.request.user)
            profile_view.send_email(self.request)
        return context

class UserListView(View):
    
    def get(self, request, data):
        try:
            user = User.objects.get(id=request.user.id)
            users = list(User.objects.filter(Q(email__icontains=data) | Q(first_name__contains=data)).exclude(email=user.email).values('id','email','first_name','last_name'))
            return JsonResponse(users, safe=False)
        except Exception as e:
            return JsonResponse({"errors":str(e)})  
        
# @logged_user_view(redirect_to=reverse_lazy('accounts:login'))
class PersonalDetailsView(FormView,TemplateView):
    
    form_class = PersonalInfoForm
    
    def get_template_names(self):
        template_name = 'accounts/personal_details.html'
        return template_name


    def get_success_url(self, *args, **kwargs):
        if Reference.objects.filter(reference_for_id=self.request.user).count() < 1:
            return reverse_lazy( 'accounts:send-reference-email')
        else:
            return reverse_lazy('accounts:profile')


    def get_form_kwargs(self):
        '''update form args '''
        data = super(PersonalDetailsView, self).get_form_kwargs()
        request = self.request
        data.update({'request': request})
        return data


    def form_invalid(self, form):
        return super(PersonalDetailsView, self).form_invalid(form)

    def form_valid(self, form):   
        flash_messages.success(
                self.request,
                messages.PROFILE_UPDATED
            )
        form.save()
        return super(PersonalDetailsView, self).form_valid(form) 

class DynamicDropdowns(View):
    '''
    To load dependency  dropdown 
    '''
    def get(self, request):
        context={}
        try:
            country_id=request.GET.get('id')
            dropdown_type=request.GET.get('dropdown_type')
            if dropdown_type=="CITY":
                context['dropdown_options'] = list(CityModel.objects.filter(country__id=country_id).values_list('id','name'))
            return JsonResponse(context)
        except Exception:
            return JsonResponse(context)

class SearchUserView(TemplateView):
    template_name = 'accounts/search_user.html'
    
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

@logged_user_view(redirect_to=reverse_lazy('accounts:login'))
class CreateCoverLetterView(View):

    def post(self, request):
        context={}
        try:
            User.objects.filter(email=self.request.user.email).update(
                cover_letter=request.POST.get('cover_letter'),
            )
            context['status'] = 'SUCCESS' 
            return JsonResponse(context)
        except Exception:
            context['status'] = 'FAILURE'
            return JsonResponse(context)

    def get(self, request):
        return render(request, 'accounts/cover_letter.html')

class SendCoverLetterView(FormView):
    form_class = SendCoverLetterForm
    template_name = 'accounts/profile.html'

    def get_form_kwargs(self):
        ''' Form Initialize '''
        data = super(SendCoverLetterView, self).get_form_kwargs()
        data.update({'request': self.request})
        return data

    def form_invalid(self, form):
        return super(SendCoverLetterView, self).form_invalid(form)

    def form_valid(self, form):   
        form.save()
        return super(SendCoverLetterView, self).form_valid(form) 

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:profile')


class SendReferenceEmailView(FormView):
    form_class = SendReferenceEmailForm
    template_name = 'accounts/add_reference.html'

    def get_form_kwargs(self):
        ''' Form Initialize '''
        data = super(SendReferenceEmailView, self).get_form_kwargs()
        data.update({'request': self.request})
        return data

    def form_invalid(self, form):
        return super(SendReferenceEmailView, self).form_invalid(form)

    def form_valid(self, form):   
        form.save()

        return super(SendReferenceEmailView, self).form_valid(form) 

    def get_success_url(self, *args, **kwargs):
        flash_messages.success(self.request, "Your reference had been sent successfully")
        return reverse_lazy('accounts:profile')


def reference(request, id):
    form = ReferenceForm()
    reference_id = ReferenceRequestId.objects.get(pk=id)
    if request.method == 'POST':
        form = ReferenceForm(request.POST, files = request.FILES)
        try:
            if form.is_valid():
                email = reference_id.email
                profile_photo = form.cleaned_data.get('profile_photo')
                phone_number = form.cleaned_data['phone_number']
                name =  reference_id.name
                user = reference_id.user
                reference_for = user
                reference = Reference(email=email, profile_photo=profile_photo, phone_number=phone_number, name=name,
                                                reference_for=reference_for)
                reference.save()
                reference_id.reference_added = True
                context = {'email': reference_for.email}
                return render(request, 'accounts/success.html', context)
        except:
            pass
    else:
        reference_id = ReferenceRequestId.objects.get(pk=id)
        form = ReferenceForm()
    context = {'form': form, 'reference':reference_id}
    return render(request, 'accounts/reference.html', context)


def unsubscribe(request, id):
    try:
        user = User.objects.get(id=id)
        user.subscribed = False
        user.save()
        context = {'email': user.email ,'message': 'Unsubscribe successful, you would no longer receive our emails'}
        return render(request,  'accounts/unsubcribe.html', context )
        
    except:
        context = {'message': 'Error: no such account'}
        return render(request,  'accounts/unsubcribe.html', context )
        