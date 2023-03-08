from django.contrib import admin
from contracts.models import ContractTypeModel
from app.models import TestimonialModel, MaillMessage
# Register your models here.

admin.site.register(ContractTypeModel)
admin.site.register(TestimonialModel)
admin.site.register(MaillMessage)