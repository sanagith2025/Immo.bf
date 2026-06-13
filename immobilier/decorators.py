from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Décorateur pour restreindre l'accès selon le rôle."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Veuillez vous connecter.")
                return redirect('connexion')
            if request.user.role not in roles:
                messages.error(request, "Accès non autorisé.")
                return redirect('accueil')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def client_required(view_func):
    return role_required('client')(view_func)


def bailleur_required(view_func):
    return role_required('bailleur')(view_func)


def agent_required(view_func):
    return role_required('agent', 'manager')(view_func)


def manager_required(view_func):
    return role_required('manager')(view_func)
