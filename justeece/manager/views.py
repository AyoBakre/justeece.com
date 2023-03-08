from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import User, Reference, ReferenceRequestId, ProfileViewModel
from contracts.models import ContractsModel
from app.models import AllSearches
from datetime import datetime, timedelta


def statistics(request):
    if request.user.is_staff:
        fully_registered = User.objects.filter(profile_added=True).count
        partly_registered = User.objects.filter(profile_added=False).count 
        fully_registerted_with_references = Reference.objects.all().count
        #contract_activities = ContractsModel.objects.all()
        references = Reference.objects.all()
        references_requested = ReferenceRequestId.objects.all()
        all_searches = AllSearches.objects.all()
        all_searches = reversed(all_searches)
        users = User.objects.all().order_by('-id')[:5]
        profile_views = ProfileViewModel.objects.all()
        context = {'fully_registered': fully_registered, 
                    'partly_registered': partly_registered, 
                    'fully_registerted_with_references': fully_registerted_with_references,
                    #'contract_activities': contract_activities, 
                    'references': references,
                    'references_requested': references_requested,
                    'all_searches': all_searches, 'users': users, 'profile_views':profile_views }

        return render(request, 'manager/statistics.html', context)

    else:
        return HttpResponse("Error, You do not have permission to view this page.")
