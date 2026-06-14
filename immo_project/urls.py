from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def health_check(request):
    return HttpResponse("OK")


def setup_admin(request):
    try:
        from immobilier.models import Utilisateur
        if not Utilisateur.objects.filter(email='manager@immobf.bf').exists():
            Utilisateur.objects.create_user(
                email='manager@immobf.bf',
                password='Admin@2026',
                nom='Admin',
                prenom='Manager',
                role='manager',
                is_staff=True,
                is_superuser=True
            )
            return HttpResponse("""
                <!DOCTYPE html>
                <html>
                <head><meta charset='utf-8'><title>Setup</title></head>
                <body style='font-family:Arial;text-align:center;margin-top:100px;'>
                    <h2 style='color:green;'>✅ Manager créé avec succès !</h2>
                    <p><strong>Email :</strong> manager@immobf.bf</p>
                    <p><strong>Mot de passe :</strong> Admin@2026</p>
                    <br>
                    <a href='/connexion/' style='background:#1a7a4a;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;'>
                        Se connecter
                    </a>
                </body>
                </html>
            """)
        else:
            return HttpResponse("""
                <!DOCTYPE html>
                <html>
                <head><meta charset='utf-8'><title>Setup</title></head>
                <body style='font-family:Arial;text-align:center;margin-top:100px;'>
                    <h2 style='color:orange;'>⚠️ Manager existe déjà</h2>
                    <p><strong>Email :</strong> manager@immobf.bf</p>
                    <p><strong>Mot de passe :</strong> Admin@2026</p>
                    <br>
                    <a href='/connexion/' style='background:#1a7a4a;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;'>
                        Se connecter
                    </a>
                </body>
                </html>
            """)
    except Exception as e:
        return HttpResponse(f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset='utf-8'><title>Erreur</title></head>
            <body style='font-family:Arial;text-align:center;margin-top:100px;'>
                <h2 style='color:red;'>❌ Erreur : {str(e)}</h2>
                <p>Vérifiez les logs Render.</p>
            </body>
            </html>
        """)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health-check/', health_check),
    path('setup/', setup_admin),
    path('', include('immobilier.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
