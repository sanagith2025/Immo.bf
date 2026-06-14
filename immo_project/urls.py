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

def setup_admin(request):
    """Fonction autonome pour créer l'administrateur"""
    try:
        from immobilier.models import Utilisateur
        email = "admin@immo.bf"
        password = "admin123"
        
        if not Utilisateur.objects.filter(email=email).exists():
            Utilisateur.objects.create_superuser(
                email=email,
                password=password,
                nom='Admin',
                prenom='Super'
            )
            return HttpResponse("""
                <h2 style="color:green;">✅ Admin créé avec succès !</h2>
                <p>Email: <strong>admin@immo.bf</strong></p>
                <p>Mot de passe: <strong>admin123</strong></p>
                <p><a href="/admin/">Se connecter</a></p>
            """)
        else:
            return HttpResponse("""
                <h2>⚠️ Admin existe déjà</h2>
                <p><a href="/admin/">Se connecter</a></p>
            """)
    except Exception as e:
        return HttpResponse(f"""
            <h2 style="color:red;">❌ Erreur: {str(e)}</h2>
            <p>Vérifiez que la table existe.</p>
        """)

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('health-check/', health_check),
    path('setup/', setup_admin),  # Nouvelle route plus courte
]
