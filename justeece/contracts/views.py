import datetime
from django.http.response import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView
from django.urls import reverse_lazy
from app.decorators import logged_user_view, PermissionRequiredMixin
from accounts.models import User
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from contracts.forms import CreateContractForm, CreateContractTypeForm
from contracts.models import ContractsModel,ContractTypeModel, ContractTemplate, ContractTemplateTag
from contracts.forms import UpdateContractForm, TemplateContractSearchForm
from app.email import Email
from contracts import messages
from django.db.models import Q
from django.contrib import messages as flash_messages
from django.http import HttpResponseRedirect
import pprint
# Create your views here.

class CreateContractTypeView(CreateView):

    form_class = CreateContractTypeForm
    template_name = 'contracts/contract_type.html'
    
    def get_success_url(self):
        return reverse_lazy( 'contracts:successview') 
    
class SuccessView(TemplateView):
    
    template_name = 'contracts/success.html'

class RenderContractType(TemplateView):
    
    template_name = 'contract'

class SubmitContract(View):
    
    def get(self,request,**args):
        try:
            contract_id = self.kwargs['contract_id']
            
            contract = ContractsModel.objects.get(id=contract_id)
            contract.status = ContractsModel.PENDING
            contract.save()
            contract_detail = reverse_lazy('contracts:contract-detail', kwargs={'id':contract.id})
            contract_detail = '%s://%s/%s' % (request.scheme, request.get_host(), contract_detail[1:])
            Email(contract.created_with_email, messages.NEW_CONTRACT_REQUEST).message_from_template('contracts/email/new_contract_request.html',
                                                                    {'contract_created_by': self.request.user.email,
                                                                    'contract_detail': contract_detail,
                                                                    'first_name': contract.created_by.first_name,
                                                                    'last_name': contract.created_by.last_name},
                                                                    request).send()
            return render(request,'contracts/contract_completion.html',{"email":contract.created_with_email})  
        except Exception as e:
            return render(request,'accounts/error.html')

class CreateContractView(View):
    
    def get(self,request,**args):
        try:
            search = request.GET.get('search')
            user_id = None
            form = CreateContractForm
            if search:
                user = User.objects.filter(email=search)
                if user:
                    user_id = user[0].id
            else:
                return render(request, 'accounts/dashboard.html')
            contracts_type = list(ContractTypeModel.objects.all().values('id','name'))
            return render(request,'contracts/create_contract.html',{"email":search,user_id:user_id, "contract_type":contracts_type,"form":form})  
        except Exception as e:
            return render(request,'contracts/create_contract.html') 
    
    
    def post(self, request):
        
        try:
            tempdict = self.request.POST.copy()
            tempdict['created_by'] = request.user.id
            
            form = CreateContractForm(tempdict)
      
            if 'payment_included' in tempdict:
                payment_included = tempdict.get('payment_included')
            else:
                payment_included = False

            if 'amount' in tempdict:
                if tempdict.get('amount') =='':
                    amount = 0
                else:
                    amount = tempdict.get('amount')
            else:
                amount = 0

            contaract_type_id = ContractTypeModel.objects.get(name=tempdict.get('contract_type'))
            instance                = form.save(commit=False)
            instance.created_by     = User.objects.get(id=request.user.id)
            instance.contract_type  = contaract_type_id
            instance.contract_name           = tempdict.get('contract_name')
            instance.contract_start_date     = tempdict.get('contract_start_date')
            instance.contract_end_date       = tempdict.get('contract_end_date') 
            instance.summary                 = tempdict.get('summary')
            instance.amount                  = amount
            instance.payment_included        = payment_included
            instance.status                  = ContractsModel.DRAFT
            instance.created_with            = User.objects.get(email=tempdict.get('created_with'))
            instance.subcategory             = tempdict.get('subcategory')
            instance.save()
            tempdict['id']      = instance.id
            tempdict['status']  = ContractsModel.DRAFT
            tempdict['created_with'] = instance.created_with
            send_data = {"contract":tempdict}
            return render(request,'contracts/contract_confirmation.html',send_data)  
        except Exception as e:
            print(str(e))
            return render(request,'contracts/create_contract.html')  

