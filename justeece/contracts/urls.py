"""justeece URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from contracts.views import *

app_name = 'contracts'

urlpatterns = [
    path('', ContractsLandingPageView.as_view(), name='contract-landing-page'),
    path('create_contract', CreateContractView.as_view(), name='create-contract'),
    path('create_contract_type/', CreateContractTypeView.as_view(), name='create-contract-type'),
    path('render_contract_type/',CreateContractTypeView.as_view(), name='render-contract'),
    # path('edit_contract/<int:contract_id>', CreateContractView.as_view(), name='edit-contract'),
    path('edit_contract/<int:contract_id>', EditContractView.as_view(), name='edit-contract'),
    path('contract_confirmation/<int:contract_id>', ContractConfirmationView.as_view(), name='contract-confirmation'),
    path('contract_completion/', ContractCompletionView.as_view(), name='contract-completion'),
    path('successview/', SuccessView.as_view(), name='successview'),
    path('submit_contract/<int:contract_id>', SubmitContract.as_view(), name='submit-contract'),
    path('contracts/', MyContractsView.as_view(), name='my-contracts'),
    path('contract_detail/<int:id>', ContractDetailView.as_view(), name='contract-detail'),
    path('update_contract/<int:id>', UpdateContractView.as_view(), name='update-contract'),
    path('contract_template/', TemplateContractView.as_view(), name='contract-template'),
    path('cancel_complete_contract/<int:id>', CancelCompleteContractView.as_view(), name='cancel-complete-contract'),
    path('search/', TemplateContractSearchView.as_view(), name='templatesearch'),
]
