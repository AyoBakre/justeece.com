from django.contrib import admin
from accounts.models import User,CountryModel,CityModel,LanguageModel,OurPartner, Reference
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'email', 'profile_added', 'occupation', 'country', 
                    'city', 'phone_number', 'ig_username', 'is_verified', 'subscribed']



admin.site.register(User, UserAdmin)
admin.site.register(CountryModel)
admin.site.register(CityModel)
admin.site.register(LanguageModel)
admin.site.register(OurPartner)
admin.site.register(Reference)
