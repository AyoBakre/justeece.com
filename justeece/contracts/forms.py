import datetime
from django import forms
from django.forms import ModelChoiceField
from django.urls import reverse_lazy
from django.contrib import messages as flash_messages
from contracts.models import ContractsModel, ContractTypeModel, ContractCloseFeedback, CancelContractReasonChoiceModel, \
    RejectContractReasonChoiceModel, EndContractReasonChoiceModel
from app.email import Email
from contracts import messages

class CreateContractForm(forms.ModelForm):
   
    class Meta:
        model = ContractsModel

        fields = ['contract_name', 'created_by', 'contract_type', 
        'subcategory', 'contract_start_date','contract_end_date', 
        'summary', 'payment_included', 'amount', 'created_with_email']

    def __init__(self, request=None, user=None, contract=None, *args, **kwargs):
        super(CreateContractForm, self).__init__(*args, **kwargs)
        
        self.fields['contract_type'].queryset = ContractTypeModel.objects.all()
    #     self.request = request
        # self.user = user
        # self.contract = contract
        self.fields['contract_type'].empty_label = None

    # def clean_created_by(self):
    #     created_by = User.objects.get(id=self.user.id)
    #     return created_by

    # def clean(self):
    #     cleaned_data = super(CreateContractForm, self).clean()
    #     if cleaned_data['contract_end_date'] < cleaned_data['contract_start_date']:
    #         self.add_error('contract_start_date', "Contract's end date cannnot be greater than the start date. ")
    #     return cleaned_data

    # def save(self):
    #     if self.contract:
    #         ContractsModel.objects.filter(id=self.contract.id).update(**self.cleaned_data)
    #     else:
    #         ContractsModel.objects.create(**self.cleaned_data)
    #     return self
    
class CreateContractTypeForm(forms.ModelForm):
   
    name = forms.CharField(required=True)
    
    class Meta:
        model = ContractTypeModel
        fields = ['name']

class UpdateContractForm(forms.ModelForm):
    cancel_contract_reason = ModelChoiceField(queryset=CancelContractReasonChoiceModel.objects, empty_label=None, required=False)
    reject_contract_reason = ModelChoiceField(queryset=RejectContractReasonChoiceModel.objects, empty_label=None, required=False)
    end_contract_reason = ModelChoiceField(queryset=EndContractReasonChoiceModel.objects, empty_label=None, required=False)
    
    class Meta:
        model = ContractCloseFeedback
        fields = "__all__"
    
    def __init__(self, contract_id=None, request=None, *args, **kwargs):
        self.contract_id = contract_id
        self.request = request
        self.contract = ContractsModel.objects.filter(id=self.contract_id)
        super(UpdateContractForm, self).__init__(*args, **kwargs)

    def save(self):        
        update_to = self.request.GET.get('update')
        self.cleaned_data['contract'] = self.contract[0]
        contract_detail = reverse_lazy('contracts:contract-detail', kwargs={'id':self.contract[0].id})
        contract_detail = '%s://%s/%s' % (self.request.scheme, self.request.get_host(), contract_detail[1:])
        if self.request.method == 'POST':
            if update_to == 'reject':
                status = ContractsModel.REJECTED
                self.contract.update(status=status)
            elif update_to == 'accept':
                status = ContractsModel.IN_PROGRESS
                self.contract.update(status=status)
            elif update_to == 'cancel':
                status = ContractsModel.CANCELED
                self.contract.update(status=status)
            elif update_to == 'end':
                status = ContractsModel.COMPLETED
                self.contract.update(status=status, contract_completed_date=datetime.datetime.now())
        Email(self.contract[0].created_by.email, messages.CONTRACT_STATUS_UPDATED).message_from_template('contracts/email/contract_status_updated.html',
                                                                        {'first_name': self.contract[0].created_by.first_name,
                                                                        'last_name': self.contract[0].created_by.last_name,
                                                                        'contract_name': self.contract[0].contract_name,
                                                                        'created_with_email': self.contract[0].created_with.email,
                                                                        'status': self.contract[0].get_status_display(),
                                                                        'comment': self.cleaned_data.get('feedback'),
                                                                        'contract_detail': contract_detail},
                                                                        self.request).send()
        flash_messages.success(
            self.request,
            messages.CONTRACT_STATUS_UPDATED
        )    
        return super().save()


class TemplateContractSearchForm(forms.Form):
    search = forms.CharField(required=False)
