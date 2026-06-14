from django.core.management.base import BaseCommand
from immobilier.models import Utilisateur


class Command(BaseCommand):
    help = 'Crée le compte manager initial'

    def handle(self, *args, **kwargs):
        email = 'manager@immobf.bf'
        password = 'Admin@2026'

        if not Utilisateur.objects.filter(email=email).exists():
            Utilisateur.objects.create_user(
                email=email,
                password=password,
                nom='Admin',
                prenom='Manager',
                role='manager',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS('✅ Manager créé avec succès !')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Manager existe déjà.')
            )
