from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Utilisateur, Propriete, PhotoPropriete, Favori, DemandeVisite
from .forms import (
    InscriptionForm, ConnexionForm, ProprieteForm, PhotoForm,
    DemandeVisiteForm, FiltreProprietesForm, UtilisateurAdminForm,
    TraiterDemandeForm
)
from .decorators import client_required, bailleur_required, agent_required, manager_required


# ─────────────────────────────────────────
#  ACCUEIL & AUTH
# ─────────────────────────────────────────

def accueil(request):
    """Page d'accueil : propriétés publiées par catégorie + dernières annonces."""
    proprietes = Propriete.objects.filter(statut='publiee').select_related('bailleur').prefetch_related('photos')
    
    # Filtre
    filtre_form = FiltreProprietesForm(request.GET)
    if filtre_form.is_valid():
        d = filtre_form.cleaned_data
        if d.get('type_bien'):
            proprietes = proprietes.filter(type_bien=d['type_bien'])
        if d.get('usage'):
            proprietes = proprietes.filter(usage=d['usage'])
        if d.get('option'):
            proprietes = proprietes.filter(option=d['option'])
        if d.get('zone'):
            proprietes = proprietes.filter(zone_geographique__icontains=d['zone'])

    dernieres = Propriete.objects.filter(statut='publiee').order_by('-date_creation')[:6]
    locations = proprietes.filter(option='location')[:4]
    ventes = proprietes.filter(option='vente')[:4]

    paginator = Paginator(proprietes, 9)
    page = request.GET.get('page', 1)
    proprietes_page = paginator.get_page(page)

    return render(request, 'immobilier/accueil.html', {
        'proprietes': proprietes_page,
        'dernieres': dernieres,
        'locations': locations,
        'ventes': ventes,
        'filtre_form': filtre_form,
    })


def detail_propriete(request, pk):
    """Fiche détaillée d'une propriété (sans coordonnées bailleur pour visiteurs)."""
    propriete = get_object_or_404(Propriete, pk=pk, statut='publiee')
    est_favori = False
    deja_demande = False

    if request.user.is_authenticated and request.user.est_client:
        est_favori = Favori.objects.filter(client=request.user, propriete=propriete).exists()
        deja_demande = DemandeVisite.objects.filter(client=request.user, propriete=propriete).exists()

    return render(request, 'immobilier/detail_propriete.html', {
        'propriete': propriete,
        'est_favori': est_favori,
        'deja_demande': deja_demande,
        'afficher_contact': request.user.is_authenticated,
    })


