from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Propriete, PhotoPropriete, Favori, DemandeVisite


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('email', 'nom', 'prenom', 'role', 'is_active', 'date_inscription')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'nom', 'prenom')
    ordering = ('nom',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations', {'fields': ('nom', 'prenom', 'telephone', 'role', 'agent_affecte')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'nom', 'prenom', 'role', 'password1', 'password2')}),
    )


class PhotoInline(admin.TabularInline):
    model = PhotoPropriete
    extra = 1


@admin.register(Propriete)
class ProprieteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_bien', 'option', 'statut', 'bailleur', 'date_creation')
    list_filter = ('statut', 'type_bien', 'option', 'usage')
    search_fields = ('titre', 'zone_geographique', 'description')
    inlines = [PhotoInline]


@admin.register(DemandeVisite)
class DemandeVisiteAdmin(admin.ModelAdmin):
    list_display = ('propriete', 'client', 'agent', 'statut', 'date_demande')
    list_filter = ('statut',)
