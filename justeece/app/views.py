from django.shortcuts import render
from django.views.generic import View, FormView, TemplateView, CreateView
from django.http import JsonResponse
from django.contrib import messages as flash_messages
from django.urls import reverse_lazy
from django.db.models import Q
from app.forms import TestimonialForm, SearchForm
from accounts.models import User
from app.models import AllSearches
# Create your views here.



class TestimonialView(FormView):
    form_class = TestimonialForm
    template_name = "accounts/dashboard.html"
    
    def form_valid(self, form):
        flash_messages.success(self.request, "Testimonial has been added successfully")
        data = {
            'success': True
        }
        form.save()
        return JsonResponse(data)
    
    def get_form_kwargs(self):
        data = super(TestimonialView, self).get_form_kwargs()
        data.update({'request': self.request})
        return data

class SearchView(FormView):
    template_name = "app/search.html"
    form_class = SearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET['search']
        context['people'] = User.objects.filter(
            (Q(email__icontains=search)|Q(phone_number__icontains=search)|Q(occupation__icontains=search))\
             & Q(is_verified=True) 
             ).exclude(is_superuser=True)
        context['search_term'] = search
        if self.request.user.is_authenticated:
            AllSearches.objects.create(search=search, user= self.request.user)
        else:
            AllSearches.objects.create(search=search)
        return context
    
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('accounts:dashboard')

class AboutUsView(TemplateView):
    template_name = "app/aboutus.html"
    
