from django import forms
# from .models import Adminitrateur, CategorieProduit, GesteionnaireStock, Stock, Utilisateur, Vendeur
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils import timezone

from categorie.models import CategorieProduit
from .models import client, Vente, Produit
from datetime import date
User = get_user_model()
# from django.contrib.auth.models import User
from django.contrib import messages
class UploadFileForm(forms.Form):
    file = forms.FileField(label='', widget=forms.FileInput(
            attrs= {'class':'form-control li'}),
            error_messages={'required': ''}
        )
    
class VerifClientForm(forms.Form):
    Code = forms.CharField(label='Code', widget=forms.TextInput(
            attrs= {'class':'form-control li', 'placeholder': 'Veuillez entrer le code du client'}),
            error_messages={'required': ''}
        )
    
# class LoginForm(AuthenticationForm):
#     username = forms.EmailField(label="", widget=forms.TextInput(attrs={'autofocus': True}))

#     def __init__(self, request=None, *args, **kwargs):
#         super().__init__(request=request, *args, **kwargs)
#         self.fields['username'].widget.attrs.update({'type': 'email', 'name': 'email','class':'form-control', 'placeholder': 'Email'})
#         self.fields['password'].label = ''
#         self.fields['password'].widget.attrs.update({'placeholder': 'Mot de passe','class':'form-control'})

class ClientForm(forms.ModelForm):
    class Meta:
        model = client
        fields = ['prenoms', 'nom', 'genre']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenoms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénoms'}),
            'genre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Genre'}),
        }
        label_suffix = ''
        
class AjoutCategorieForm(forms.ModelForm):
    class Meta:
        model = CategorieProduit
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la nouvelle Categorie'}),
        }
        


class AjoutProduitForm(forms.ModelForm):
    IdCategorie = forms.ModelChoiceField(label="Categorie",queryset=CategorieProduit.objects.all(), required=True, widget=forms.Select(attrs={'onchange': 'updateProductDetails();'}))
    Description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Description du nouveau produit (facultatif)'
    }))
    class Meta:
        model = Produit
        fields = ['Nom', 'PrixUnitaire','IdCategorie','Description']
    
    def __init__(self, *args, **kwargs):
        super(AjoutProduitForm, self).__init__(*args, **kwargs)
        self.fields['Nom'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom du nouveau produit'})
        self.fields['PrixUnitaire'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Prix du Produit'})
        self.fields['IdCategorie'].widget.attrs.update({'class': 'form-control'})
        self.fields['Description'].widget.attrs.update({'class': 'form-control'})
        
class VenteForm(forms.ModelForm):
    
    IdProduit = forms.ModelChoiceField(label="Produit", queryset=Produit.objects.all(), required=True, widget=forms.Select(attrs={'onchange': 'updateTotalAmount()'}))
   
    class Meta:
        model = Vente
        fields = ['IdProduit', 'QuantiteVendu']
    
    def __init__(self, *args, **kwargs):
        super(VenteForm, self).__init__(*args, **kwargs)
        self.fields['IdProduit'].widget.attrs.update({'class': 'form-control IdProduit', 'placeholder': 'produit'})
        # self.fields['QuantiteVendu'].widget.attrs.update({'class': 'form-control QuantiteVendu', 'placeholder': 'quantité'})
        self.fields['QuantiteVendu'] = forms.IntegerField(label="Quantité", min_value=1, required=True, widget=forms.NumberInput(attrs={'class': 'form-control QuantiteVendu','placeholder': 'quantité'}))
        # self.fields['genre'].widget.attrs.update({'class': 'form-control'})

class StockUpdateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produit_0'] = forms.ModelChoiceField(queryset=Produit.objects.all(), label="Produit", required=True, widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['quantite_0'] = forms.IntegerField(label="Quantité", min_value=0, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class DateForm(forms.Form):
    # Liste des mois au format (valeur, libellé)
    MONTH_CHOICES = [
        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
        (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre'),
    ]
    
    # Liste des années à partir de 2021 jusqu'à l'année en cours
    year_range = range(2021, date.today().year + 1)
    YEAR_CHOICES = [('', '---------')] + [(year, year) for year in year_range]

    # Champs pour le mois et l'année
    month = forms.ChoiceField(label='Mois', choices=[('', '---------')], widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(label='Année', choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'].choices = [('', '---------')] + self.MONTH_CHOICES[:date.today().month]
    
    def clean(self):
        cleaned_data = super().clean()
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')
        if month and year:
            # Formater la date comme 'MM/YYYY'
            cleaned_data['date_input'] = f"{month}/{year}"
        return cleaned_data

from django import forms

class PredictionForm(forms.Form):
    YEAR_CHOICES = [('', '---------')] + [(year, year) for year in range(2024, 2041)]
    # Liste des mois au format (valeur, libellé)
    MONTH_CHOICES = [('', '---------')] + [
        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
        (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre'),
    ]
    # MONTH_CHOICES = [(month, month) for month in range(1, 13)]

    # year = forms.ChoiceField(choices=YEAR_CHOICES, label="Année")
    # month = forms.ChoiceField(choices=MONTH_CHOICES, label="Mois")
    # Champs pour le mois et l'année
    month = forms.ChoiceField(label='Mois', choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(label='Année', choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    