def inscription(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.prenom} ! Votre compte a été créé.")
            return redirect('accueil')
    else:
        form = InscriptionForm()
    return render(request, 'immobilier/inscription.html', {'form': form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('tableau_bord')
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue {user.prenom} !")
            next_url = request.GET.get('next', 'tableau_bord')
            return redirect(next_url)
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = ConnexionForm()
    return render(request, 'immobilier/connexion.html', {'form': form})


@login_required
def deconnexion(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('accueil')


@login_required
def tableau_bord(request):
    """Redirige vers le bon tableau de bord selon le rôle."""
    role = request.user.role
    if role == 'client':
        return redirect('client_dashboard')
    elif role == 'bailleur':
        return redirect('bailleur_dashboard')
    elif role == 'agent':
        return redirect('agent_dashboard')
    elif role == 'manager':
        return redirect('manager_dashboard')
    return redirect('accueil')


# ─────────────────────────────────────────
#  MODULE CLIENT
# ─────────────────────────────────────────

@client_required
def client_dashboard(request):
    client = request.user
    favoris_count = Favori.objects.filter(client=client).count()
    visites_count = DemandeVisite.objects.filter(client=client).count()
    visites_recentes = DemandeVisite.objects.filter(client=client).order_by('-date_demande')[:5]
    return render(request, 'immobilier/client/dashboard.html', {
        'favoris_count': favoris_count,
        'visites_count': visites_count,
        'visites_recentes': visites_recentes,
    })


@client_required
def client_favoris(request):
    favoris = Favori.objects.filter(client=request.user).select_related('propriete').prefetch_related('propriete__photos')
    return render(request, 'immobilier/client/favoris.html', {'favoris': favoris})


@client_required
def toggle_favori(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk, statut='publiee')
    favori, created = Favori.objects.get_or_create(client=request.user, propriete=propriete)
    if not created:
        favori.delete()
        messages.info(request, "Retiré des favoris.")
    else:
        messages.success(request, "Ajouté aux favoris !")
    return redirect('detail_propriete', pk=pk)


@client_required
def client_demandes(request):
    demandes = DemandeVisite.objects.filter(client=request.user).select_related('propriete', 'agent')
    return render(request, 'immobilier/client/demandes.html', {'demandes': demandes})


@client_required
def demander_visite(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk, statut='publiee')
    if DemandeVisite.objects.filter(client=request.user, propriete=propriete).exists():
        messages.warning(request, "Vous avez déjà une demande de visite pour cette propriété.")
        return redirect('detail_propriete', pk=pk)

    if request.method == 'POST':
        form = DemandeVisiteForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.client = request.user
            demande.propriete = propriete
            # Affecter l'agent du client si disponible
            demande.agent = request.user.agent_affecte
            demande.save()
            messages.success(request, "Votre demande de visite a été envoyée.")
            return redirect('client_demandes')
    else:
        form = DemandeVisiteForm()
    return render(request, 'immobilier/client/demander_visite.html', {
        'form': form, 'propriete': propriete
    })


# ─────────────────────────────────────────
#  MODULE BAILLEUR
# ─────────────────────────────────────────

@bailleur_required
def bailleur_dashboard(request):
    bailleur = request.user
    proprietes = Propriete.objects.filter(bailleur=bailleur)
    stats = {
        'total': proprietes.count(),
        'en_attente': proprietes.filter(statut='en_attente').count(),
        'publiees': proprietes.filter(statut='publiee').count(),
        'retirees': proprietes.filter(statut='retiree').count(),
    }
    return render(request, 'immobilier/bailleur/dashboard.html', {
        'proprietes': proprietes,
        'stats': stats,
    })


@bailleur_required
def bailleur_ajouter_propriete(request):
    if request.method == 'POST':
        form = ProprieteForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)
        if form.is_valid() and photo_form.is_valid():
            propriete = form.save(commit=False)
            propriete.bailleur = request.user
            propriete.statut = 'en_attente'
            propriete.save()
            if photo_form.cleaned_data.get('image'):
                photo = photo_form.save(commit=False)
                photo.propriete = propriete
                photo.save()
            messages.success(request, "Annonce déposée. Elle sera publiée après validation.")
            return redirect('bailleur_dashboard')
    else:
        form = ProprieteForm()
        photo_form = PhotoForm()
    return render(request, 'immobilier/bailleur/formulaire_propriete.html', {
        'form': form, 'photo_form': photo_form, 'titre': 'Déposer une annonce'
    })


@bailleur_required
def bailleur_modifier_propriete(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk, bailleur=request.user)
    if request.method == 'POST':
        form = ProprieteForm(request.POST, instance=propriete)
        photo_form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if photo_form.is_valid() and photo_form.cleaned_data.get('image'):
                photo = photo_form.save(commit=False)
                photo.propriete = propriete
                photo.save()
            messages.success(request, "Annonce modifiée avec succès.")
            return redirect('bailleur_dashboard')
    else:
        form = ProprieteForm(instance=propriete)
        photo_form = PhotoForm()
    return render(request, 'immobilier/bailleur/formulaire_propriete.html', {
        'form': form, 'photo_form': photo_form, 'titre': 'Modifier l\'annonce', 'propriete': propriete
    })


@bailleur_required
def bailleur_supprimer_propriete(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk, bailleur=request.user)
    if request.method == 'POST':
        propriete.delete()
        messages.success(request, "Annonce supprimée.")
    return redirect('bailleur_dashboard')


# ─────────────────────────────────────────
#  MODULE AGENT
# ─────────────────────────────────────────

@agent_required
def agent_dashboard(request):
    agent = request.user
    annonces_attente = Propriete.objects.filter(statut='en_attente').count()
    clients = Utilisateur.objects.filter(agent_affecte=agent)
    visites = DemandeVisite.objects.filter(agent=agent, statut='en_attente').count()
    return render(request, 'immobilier/agent/dashboard.html', {
        'annonces_attente': annonces_attente,
        'clients': clients,
        'visites_en_attente': visites,
    })


@agent_required
def agent_annonces_attente(request):
    annonces = Propriete.objects.filter(statut='en_attente').select_related('bailleur').prefetch_related('photos')
    return render(request, 'immobilier/agent/annonces_attente.html', {'annonces': annonces})


@agent_required
def agent_valider_annonce(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'valider':
            propriete.statut = 'publiee'
            propriete.agent_validateur = request.user
            propriete.save()
            messages.success(request, f"Annonce « {propriete.titre} » publiée.")
        elif action == 'refuser':
            propriete.statut = 'refusee'
            propriete.save()
            messages.warning(request, f"Annonce « {propriete.titre} » refusée.")
    return redirect('agent_annonces_attente')


@agent_required
def agent_clients(request):
    clients = Utilisateur.objects.filter(agent_affecte=request.user)
    return render(request, 'immobilier/agent/clients.html', {'clients': clients})


@agent_required
def agent_visites(request):
    visites = DemandeVisite.objects.filter(
        agent=request.user
    ).select_related('client', 'propriete')
    return render(request, 'immobilier/agent/visites.html', {'visites': visites})


@agent_required
def agent_traiter_visite(request, pk):
    visite = get_object_or_404(DemandeVisite, pk=pk, agent=request.user)
    if request.method == 'POST':
        form = TraiterDemandeForm(request.POST, instance=visite)
        if form.is_valid():
            v = form.save(commit=False)
            v.date_traitement = timezone.now()
            v.save()
            messages.success(request, "Demande de visite traitée.")
            return redirect('agent_visites')
    else:
        form = TraiterDemandeForm(instance=visite)
    return render(request, 'immobilier/agent/traiter_visite.html', {'form': form, 'visite': visite})


@agent_required
def agent_ajouter_propriete(request):
    """Agent peut ajouter une propriété d'agence sans validation."""
    if request.method == 'POST':
        form = ProprieteForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)
        if form.is_valid() and photo_form.is_valid():
            propriete = form.save(commit=False)
            propriete.bailleur = request.user
            propriete.statut = 'publiee'
            propriete.est_agence = True
            propriete.agent_validateur = request.user
            propriete.save()
            if photo_form.cleaned_data.get('image'):
                photo = photo_form.save(commit=False)
                photo.propriete = propriete
                photo.save()
            messages.success(request, "Propriété d'agence publiée directement.")
            return redirect('agent_dashboard')
    else:
        form = ProprieteForm()
        photo_form = PhotoForm()
    return render(request, 'immobilier/bailleur/formulaire_propriete.html', {
        'form': form, 'photo_form': photo_form, 'titre': "Ajouter une propriété d'agence"
    })


# ─────────────────────────────────────────
#  MODULE MANAGER
# ─────────────────────────────────────────

@manager_required
def manager_dashboard(request):
    from django.db.models.functions import TruncMonth
    
    stats = {
        'total_proprietes': Propriete.objects.count(),
        'en_attente': Propriete.objects.filter(statut='en_attente').count(),
        'publiees': Propriete.objects.filter(statut='publiee').count(),
        'total_clients': Utilisateur.objects.filter(role='client').count(),
        'total_bailleurs': Utilisateur.objects.filter(role='bailleur').count(),
        'total_agents': Utilisateur.objects.filter(role='agent').count(),
        'visites_total': DemandeVisite.objects.count(),
    }

    # Visites par mois (6 derniers mois)
    visites_par_mois = (
        DemandeVisite.objects
        .annotate(mois=TruncMonth('date_demande'))
        .values('mois')
        .annotate(total=Count('id'))
        .order_by('mois')[:6]
    )

    # Propriétés par type
    par_type = (
        Propriete.objects
        .values('type_bien')
        .annotate(total=Count('id'))
    )

    return render(request, 'immobilier/manager/dashboard.html', {
        'stats': stats,
        'visites_par_mois': list(visites_par_mois),
        'par_type': list(par_type),
    })


@manager_required
def manager_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all().order_by('role', 'nom')
    return render(request, 'immobilier/manager/utilisateurs.html', {'utilisateurs': utilisateurs})


@manager_required
def manager_creer_utilisateur(request):
    if request.method == 'POST':
        form = UtilisateurAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur créé.")
            return redirect('manager_utilisateurs')
    else:
        form = UtilisateurAdminForm()
    return render(request, 'immobilier/manager/form_utilisateur.html', {
        'form': form, 'titre': 'Créer un utilisateur'
    })


@manager_required
def manager_modifier_utilisateur(request, pk):
    user = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        form = UtilisateurAdminForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur modifié.")
            return redirect('manager_utilisateurs')
    else:
        form = UtilisateurAdminForm(instance=user)
    return render(request, 'immobilier/manager/form_utilisateur.html', {
        'form': form, 'titre': 'Modifier l\'utilisateur', 'utilisateur': user
    })


@manager_required
def manager_supprimer_utilisateur(request, pk):
    user = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Utilisateur supprimé.")
    return redirect('manager_utilisateurs')


@manager_required
def manager_affecter_client(request, pk):
    client = get_object_or_404(Utilisateur, pk=pk, role='client')
    agents = Utilisateur.objects.filter(role='agent', is_active=True)
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        if agent_id:
            agent = get_object_or_404(Utilisateur, pk=agent_id, role='agent')
            client.agent_affecte = agent
        else:
            client.agent_affecte = None
        client.save()
        messages.success(request, f"{client.nom_complet} affecté(e) à l'agent.")
        return redirect('manager_utilisateurs')
    return render(request, 'immobilier/manager/affecter_client.html', {
        'client': client, 'agents': agents
    })


@manager_required
def manager_retirer_annonce(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk)
    if request.method == 'POST':
        propriete.statut = 'retiree'
        propriete.save()
        messages.success(request, "Annonce retirée.")
    return redirect('manager_dashboard')


@manager_required
def manager_annonces(request):
    annonces = Propriete.objects.all().select_related('bailleur', 'agent_validateur')
    return render(request, 'immobilier/manager/annonces.html', {'annonces': annonces})
