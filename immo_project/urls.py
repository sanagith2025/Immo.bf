from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from immobilier.models import Utilisateur  # AJOUTÉ

def home(request):
    return HttpResponse("""
        <h1>Bienvenue sur Immo.bf !</h1>
        <p>Votre site Django est en ligne avec succès !</p>
        <p><a href="/admin/">Acceder a l'administration</a></p>
    """)

def health_check(request):
    return HttpResponse("OK")

# AJOUTÉ - Fonction pour créer un superutilisateur
def create_admin(request):
    email = "admin@immo.bf"
    password = "admin123"
    
    if not Utilisateur.objects.filter(email=email).exists():
        Utilisateur.objects.create_superuser(
            email=email, 
            password=password, 
            nom='Admin', 
            prenom='Super'
        )
        return HttpResponse(f"✅ Superutilisateur {email} créé avec succès !<br><a href='/admin/'>Se connecter à l'admin</a>")
    else:
        return HttpResponse(f"⚠️ L'utilisateur {email} existe déjà.<br><a href='/admin/'>Se connecter à l'admin</a>")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('health-check/', health_check),
    path('create-admin/', create_admin),  # AJOUTÉ - Route temporaire
]
