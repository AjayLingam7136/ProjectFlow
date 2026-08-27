from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import StyledPasswordChangeForm, StyledPasswordResetForm, StyledSetPasswordForm

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('theme/', views.ThemeToggleView.as_view(), name='theme_toggle'),

    # Password management
    path('password-change/', auth_views.PasswordChangeView.as_view(
        form_class=StyledPasswordChangeForm,
        template_name='accounts/password_change.html',
        success_url='/accounts/password-change/done/',
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        form_class=StyledPasswordResetForm,
        template_name='accounts/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        form_class=StyledSetPasswordForm,
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
