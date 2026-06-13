# IMMO-BF — Plateforme de Gestion Immobilière
### Projet Intégrateur L2IT — Université Aube Nouvelle — 2025-2026

---

## 📋 Description
Système web de gestion immobilière pour le Burkina Faso, permettant la mise en relation
entre bailleurs (propriétaires) et clients (locataires/acheteurs), via une agence immobilière.

## 🛠️ Technologies
- **Backend** : Python 3.12 + Django 6.x
- **Base de données** : SQLite (dev) / MySQL 8+ (prod)
- **Architecture** : MVT (Model-View-Template) — équivalent MVC
- **Sécurité** : hashage PBKDF2-SHA256, requêtes préparées (ORM), protection CSRF/XSS

---

## ⚙️ Installation

### 1. Prérequis
```
Python >= 3.12
pip
```

### 2. Installer les dépendances
```bash
pip install django pillow
```

### 3. Cloner / décompresser le projet
```bash
cd immo_project
```

### 4. Appliquer les migrations
```bash
python manage.py migrate
```

### 5. Créer le compte Manager
```bash
python manage.py createsuperuser
# Renseigner : email, nom, prénom, rôle=manager, mot de passe
```

Ou via le shell Django :
```bash
python manage.py shell
>>> from immobilier.models import Utilisateur
>>> Utilisateur.objects.create_user(
...     email='manager@immobf.bf',
...     password='Admin@2026',
...     nom='Administrateur', prenom='Principal',
...     role='manager', is_staff=True, is_superuser=True
... )
```

### 6. Collecter les fichiers statiques (production)
```bash
python manage.py collectstatic
```

### 7. Lancer le serveur de développement
```bash
python manage.py runserver
```
Accéder à : **http://127.0.0.1:8000/**

---

## 👥 Acteurs et accès

| Rôle       | Création         | Accès                              |
|------------|------------------|------------------------------------|
| Visiteur   | —                | Consulter les annonces publiées    |
| Client     | Inscription libre| Favoris, demandes de visite        |
| Bailleur   | Inscription libre| Déposer/gérer ses annonces         |
| Agent      | Par le Manager   | Valider annonces, traiter visites  |
| Manager    | Par le Manager   | Administration complète            |

---

## 🗂️ Structure du projet

```
immo_project/
├── immo_project/          # Configuration Django
│   ├── settings.py
│   └── urls.py
├── immobilier/            # Application principale
│   ├── models.py          # Modèles (Utilisateur, Propriete, Favori, DemandeVisite)
│   ├── views.py           # Vues (logique métier)
│   ├── forms.py           # Formulaires
│   ├── urls.py            # Routage
│   ├── decorators.py      # Contrôle d'accès par rôle
│   ├── admin.py           # Interface d'administration
│   └── tests.py           # 12 tests unitaires
├── templates/immobilier/  # Templates HTML
│   ├── base.html
│   ├── accueil.html
│   ├── client/
│   ├── bailleur/
│   ├── agent/
│   └── manager/
├── static/css/style.css   # CSS (sans framework externe)
├── media/                 # Photos uploadées
├── schema_mysql.sql       # Script SQL pour MySQL
└── README.md
```

---

## ✅ Lancer les tests unitaires
```bash
python manage.py test immobilier --verbosity=2
```
**12 tests — tous passent ✅**

---

## 🔒 Sécurité mise en œuvre
- Mots de passe hachés (PBKDF2-SHA256) — ENF-5
- Requêtes SQL paramétrées via l'ORM Django — ENF-6
- Protection XSS : échappement automatique Django — ENF-7
- Contrôle d'accès par rôle via décorateurs — ENF-8
- Protection CSRF sur tous les formulaires — ENF-6

---

## 📦 Livrables
1. `README.md` — Ce fichier
2. `schema_mysql.sql` — Script SQL de création de la base
3. Code source complet dans `immobilier/`
4. Templates HTML dans `templates/`
