from django import forms
from .models import User, Profile
from django.contrib.auth.models import User

class SimpleRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ["username"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user 

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'avatar', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        } 