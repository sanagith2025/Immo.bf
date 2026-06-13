from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
        <h1>Bienvenue sur Immo.bf !</h1>
        <p>Votre site Django est en ligne avec succès !</p>
        <p><a href="/admin/">Acceder a l'administration</a></p>
    """)

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('health-check/', health_check),
]