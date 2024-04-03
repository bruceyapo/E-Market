from django import forms
from .models import Adminitrateur, Stock, Utilisateur, Vendeur
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import client, Vente, Produit

User = get_user_model()
# from django.contrib.auth.models import User
from django.contrib import messages
class UploadFileForm(forms.Form):
    file = forms.FileField(label='Charger un fichier de vente', widget=forms.FileInput(
            attrs= {'class':'form-control li'}),
            error_messages={'required': ''}
        )
    
class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="", widget=forms.TextInput(attrs={'autofocus': True}))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'type': 'email', 'name': 'email','class':'form-control', 'placeholder': 'Email'})
        self.fields['password'].label = ''
        self.fields['password'].widget.attrs.update({'placeholder': 'Mot de passe','class':'form-control'})
    
class VendeurForm(forms.ModelForm):
    email = forms.EmailField(required=True,widget=forms.EmailInput(
        {'class': 'form-control'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        {'class': 'form-control'}
    ))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        {'class': 'form-control'}
    ))

    class Meta:
        model = Vendeur
        fields = ['nom', 'prenoms', 'ville', 'telephone', 'image']
    
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if Utilisateur.objects.filter(email=email).exists():
    #         raise ValidationError("Un utilisateur avec cet email existe déjà.")
    #     return email
    
    def __init__(self, *args, **kwargs):
        super(VendeurForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({'class': 'form-control'})
        self.fields['prenoms'].widget.attrs.update({'class': 'form-control'})
        self.fields['ville'].widget.attrs.update({'class': 'form-control'})
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

    # def clean(self):
    #     cleaned_data = super().clean()
    #     password = cleaned_data.get("password")
    #     confirm_password = cleaned_data.get("confirm_password")
        
    #     if password != confirm_password:
    #         self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")
        
    #     return cleaned_data

    def save(self, commit=True):
        instance = super(VendeurForm, self).save(commit=False)
        
        utilisateur = Utilisateur(email=self.cleaned_data['email'], roles='Vendeur')
        utilisateur.set_password(self.cleaned_data['password'])
        
        if commit:
            utilisateur.save()
            instance.IdUtilisateur = utilisateur
            instance.save()
        
        return instance

class AdminForm(forms.ModelForm):
    email = forms.EmailField(required=True,widget=forms.EmailInput(
        {'class': 'form-control'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        {'class': 'form-control'}
    ))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        {'class': 'form-control'}
    ))

    class Meta:
        model = Adminitrateur
        fields = ['nom', 'prenoms', 'telephone', 'image']
        
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if Utilisateur.objects.filter(email=email).exists():
    #         raise ValidationError("Un utilisateur avec cet email existe déjà.")
    #     return email
    
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({'class': 'form-control'})
        self.fields['prenoms'].widget.attrs.update({'class': 'form-control'})
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

    # def clean(self):
    #     cleaned_data = super().clean()
    #     password = cleaned_data.get("password")
    #     confirm_password = cleaned_data.get("confirm_password")
        
    #     if password != confirm_password:
    #         self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")
        
    #     return cleaned_data

    def save(self, commit=True):
        instance = super(AdminForm, self).save(commit=False)
        
        utilisateur = Utilisateur(email=self.cleaned_data['email'], roles='Administratuer')
        utilisateur.set_password(self.cleaned_data['password'])
        
        if commit:
            utilisateur.save()
            instance.IdUtilisateur = utilisateur
            instance.save()
        
        return instance
    
    
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
    # def __init__(self, *args, **kwargs):
    #     super(ClientForm, self).__init__(*args, **kwargs)
    #     self.fields['nom'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['prenoms'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['genre'].widget.attrs.update({'class': 'form-control'})
        


class VenteForm(forms.ModelForm):
    MontantTotal = forms.DecimalField(label="", required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly','class': 'form-control'}))
    IdProduit = forms.ModelChoiceField(label="",queryset=Produit.objects.all(), required=True, widget=forms.Select(attrs={'onchange': 'updateProductDetails();'}))

    class Meta:
        model = Vente
        fields = ['IdProduit', 'QuantiteVendu']
    
    def __init__(self, *args, **kwargs):
        super(VenteForm, self).__init__(*args, **kwargs)
        self.fields['IdProduit'].widget.attrs.update({'class': 'form-control', 'placeholder': 'produit'})
        self.fields['QuantiteVendu'].widget.attrs.update({'class': 'form-control', 'placeholder': 'quantité'})
        # self.fields['genre'].widget.attrs.update({'class': 'form-control'})
        
# class StockUpdateForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         super(StockUpdateForm, self).__init__(*args, **kwargs)
        
#         stock_bas = Produit.objects.filter(stock__QuantiteStock__lt=250)
        
#         for produit in stock_bas:
#             self.fields[f'product_{produit.id}'] = forms.IntegerField(
#                 label=produit.Nom,
#                 initial=produit.stock.QuantiteStock,
#                 min_value=0
#             )

# class StockUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Stock
#         fields = ['IdProduit', 'QuantiteStock']
#         widgets = {
#             'IdProduit': forms.Select(attrs={'class': 'form-control'}),
#             'QuantiteStock': forms.NumberInput(attrs={'class': 'form-control'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super(StockUpdateForm, self).__init__(*args, **kwargs)
        
#         # Remplir le champ IdProduit avec les produits existants
#         self.fields['IdProduit'].queryset = Produit.objects.all()
#         self.fields['IdProduit'].label = "Produit"
        
# class StockUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Stock
#         fields = ['QuantiteStock']
#         widgets = {
#             # 'IdProduit': forms.Select(attrs={'class': 'form-control'}),
#             'QuantiteStock': forms.NumberInput(attrs={'class': 'form-control'}),
#         }
# class StockUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Stock
#         fields = ['IdProduit', 'QuantiteStock']
#         widgets = {
#             'IdProduit': forms.Select(attrs={'class': 'form-control'}),
#             'QuantiteStock': forms.NumberInput(attrs={'class': 'form-control'}),
#         }
# StockFormSet = forms.modelformset_factory(
#     Stock, 
#     form=StockUpdateForm, 
#     extra=1  # Nombre initial de formulaires affichés
# )

class StockUpdateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produit_0'] = forms.ModelChoiceField(queryset=Produit.objects.all(), label="Produit", required=True, widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['quantite_0'] = forms.IntegerField(label="Quantité", min_value=0, required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
# class StockUpdateForm(forms.Form):
#     produits = forms.ModelMultipleChoiceField(queryset=Produit.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'produits-select'}))

#     def __init__(self, *args, **kwargs):
#         super(StockUpdateForm, self).__init__(*args, **kwargs)
        
#         for produit in self.fields['produits'].queryset:
#             try:
#                 stock = Stock.objects.get(IdProduit=produit)
#                 self.fields[f'quantite_{produit.id}'] = forms.IntegerField(initial=stock.QuantiteStock, widget=forms.NumberInput(attrs={'class': 'quantite-input', 'data-produit-id': produit.id}))
#             except Stock.DoesNotExist:
#                 self.fields[f'quantite_{produit.id}'] = forms.IntegerField(initial=0, widget=forms.NumberInput(attrs={'class': 'quantite-input', 'data-produit-id': produit.id}))


#     def save(self):
#         quantites = {k.split('_')[1]: v for k, v in self.cleaned_data.items() if 'quantite_' in k}
        
#         for produit_id, quantite in quantites.items():
#             stock, created = Stock.objects.get_or_create(IdProduit_id=produit_id)
#             stock.QuantiteStock = quantite
#             stock.save()