class EditContractView(View):
    
    def get(self,request,**kwargs):
        try:
            contract_id = self.kwargs['contract_id']
            contract = ContractsModel.objects.get(id=contract_id)
            contracts_type = list(ContractTypeModel.objects.all().values('id','name'))
            data = {
                "email"         :contract.created_with.email,
                "contract_type" :contract.contract_type.name,
                "subcategory"   :contract.subcategory,
                "contract_start_date":contract.contract_start_date,
                "contract_end_date"  :contract.contract_end_date,
                "summary"       : contract.summary,
                "payment_included": contract.payment_included,
                "amount"          : contract.amount
            }
            form = CreateContractForm(initial=data)
           
            return render(request,'contracts/create_contract.html',{"email":data["email"],"selected_contract":data["contract_type"],"contract_type":contracts_type, "form":form})  
        except Exception as e:
            return render(request,'contracts/create_contract.html') 

class ContractConfirmationView(TemplateView):
    template_name = 'contracts/contract_confirmation.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        contract = ContractsModel.objects.get(id=self.kwargs['contract_id'])
        try:
            context['contract'] = contract
        except:
            pass
        return context

class ContractCompletionView(TemplateView):
    template_name = 'contracts/contract_completion.html'


@logged_user_view(redirect_to=reverse_lazy('accounts:login'))
class MyContractsView(UserPassesTestMixin, TemplateView):
    template_name = 'contracts/contracts.html'

     #function to check if user has filled profile
    def test_func(self):
        return self.request.user.profile_added
        
    #function to redirect if user hasn't filled profile
    def handle_no_permission(self):
        flash_messages.error(self.request, 'You have to fill in your Profile Form to get full access')  
        return redirect('accounts:personal-details')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_contracts = ContractsModel.objects.all()
        context['contracts_provider'] = all_contracts.filter(created_with=self.request.user).exclude(status=ContractsModel.DRAFT).order_by('-create_date')
        context['contracts_client'] = all_contracts.filter(created_by=self.request.user).exclude(status=ContractsModel.DRAFT).order_by('-create_date')
        return context

@logged_user_view(redirect_to=reverse_lazy('accounts:login'))
class ContractDetailView(PermissionRequiredMixin, TemplateView):
    template_name = "contracts/contract_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['contract'] = ContractsModel.objects.get(id=kwargs['id'])
        except:
            return Http404
        return context

class UpdateContractView(FormView):
    form_class = UpdateContractForm

    def get_template_names(self):
        if self.request.is_ajax():
            if self.request.method == 'GET':
                action_key = self.request.GET.get('action_key')
                if action_key == 'accept-contract':
                    return 'contracts/partials/accept_contract_partials.html'
                elif action_key == 'reject-contract':
                    return 'contracts/partials/reject_contract_partials.html'
                elif action_key == 'cancel-contract':
                    return 'contracts/partials/cancel_contract_partials.html'
                else:
                    return 'contracts/partials/end_contract_partials.html'
        else:
            return 'contracts/contracts.html'

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_contracts = ContractsModel.objects.all()
        contract = all_contracts.filter(id=self.kwargs['id'])
        context['contracts_pending'] = ContractsModel.objects.filter(created_with=self.request.user, status=ContractsModel.PENDING)
        context['contracts_provider'] = all_contracts.filter(created_with=self.request.user).exclude(status=ContractsModel.DRAFT)
        context['contracts_client'] = all_contracts.filter(created_by=self.request.user).exclude(status=ContractsModel.DRAFT)
        context['contract'] = contract.first()
        return context
    
    def get_form_kwargs(self):
        ''' Form Initialize '''
        data = super(UpdateContractView, self).get_form_kwargs()
        data.update({'contract_id': self.kwargs['id'], 'request': self.request})
        return data

    def form_valid(self, form):   
        form.save()
        return super(UpdateContractView, self).form_valid(form) 

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:dashboard')


