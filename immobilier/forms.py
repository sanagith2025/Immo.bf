from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Utilisateur, Propriete, PhotoPropriete, DemandeVisite


class InscriptionForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
        min_length=8
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmation'})
    )
    role = forms.ChoiceField(
        choices=[('client', 'Client'), ('bailleur', 'Bailleur')],
        label="Je suis"
    )

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'telephone', 'role']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Téléphone'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return p2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ConnexionForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'autofocus': True})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'})
    )


class ProprieteForm(forms.ModelForm):
    class Meta:
        model = Propriete
        fields = ['titre', 'type_bien', 'usage', 'option', 'zone_geographique',
                  'superficie', 'prix', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': 'Titre de l\'annonce'}),
            'zone_geographique': forms.TextInput(attrs={'placeholder': 'Ex: Ouaga 2000, Secteur 15...'}),
            'superficie': forms.NumberInput(attrs={'placeholder': 'Superficie en m²', 'step': '0.01'}),
            'prix': forms.NumberInput(attrs={'placeholder': 'Prix en FCFA'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Description détaillée...'}),
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = PhotoPropriete
        fields = ['image', 'legende']


class DemandeVisiteForm(forms.ModelForm):
    class Meta:
        model = DemandeVisite
        fields = ['message', 'date_souhaitee']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Message pour l\'agent...'}),
            'date_souhaitee': forms.DateInput(attrs={'type': 'date'}),
        }


class FiltreProprietesForm(forms.Form):
    type_bien = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Propriete.TYPE_CHOICES,
        required=False, label="Type"
    )
    usage = forms.ChoiceField(
        choices=[('', 'Tous les usages')] + Propriete.USAGE_CHOICES,
        required=False, label="Usage"
    )
    option = forms.ChoiceField(
        choices=[('', 'Location ou Vente')] + Propriete.OPTION_CHOICES,
        required=False, label="Option"
    )
    zone = forms.CharField(
        required=False, label="Zone géographique",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Ouaga 2000...'})
    )


class UtilisateurAdminForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mot de passe", widget=forms.PasswordInput(), required=False,
        help_text="Laisser vide pour ne pas changer."
    )
    password2 = forms.CharField(
        label="Confirmer", widget=forms.PasswordInput(), required=False
    )

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'telephone', 'role', 'is_active', 'agent_affecte']

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get('password1')
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
        return user


class TraiterDemandeForm(forms.ModelForm):
    class Meta:
        model = DemandeVisite
        fields = ['statut', 'commentaire_agent']
        widgets = {
            'commentaire_agent': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['statut'].choices = [
            ('validee', 'Valider'),
            ('refusee', 'Refuser'),
        ]
