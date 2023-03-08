from django.contrib import admin
from contracts.models import ContractsModel, EndContractReasonChoiceModel, RejectContractReasonChoiceModel, \
                        CancelContractReasonChoiceModel, ContractCloseFeedback, ContractTemplate, ContractTemplateTag
# Register your models here.

admin.site.register(ContractsModel)
admin.site.register(EndContractReasonChoiceModel)
admin.site.register(RejectContractReasonChoiceModel)
admin.site.register(CancelContractReasonChoiceModel)
admin.site.register(ContractCloseFeedback)
admin.site.register(ContractTemplate)
admin.site.register(ContractTemplateTag)