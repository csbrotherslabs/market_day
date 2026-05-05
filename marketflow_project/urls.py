from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from core_app import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('accounts/login/', core_views.login_view, name='login'),
    path('accounts/register/', core_views.register_view, name='register'),
    path('accounts/logout/', core_views.logout_view, name='logout'),
    path('accounts/profile/', core_views.profile_view, name='profile'),
    path('buyers/', include('buyers_app.urls')),
    path('sellers/', include('sellers_app.urls')),
    path('drivers/', include('drivers_app.urls')),
    path('qa/', include('qa_app.urls')),
    path('adminops/', include('adminops_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
