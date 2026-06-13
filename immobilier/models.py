from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'manager')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('visiteur', 'Visiteur'),
        ('client', 'Client'),
        ('bailleur', 'Bailleur'),
        ('agent', 'Agent'),
        ('manager', 'Manager'),
    ]

    email = models.EmailField(unique=True, verbose_name="Email")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client', verbose_name="Rôle")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_inscription = models.DateTimeField(default=timezone.now)

    # Agent affecté au client (relation client -> agent)
    agent_affecte = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='clients_affectes',
        limit_choices_to={'role': 'agent'},
        verbose_name="Agent affecté"
    )

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.role})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def est_client(self):
        return self.role == 'client'

    @property
    def est_bailleur(self):
        return self.role == 'bailleur'

    @property
    def est_agent(self):
        return self.role == 'agent'

    @property
    def est_manager(self):
        return self.role == 'manager'


class Propriete(models.Model):
    TYPE_CHOICES = [
        ('terrain', 'Terrain'),
        ('batiment', 'Bâtiment'),
        ('appartement', 'Appartement'),
        ('villa', 'Villa'),
        ('commerce', 'Commerce'),
    ]
    USAGE_CHOICES = [
        ('residence', 'Résidence'),
        ('bureau', 'Bureau'),
        ('commerce', 'Commerce'),
        ('agriculture', 'Agriculture'),
    ]
    OPTION_CHOICES = [
        ('location', 'Location'),
        ('vente', 'Vente'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente de validation'),
        ('publiee', 'Publiée'),
        ('retiree', 'Retirée'),
        ('refusee', 'Refusée'),
    ]

    bailleur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE,
        related_name='proprietes',
        limit_choices_to={'role__in': ['bailleur', 'agent']},
        verbose_name="Bailleur/Propriétaire"
    )
    agent_validateur = models.ForeignKey(
        Utilisateur, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='proprietes_validees',
        verbose_name="Agent validateur"
    )
    titre = models.CharField(max_length=200, verbose_name="Titre")
    type_bien = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type de bien")
    usage = models.CharField(max_length=20, choices=USAGE_CHOICES, verbose_name="Usage")
    option = models.CharField(max_length=10, choices=OPTION_CHOICES, verbose_name="Option")
    zone_geographique = models.CharField(max_length=200, verbose_name="Zone géographique")
    superficie = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Superficie (m²)")
    prix = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Prix (FCFA)")
    description = models.TextField(verbose_name="Description")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    est_agence = models.BooleanField(default=False, verbose_name="Annonce de l'agence")

    class Meta:
        verbose_name = "Propriété"
        verbose_name_plural = "Propriétés"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.titre} - {self.get_type_bien_display()} ({self.get_statut_display()})"

    @property
    def photo_principale(self):
        photo = self.photos.first()
        return photo if photo else None


class PhotoPropriete(models.Model):
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='proprietes/', verbose_name="Image")
    legende = models.CharField(max_length=200, blank=True, verbose_name="Légende")
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"

    def __str__(self):
        return f"Photo de {self.propriete.titre}"


class Favori(models.Model):
    client = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE,
        related_name='favoris',
        limit_choices_to={'role': 'client'}
    )
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, related_name='favoris')
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('client', 'propriete')
        verbose_name = "Favori"

    def __str__(self):
        return f"{self.client.nom_complet} ❤ {self.propriete.titre}"


class DemandeVisite(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
    ]

    client = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE,
        related_name='demandes_visite',
        limit_choices_to={'role': 'client'}
    )
    propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, related_name='demandes_visite')
    agent = models.ForeignKey(
        Utilisateur, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='visites_a_traiter',
        limit_choices_to={'role': 'agent'}
    )
    message = models.TextField(blank=True, verbose_name="Message")
    date_souhaitee = models.DateField(null=True, blank=True, verbose_name="Date souhaitée")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    commentaire_agent = models.TextField(blank=True, verbose_name="Commentaire de l'agent")

    class Meta:
        verbose_name = "Demande de visite"
        verbose_name_plural = "Demandes de visite"
        ordering = ['-date_demande']

    def __str__(self):
        return f"Visite {self.propriete.titre} par {self.client.nom_complet} ({self.get_statut_display()})"
