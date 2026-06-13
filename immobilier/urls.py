from django.urls import path
from . import views

urlpatterns = [
    # Accueil & Auth
    path('', views.accueil, name='accueil'),
    path('propriete/<int:pk>/', views.detail_propriete, name='detail_propriete'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('tableau-de-bord/', views.tableau_bord, name='tableau_bord'),

    # Client
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('client/favoris/', views.client_favoris, name='client_favoris'),
    path('client/favoris/toggle/<int:pk>/', views.toggle_favori, name='toggle_favori'),
    path('client/demandes/', views.client_demandes, name='client_demandes'),
    path('client/demandes/nouvelle/<int:pk>/', views.demander_visite, name='demander_visite'),

    # Bailleur
    path('bailleur/', views.bailleur_dashboard, name='bailleur_dashboard'),
    path('bailleur/ajouter/', views.bailleur_ajouter_propriete, name='bailleur_ajouter'),
    path('bailleur/modifier/<int:pk>/', views.bailleur_modifier_propriete, name='bailleur_modifier'),
    path('bailleur/supprimer/<int:pk>/', views.bailleur_supprimer_propriete, name='bailleur_supprimer'),

    # Agent
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/annonces/', views.agent_annonces_attente, name='agent_annonces_attente'),
    path('agent/annonces/valider/<int:pk>/', views.agent_valider_annonce, name='agent_valider'),
    path('agent/clients/', views.agent_clients, name='agent_clients'),
    path('agent/visites/', views.agent_visites, name='agent_visites'),
    path('agent/visites/traiter/<int:pk>/', views.agent_traiter_visite, name='agent_traiter_visite'),
    path('agent/ajouter-propriete/', views.agent_ajouter_propriete, name='agent_ajouter_propriete'),

    # Manager
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/utilisateurs/', views.manager_utilisateurs, name='manager_utilisateurs'),
    path('manager/utilisateurs/creer/', views.manager_creer_utilisateur, name='manager_creer_utilisateur'),
    path('manager/utilisateurs/modifier/<int:pk>/', views.manager_modifier_utilisateur, name='manager_modifier_utilisateur'),
    path('manager/utilisateurs/supprimer/<int:pk>/', views.manager_supprimer_utilisateur, name='manager_supprimer_utilisateur'),
    path('manager/utilisateurs/affecter/<int:pk>/', views.manager_affecter_client, name='manager_affecter_client'),
    path('manager/annonces/', views.manager_annonces, name='manager_annonces'),
    path('manager/annonces/retirer/<int:pk>/', views.manager_retirer_annonce, name='manager_retirer_annonce'),
]
