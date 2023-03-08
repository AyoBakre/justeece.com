from django import forms
from app.models import TestimonialModel
from app.validations import validate_password
from app.decorators import anonymous_only, anonymous_view


class TestimonialForm(forms.ModelForm):
    
    class Meta:
        model = TestimonialModel
        fields = ('feedback', 'user')

    def __init__(self, request, *args, **kwargs):
        '''
        Init Method 

        '''
        self.request = request
        super(TestimonialForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        TestimonialModel.objects.create(feedback=self.cleaned_data['feedback'], user=self.request.user)

class SearchForm(forms.Form):
    search = forms.CharField(required=False)