@logged_user_view(redirect_to=reverse_lazy('accounts:login'))
class TemplateContractView(UserPassesTestMixin, View):
    
    #function to check if user has filled profile
    def test_func(self):
        return self.request.user.profile_added
        
    #function to redirect if user hasn't filled profile
    def handle_no_permission(self):
        flash_messages.error(self.request, 'You have to fill in your Profile Form to get full access')  
        return redirect('accounts:personal-details')

    def get(self, request, **args):
        form = CreateContractForm
        all_contract_templates = ContractTemplate.objects.all()
        all_contract_template_tags = ContractTemplateTag.objects.all()
        context = dict()
        context['contract_templates'] = all_contract_templates
        context['contract_template_tags'] = all_contract_template_tags
        return render(request, 'contracts/contract_templates.html', context)
    
    
    def post(self, request):

        try:
            tempdict = self.request.POST.copy()
            tempdict['created_by'] = request.user.id
            form = CreateContractForm(tempdict)
            payment_included = False
            amount = tempdict.get('amount')
            template_contract = ContractTemplate.objects.get(title=tempdict.get('contract_name'))   
            contaract_type_id = template_contract.contract_type
            contract_tags = template_contract.tag
            
            instance = form.save(commit=False)
            instance.created_by = User.objects.get(id=request.user.id)
            instance.contract_type = contaract_type_id
            instance.contract_name = tempdict.get('contract_name')
            instance.contract_start_date = tempdict.get('contract_start_date')
            instance.contract_end_date = tempdict.get('contract_end_date') 
            instance.summary = tempdict.get('summary')
            instance.amount = amount
            instance.payment_included = payment_included
            instance.status = ContractsModel.DRAFT
            instance.created_with_email = tempdict.get('created_with_email')
            try:
                if User.objects.get(email= instance.created_with_email):
                    instance.created_with = User.objects.get(email=tempdict.get('created_with_email'))
            except:
                pass
            instance.subcategory = contract_tags
            instance.save()
            tempdict['id']      = instance.id
            tempdict['status']  = ContractsModel.DRAFT
            tempdict['created_with_email'] = instance.created_with_email
            tempdict['contract_type'] = instance.contract_type
            send_data = {"contract":tempdict}
            return render(request,'contracts/contract_confirmation.html',send_data)  
        except Exception as e:
            print(e)
            flash_messages.error(self.request, "There was an error while creating your contract" + ' --- ' + str(e))
            return redirect('contracts:contract-template')
           

@logged_user_view(redirect_to=reverse_lazy('accounts:login'))
class ContractsLandingPageView(UserPassesTestMixin, TemplateView):
    template_name = 'contracts/contract_landing.html'

     #function to check if user has filled profile
    def test_func(self):
        return self.request.user.profile_added
        
    #function to redirect if user hasn't filled profile
    def handle_no_permission(self):
        flash_messages.error(self.request, 'You have to fill in your Profile Form to get full access')  
        return redirect('accounts:personal-details')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TemplateContractSearchView(FormView):
    template_name = 'contracts/contract_template_search.html'
    form_class = TemplateContractSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:    
            search = self.request.GET['search']
            context['contract_templates'] = ContractTemplate.objects.filter(
                Q(title__icontains=search))
            context['template_search_term'] = search
            all_contract_template_tags = ContractTemplateTag.objects.all()
            context['contract_template_tags'] = all_contract_template_tags
            return context
        except:
            # Define exception later and rework code
            search = self.request.GET['searc']
            search = ContractTemplateTag.objects.get(pk=search)
            context['template_search_term'] = search
            search = search.contracttemplate_set.all()
            context['contract_templates'] = search
            all_contract_template_tags = ContractTemplateTag.objects.all()
            context['contract_template_tags'] = all_contract_template_tags
            return context


class CancelCompleteContractView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            contract = ContractsModel.objects.get(id=self.kwargs.get('id'))
        except:
            raise Http404
        context['contract'] = contract
        return context

    def get_template_names(self):
        contract = ContractsModel.objects.get(id=self.kwargs.get('id'))
        status = contract.status
        if status == ContractsModel.COMPLETED:
            template_name = 'contracts/contract_ended.html'
        elif status == ContractsModel.CANCELED:
            template_name = 'contracts/contract_cancelled.html'
        else:
            template_name = 'contracts/contract_detail.html'
        
        return template_name
