from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Vue temporaire pour la page d'accueil
def accueil(request):
    return HttpResponse("""
        <h1>Bienvenue sur Immo.bf !</h1>
        <p>Votre site Django est en ligne avec succès 🎉</p>
        <hr>
        <p><a href='/admin/'>Administration</a></p>
    """)

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('', accueil),  # Page d'accueil
    path('health-check/', health_check),  # Pour Render
    path('admin/', admin.site.urls),  # Interface admin
    # path('', include('immobilier.urls')),  # Décommentez quand vos URLs sont prêtes
]