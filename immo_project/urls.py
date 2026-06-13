from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello World! Django fonctionne!")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
]
