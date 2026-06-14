from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def health_check(request):
    return HttpResponse("OK")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health-check/', health_check),
    path('', include('immobilier.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
