from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm as AuthPasswordResetForm,
    SetPasswordForm as AuthSetPasswordForm,
    UserCreationForm,
)

from core.forms import StyledFormMixin

User = get_user_model()


class SignUpForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'you@example.com', 'autocomplete': 'email'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'})
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username', 'autocomplete': 'username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password', 'autocomplete': 'new-password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm password', 'autocomplete': 'new-password'}),
        }


class LoginForm(StyledFormMixin, AuthenticationForm):
    username = forms.CharField(
        label='Email',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )


class UserProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-file-input'}),
        }


class StyledPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    old_password = forms.CharField(
        label='Old password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Enter current password', 'autofocus': True}),
    )
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Enter new password'}),
    )
    new_password2 = forms.CharField(
        label='New password confirmation',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm new password'}),
    )


class StyledPasswordResetForm(StyledFormMixin, AuthPasswordResetForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
            'autofocus': True,
        })
    )


class StyledSetPasswordForm(StyledFormMixin, AuthSetPasswordForm):
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Enter new password', 'autocomplete': 'new-password'}),
    )
    new_password2 = forms.CharField(
        label='New password confirmation',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm new password', 'autocomplete': 'new-password'}),
    )
