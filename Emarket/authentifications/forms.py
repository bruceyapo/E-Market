from django import forms
from .models import Adminitrateur, GesteionnaireStock, UserProfile, Utilisateur, Vendeur, client
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
User = get_user_model()
# from django.contrib.auth.models import User
from django.contrib import messages

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="", widget=forms.TextInput(attrs={'autofocus': True}))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'type': 'email', 'name': 'email','class':'form-control', 'placeholder': 'Email'})
        self.fields['password'].label = ''
        self.fields['password'].widget.attrs.update({'placeholder': 'Mot de passe','class':'form-control'})
    
# class VendeurForm(forms.ModelForm):
#     email = forms.EmailField(required=True,widget=forms.EmailInput(
#         {'class': 'form-control'}
#     ))
#     password = forms.CharField(widget=forms.PasswordInput(
#         {'class': 'form-control'}
#     ))
#     confirm_password = forms.CharField(widget=forms.PasswordInput(
#         {'class': 'form-control'}
#     ))

#     class Meta:
#         model = Vendeur
#         fields = ['nom', 'prenoms', 'ville', 'telephone', 'image']
    
#     def __init__(self, *args, **kwargs):
#         super(VendeurForm, self).__init__(*args, **kwargs)
#         self.fields['nom'].widget.attrs.update({'class': 'form-control'})
#         self.fields['prenoms'].widget.attrs.update({'class': 'form-control'})
#         self.fields['ville'].widget.attrs.update({'class': 'form-control'})
#         self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
#         self.fields['image'].widget.attrs.update({'class': 'form-control'})


#     def save(self, commit=True):
#         instance = super(VendeurForm, self).save(commit=False)
        
#         utilisateur = Utilisateur(email=self.cleaned_data['email'], roles='Vendeur')
#         utilisateur.set_password(self.cleaned_data['password'])
        
#         if commit:
#             utilisateur.save()
#             instance.IdUtilisateur = utilisateur
#             instance.save()
        
#         return instance

class VendeurForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
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
    
    def __init__(self, *args, **kwargs):
        super(VendeurForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({'class': 'form-control'})
        self.fields['prenoms'].widget.attrs.update({'class': 'form-control'})
        self.fields['ville'].widget.attrs.update({'class': 'form-control'})
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")

    def save(self, commit=True):
        instance = super(VendeurForm, self).save(commit=False)
        
        utilisateur = Utilisateur(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['email'],  # Utiliser l'email comme username
            roles='Vendeur'
        )
        utilisateur.set_password(self.cleaned_data['password'])
        
        if commit:
            utilisateur.save()
            instance.IdUtilisateur = utilisateur
            instance.save()
        
        return instance
    
    
class VendeurUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Vendeur
        fields = ['nom', 'prenoms', 'ville', 'telephone', 'image']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenoms': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            # Configurez les widgets pour les autres champs si nécessaire.
        }


    def __init__(self, *args, **kwargs):
        super(VendeurUpdateForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.IdUtilisateur:
            self.fields['email'].initial = self.instance.IdUtilisateur.email

    def save(self, commit=True):
        vendeur = super(VendeurUpdateForm, self).save(commit=False)
        if commit:
            utilisateur = vendeur.IdUtilisateur
            utilisateur.email = self.cleaned_data['email']
            utilisateur.save()
            vendeur.save()
        return vendeur
    
   
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
    
    
# class GesteionnaireStockForm(forms.ModelForm):
#     email = forms.EmailField(required=True,widget=forms.EmailInput(
#         {'class': 'form-control'}
#     ))
#     password = forms.CharField(widget=forms.PasswordInput(
#         {'class': 'form-control'}
#     ))
#     confirm_password = forms.CharField(widget=forms.PasswordInput(
#         {'class': 'form-control'}
#     ))

#     class Meta:
#         model = GesteionnaireStock
#         fields = ['nom', 'prenoms', 'telephone', 'image']
    
#     def __init__(self, *args, **kwargs):
#         super(GesteionnaireStockForm, self).__init__(*args, **kwargs)
#         self.fields['nom'].widget.attrs.update({'class': 'form-control'})
#         self.fields['prenoms'].widget.attrs.update({'class': 'form-control'})
#         self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
#         self.fields['image'].widget.attrs.update({'class': 'form-control'})

#     def save(self, commit=True):
#         instance = super(GesteionnaireStockForm, self).save(commit=False)
        
#         utilisateur = Utilisateur(email=self.cleaned_data['email'], roles='GesteionnaireStock')
#         utilisateur.set_password(self.cleaned_data['password'])
        
#         if commit:
#             utilisateur.save()
#             instance.IdUtilisateur = utilisateur
#             instance.save()
        
#         return instance
    
class GesteionnaireStockForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        {'class': 'form-control'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        {'class': 'form-control'}
    ))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        {'class': 'form-control'}
    ))

    class Meta:
        model = GesteionnaireStock
        fields = ['nom', 'prenoms', 'telephone', 'image']
    
    def __init__(self, *args, **kwargs):
        super(GesteionnaireStockForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({'class': 'form-control'})
        self.fields['prenoms'].widget.attrs.update({'class': 'form-control'})
        self.fields['telephone'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")

    def save(self, commit=True):
        instance = super(GesteionnaireStockForm, self).save(commit=False)
        
        utilisateur = Utilisateur(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['email'],  # Utiliser l'email comme username
            roles='GesteionnaireStock'
        )
        utilisateur.set_password(self.cleaned_data['password'])
        
        if commit:
            utilisateur.save()
            instance.IdUtilisateur = utilisateur
            instance.save()
        
        return instance
    
class GestStockUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = GesteionnaireStock
        fields = ['nom', 'prenoms', 'telephone', 'image']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenoms': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super(GestStockUpdateForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.IdUtilisateur:
            self.fields['email'].initial = self.instance.IdUtilisateur.email

    def save(self, commit=True):
        gesteionnairestock = super(GestStockUpdateForm, self).save(commit=False)
        if commit:
            utilisateur = gesteionnairestock.IdUtilisateur
            utilisateur.email = self.cleaned_data['email']
            utilisateur.save()
            gesteionnairestock.save()
        return gesteionnairestock
    


# class ClientRegisterForm(forms.ModelForm):
#     email = forms.EmailField(required=True,widget=forms.EmailInput(
#         {'class': 'form-control'}
#     ))
#     password = forms.CharField(widget=forms.PasswordInput(
#         {'class': 'form-control'}
#     ))
#     confirm_password = forms.CharField(widget=forms.PasswordInput(
#         {'class': 'form-control'}
#     ))

#     class Meta:
#         model = client
#         fields = ['prenoms', 'nom', 'genre']
    
#     def __init__(self, *args, **kwargs):
#         super(ClientRegisterForm, self).__init__(*args, **kwargs)
#         self.fields['nom'].widget.attrs.update({'class': 'form-control'})
#         self.fields['prenoms'].widget.attrs.update({'class': 'form-control'})
#         self.fields['genre'].widget.attrs.update({'class': 'form-control'})

#     def save(self, commit=True):
#         instance = super(ClientRegisterForm, self).save(commit=False)
        
#         utilisateur = Utilisateur(email=self.cleaned_data['email'], roles='Client')
#         utilisateur.set_password(self.cleaned_data['password'])
        
#         if commit:
#             utilisateur.save()
#             instance.IdUtilisateur = utilisateur
#             instance.save()
        
#         return instance
    

Utilisateur = get_user_model()

class ClientRegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        {'class': 'form-control'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        {'class': 'form-control'}
    ))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        {'class': 'form-control'}
    ))

    class Meta:
        model = client
        fields = ['prenoms', 'nom', 'genre']
    
    def __init__(self, *args, **kwargs):
        super(ClientRegisterForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({'class': 'form-control'})
        self.fields['prenoms'].widget.attrs.update({'class': 'form-control'})
        self.fields['genre'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")

    def save(self, commit=True):
        instance = super(ClientRegisterForm, self).save(commit=False)
        
        utilisateur = Utilisateur(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['email'],  # Utiliser l'email comme username
            roles='Client'
        )
        utilisateur.set_password(self.cleaned_data['password'])
        
        if commit:
            utilisateur.save()
            instance.IdUtilisateur = utilisateur
            instance.save()
        
        return instance
    
    
class UserForm(forms.ModelForm):
    class Meta:
        model = client
        fields = ['nom', 'prenoms', 'telephone'] 
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({'placeholder': 'enter your first name', 'class': 'form-control'})
        self.fields['prenoms'].widget.attrs.update({'placeholder': 'enter your last name', 'class': 'form-control'})
        self.fields['telephone'].widget.attrs.update({'placeholder': 'enter your phone number', 'class': 'form-control'})
        
class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid': ("Image file only")}, widget= forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture']
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['address_line_1'].widget.attrs.update({'placeholder': 'enter your address line 1', 'class': 'form-control'})
        self.fields['address_line_2'].widget.attrs.update({'placeholder': 'enter your address line 2', 'class': 'form-control'})
        self.fields['city'].widget.attrs.update({'placeholder': 'enter your city', 'class': 'form-control'})
        self.fields['state'].widget.attrs.update({'placeholder': 'enter your state', 'class': 'form-control'})
        self.fields['country'].widget.attrs.update({'placeholder': 'enter your country', 'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
        
# class ClientRegisterForm(forms.ModelForm):
#     class Meta:
#         model = client
#         fields = ['prenoms', 'nom', 'genre', 'ville', 'telephone', 'image']
#         widgets = {
#             'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
#             'prenoms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénoms'}),
#             'genre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Genre'}),
#             'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
#             'telephone': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Telephone'}),
#             'image': forms.FileInput(attrs={'class': 'form-control'}),
#         }
#         label_suffix = ''
    
#     def __init__(self, *args, **kwargs):
#         super(ClientRegisterForm, self).__init__(*args, **kwargs)
#         if self.instance and self.instance.IdUtilisateur:
#             self.fields['email'].initial = self.instance.IdUtilisateur.email

#     def save(self, commit=True):
#         clients = super(ClientRegisterForm, self).save(commit=False)
#         if commit:
#             utilisateur = clients.IdUtilisateur
#             utilisateur.email = self.cleaned_data['email']
#             utilisateur.save()
#             clients.save()
#         return clients
    
        
        