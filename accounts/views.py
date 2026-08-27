import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView

from .forms import LoginForm, UserProfileForm

User = get_user_model()


class LoginView(AuthLoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().get_short_name() or form.get_user().username}!')
        return super().form_valid(form)


class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('accounts:login')
    http_method_names = ['get', 'post', 'options']

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)


class ThemeToggleView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False}, status=400)

        theme = data.get('theme', 'dark')
        valid_themes = [c[0] for c in User.THEME_CHOICES]
        if theme not in valid_themes:
            theme = 'dark'

        request.user.theme_preference = theme
        request.user.save(update_fields=['theme_preference'])
        return JsonResponse({'success': True, 'theme': theme})
