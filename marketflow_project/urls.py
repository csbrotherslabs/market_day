from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy
from core_app import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('accounts/login/', core_views.login_view, name='login'),
    path('accounts/register/', core_views.register_view, name='register'),
    path('accounts/logout/', core_views.logout_view, name='logout'),
    path('accounts/profile/', core_views.profile_view, name='profile'),
    path(
        'accounts/password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='core_app/password_reset_form.html',
            email_template_name='core_app/password_reset_email.html',
            subject_template_name='core_app/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'accounts/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='core_app/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='core_app/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='core_app/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path('', include('core_app.urls')),
    path('buyers/', include('buyers_app.urls')),
    path('sellers/', include('sellers_app.urls')),
    path('drivers/', include('drivers_app.urls')),
    path('qa/', include('qa_app.urls')),
    path('adminops/', include('adminops_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
