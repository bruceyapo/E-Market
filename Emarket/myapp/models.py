from django.db import models
from django.utils import timezone
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


ROLES_CHOICES= (
    ('Administratuer','Administratuer'),
    ('Vendeur','Vendeur')
)
class Utilisateur(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    # password = models.CharField(max_length=128)
    roles = models.CharField(choices= ROLES_CHOICES, max_length=100)
    USERNAME_FIELD = 'email'
    objects = UtilisateurManager()  # Vous utilisez ici le gestionnaire personnalisé
    # Supprimer les champs first_name et last_name
    first_name = None
    last_name = None
    def __str__(self):
        return self.email
    
class client(models.Model):
    prenoms = models.CharField(max_length=200)
    nom = models.CharField(max_length=50)
    genre = models.CharField(max_length=15)
    ville = models.CharField(max_length=50, null=True)
    telephone = models.IntegerField(default=0, null=True)
    def __str__(self):
        return self.nom
    
class Adminitrateur(models.Model):
    nom = models.CharField(max_length=50)
    prenoms = models.CharField(max_length=200)
    telephone = models.IntegerField(default=0, null=True)
    image = models.ImageField(upload_to='Admin', default='default_profil.png')
    IdUtilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    def __str__(self):
        return self.nom
    
class Vendeur(models.Model):
    nom = models.CharField(max_length=50)
    prenoms = models.CharField(max_length=200)
    ville = models.CharField(max_length=50, null=True)
    telephone = models.IntegerField(default=0, null=True)
    image = models.ImageField(upload_to='Vendeur', default='default_profil.png')
    IdUtilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    def __str__(self):
        return self.nom
    
class CategorieProduit(models.Model):
    nom = models.CharField(max_length=100)
    def __str__(self):
        return self.nom
    
class Produit(models.Model):
    Nom = models.CharField(max_length=100)
    PrixUnitaire = models.FloatField()
    Description = models.TextField(null=True)
    IdCategorie = models.ForeignKey(CategorieProduit, on_delete=models.CASCADE)
    def __str__(self):
        return self.Nom
    
class Vente(models.Model):
    IdVendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE)
    IdClient = models.ForeignKey(client, on_delete=models.CASCADE)
    IdProduit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    QuantiteVendu = models.IntegerField()
    MontantTotal = models.DecimalField(max_digits=10, decimal_places=2)
    DateVente = models.CharField(max_length=100)

    def __str__(self):
        return f"Vente {self.Idvente}"
    
class Stock(models.Model):
    IdProduit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    QuantiteStock = models.IntegerField()
    Date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Stock {self.IdStock}"
    
class Notification(models.Model):
    message = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    est_lu = models.BooleanField(default=False)

    def __str__(self):
        return self.message