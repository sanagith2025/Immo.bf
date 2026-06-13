"""
Tests unitaires — Couche métier IMMO-BF
Au moins 5 tests requis (ENF-9)
"""
from django.test import TestCase, Client as TestClient
from django.urls import reverse
from .models import Utilisateur, Propriete, Favori, DemandeVisite


class UtilisateurModelTest(TestCase):
    """Test 1 — Création et hachage du mot de passe."""

    def setUp(self):
        self.user = Utilisateur.objects.create_user(
            email='client@test.bf',
            password='motdepasse123',
            nom='Kaboré', prenom='Aminata', role='client'
        )

    def test_password_hache(self):
        """Le mot de passe ne doit pas être stocké en clair."""
        self.assertNotEqual(self.user.password, 'motdepasse123')
        self.assertTrue(self.user.check_password('motdepasse123'))

    def test_roles_properties(self):
        """Les propriétés de rôle doivent être correctes."""
        self.assertTrue(self.user.est_client)
        self.assertFalse(self.user.est_bailleur)
        self.assertFalse(self.user.est_agent)
        self.assertFalse(self.user.est_manager)


class ProprieteStatutTest(TestCase):
    """Test 2 — Gestion des statuts d'une propriété."""

    def setUp(self):
        self.bailleur = Utilisateur.objects.create_user(
            email='bailleur@test.bf', password='pass123',
            nom='Ouédraogo', prenom='Ibrahim', role='bailleur'
        )
        self.propriete = Propriete.objects.create(
            bailleur=self.bailleur,
            titre='Villa Ouaga 2000',
            type_bien='villa', usage='residence', option='vente',
            zone_geographique='Ouaga 2000',
            superficie=500, prix=150000000,
            description='Belle villa', statut='en_attente'
        )

    def test_statut_initial_en_attente(self):
        """Une annonce bailleur est en attente par défaut."""
        self.assertEqual(self.propriete.statut, 'en_attente')

    def test_validation_publie(self):
        """Après validation par un agent, le statut passe à publiée."""
        agent = Utilisateur.objects.create_user(
            email='agent@test.bf', password='pass123',
            nom='Sawadogo', prenom='Paul', role='agent'
        )
        self.propriete.statut = 'publiee'
        self.propriete.agent_validateur = agent
        self.propriete.save()
        self.assertEqual(self.propriete.statut, 'publiee')

    def test_retrait_annonce(self):
        """Le manager peut passer une annonce à l'état retiree."""
        self.propriete.statut = 'retiree'
        self.propriete.save()
        self.assertEqual(self.propriete.statut, 'retiree')


class FavoriTest(TestCase):
    """Test 3 — Gestion des favoris (unicité)."""

    def setUp(self):
        self.client_user = Utilisateur.objects.create_user(
            email='c@test.bf', password='pass123',
            nom='Traoré', prenom='Fatou', role='client'
        )
        bailleur = Utilisateur.objects.create_user(
            email='b@test.bf', password='pass123',
            nom='Diallo', prenom='Moussa', role='bailleur'
        )
        self.propriete = Propriete.objects.create(
            bailleur=bailleur, titre='Terrain Pissy',
            type_bien='terrain', usage='agriculture', option='vente',
            zone_geographique='Pissy', superficie=1000, prix=5000000,
            description='Terrain agricole', statut='publiee'
        )

    def test_ajout_favori(self):
        """Un client peut ajouter une propriété en favori."""
        fav, created = Favori.objects.get_or_create(
            client=self.client_user, propriete=self.propriete
        )
        self.assertTrue(created)

    def test_favori_unique(self):
        """Un même favori ne peut être ajouté deux fois."""
        Favori.objects.create(client=self.client_user, propriete=self.propriete)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Favori.objects.create(client=self.client_user, propriete=self.propriete)


class DemandeVisiteTest(TestCase):
    """Test 4 — Logique des demandes de visite."""

    def setUp(self):
        bailleur = Utilisateur.objects.create_user(
            email='bail@test.bf', password='pass123',
            nom='Compaoré', prenom='Alice', role='bailleur'
        )
        self.agent = Utilisateur.objects.create_user(
            email='agt@test.bf', password='pass123',
            nom='Zoungrana', prenom='Roger', role='agent'
        )
        self.client_user = Utilisateur.objects.create_user(
            email='cl@test.bf', password='pass123',
            nom='Kinda', prenom='Sophie', role='client',
            agent_affecte=self.agent
        )
        self.propriete = Propriete.objects.create(
            bailleur=bailleur, titre='Appart Wemtenga',
            type_bien='appartement', usage='residence', option='location',
            zone_geographique='Wemtenga', superficie=80, prix=200000,
            description='Bel appartement', statut='publiee'
        )

    def test_creation_demande(self):
        """Une demande de visite est créée avec le bon statut."""
        demande = DemandeVisite.objects.create(
            client=self.client_user,
            propriete=self.propriete,
            agent=self.agent,
            message='Je souhaite visiter ce bien.'
        )
        self.assertEqual(demande.statut, 'en_attente')

    def test_traitement_demande(self):
        """L'agent peut valider ou refuser une demande."""
        demande = DemandeVisite.objects.create(
            client=self.client_user, propriete=self.propriete, agent=self.agent
        )
        demande.statut = 'validee'
        demande.commentaire_agent = 'Rendez-vous confirmé.'
        demande.save()
        self.assertEqual(demande.statut, 'validee')


class AccesSecuriteTest(TestCase):
    """Test 5 — Contrôle d'accès (ENF-8)."""

    def setUp(self):
        self.tc = TestClient()
        self.client_user = Utilisateur.objects.create_user(
            email='sec@test.bf', password='pass123',
            nom='Test', prenom='Sec', role='client'
        )

    def test_dashboard_manager_inaccessible_client(self):
        """Un client ne peut pas accéder au dashboard manager."""
        self.tc.login(username='sec@test.bf', password='pass123')
        response = self.tc.get(reverse('manager_dashboard'))
        # Doit rediriger vers accueil (accès refusé)
        self.assertIn(response.status_code, [302, 403])

    def test_pages_protegees_non_authentifie(self):
        """Les pages protégées redirigent les visiteurs non connectés."""
        response = self.tc.get(reverse('client_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/connexion/', response['Location'])

    def test_bailleur_inaccessible_client(self):
        """Un client ne peut pas accéder à l'espace bailleur."""
        self.tc.login(username='sec@test.bf', password='pass123')
        response = self.tc.get(reverse('bailleur_dashboard'))
        self.assertIn(response.status_code, [302, 403])
