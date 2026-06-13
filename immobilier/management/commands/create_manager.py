from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from immobilier.models import Utilisateur
from getpass import getpass


class Command(BaseCommand):
    help = 'Crée un utilisateur avec le rôle manager'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email du manager')
        parser.add_argument('--nom', type=str, required=True, help='Nom du manager')
        parser.add_argument('--prenom', type=str, required=True, help='Prénom du manager')
        parser.add_argument('--telephone', type=str, help='Téléphone (optionnel)')
        parser.add_argument('--no-input', action='store_true', help='Mode non interactif')

    def handle(self, *args, **options):
        email = options['email']
        nom = options['nom']
        prenom = options['prenom']
        telephone = options.get('telephone', '')
        no_input = options['no_input']

        # Vérifier si l'email existe déjà
        if Utilisateur.objects.filter(email=email).exists():
            raise CommandError(f"Un utilisateur avec l'email {email} existe déjà")

        # Demander le mot de passe
        if no_input:
            password = 'manager123'  # Mot de passe par défaut
            self.stdout.write(self.style.WARNING(f"Mot de passe par défaut: {password}"))
        else:
            password = getpass("Entrez le mot de passe: ")
            password_confirm = getpass("Confirmez le mot de passe: ")

            if password != password_confirm:
                raise CommandError("Les mots de passe ne correspondent pas")

            if len(password) < 6:
                raise CommandError("Le mot de passe doit contenir au moins 6 caractères")

        # Créer le manager
        try:
            manager = Utilisateur.objects.create_user(
                email=email,
                password=password,
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                role='manager',
                is_staff=True,
                is_superuser=False
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Manager créé avec succès !\n"
                    f"Email: {manager.email}\n"
                    f"Nom complet: {manager.nom_complet}\n"
                    f"Rôle: {manager.role}"
                )
            )
            
        except Exception as e:
            raise CommandError(f"Erreur lors de la création du manager: {str(e)}")