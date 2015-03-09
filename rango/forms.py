from django import forms
from rango.models import Page, Category, UserProfile
from django.contrib.auth.models import User

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name',)


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.CharField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    
    def clean(self):
        return fixURL(self, 'url')

    class Meta:
        model = Page
        fields = ('title', 'url')


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    website = forms.CharField()
    
    def clean(self):
        return fixURL(self, 'website')
        
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')


# Formats a given URL string.
def fixURL(self, name):
    cleaned_data = self.cleaned_data
    url = cleaned_data.get(name)

    if url and not url.startswith('http://'):
        url = 'http://' + url
        cleaned_data[name] = url

    return cleaned_data