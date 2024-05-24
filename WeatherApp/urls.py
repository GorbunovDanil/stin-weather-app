from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from weather.views import logout_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/current-weather/', permanent=True)),  # Redirect root URL to /current-weather/
    path('', include('weather.urls')),  # Include weather URLs
    path('api/', include('weather.api_urls')),  # Include API URLs separately
    path('accounts/', include('django.contrib.auth.urls')),  # Include default auth URLs
    path('accounts/logout/', logout_view, name='logout'),  # Override default logout URL
]
