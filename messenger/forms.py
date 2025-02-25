from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        help_text='Максимум 150 символов. Буквы, цифры и символы @/./+/-/_',
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}),
        help_text='Введите тот же пароль, что и выше'
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем все стандартные проверки пароля
        self.fields['password1'].help_text = ''

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'name', 'description'] 