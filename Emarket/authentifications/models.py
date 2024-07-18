from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class UtilisateurManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        
        if not username:
            raise ValueError('Le username est obligatoire')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superadmin = True
        user.is_active = True
        user.save(using=self._db)
        return user
    

ROLES_CHOICES = (
    ('Administrateur', 'Administrateur'),
    ('Vendeur', 'Vendeur'),
    ('GestionnaireStock', 'GestionnaireStock'),
    ('Client', 'Client')   
)

class Utilisateur(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    roles = models.CharField(choices=ROLES_CHOICES, max_length=100)
    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UtilisateurManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

class client(models.Model):
    prenoms = models.CharField(max_length=200)
    nom = models.CharField(max_length=50)
    genre = models.CharField(max_length=15)
    ville = models.CharField(max_length=50, null=True)
    telephone = models.IntegerField(default=0, null=True)
    image = models.ImageField(upload_to='Client', default='/media/Client/default_profil.png')
    IdUtilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    def __str__(self):
        return self.IdUtilisateur.email

class Vendeur(models.Model):
    nom = models.CharField(max_length=50)
    prenoms = models.CharField(max_length=200)
    ville = models.CharField(max_length=50, null=True)
    telephone = models.IntegerField(default=0, null=True)
    image = models.ImageField(upload_to='Vendeur', default='/media/Vendeur/default_profil.png')
    IdUtilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nom

class GesteionnaireStock(models.Model):
    nom = models.CharField(max_length=50)
    prenoms = models.CharField(max_length=200)
    telephone = models.IntegerField(default=0, null=True)
    image = models.ImageField(upload_to='GesteionnaireStock', default='/media/GesteionnaireStock/default_profil.png')
    IdUtilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    def __str__(self):
        return self.nom

class Adminitrateur(models.Model):
    nom = models.CharField(max_length=50)
    prenoms = models.CharField(max_length=200)
    telephone = models.IntegerField(default=0, null=True)
    image = models.ImageField(upload_to='Admin', default='/media/Admin/default_profil.png')
    IdUtilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nom
    
class UserProfile(models.Model):  
    user            = models.OneToOneField(client, on_delete= models.CASCADE)
    address_line_1  = models.CharField(max_length=100, blank=True)
    address_line_2  = models.CharField(max_length=100, blank=True)
    profile_picture  = models.ImageField(upload_to='userprofile', blank=True)
    city            = models.CharField(max_length=50, blank=True)
    state           = models.CharField(max_length=50, blank=True)
    country         = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.user.nom
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    
    
        