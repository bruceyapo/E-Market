from django.contrib import admin

from myapp.models import CategorieProduit, Utilisateur, Vendeur, client, Adminitrateur

# Register your models here.
class clientModelAdmin(admin.ModelAdmin):
    list_display = ('id','nom', 'prenoms','genre', 'ville', 'telephone')
admin.site.register(client, clientModelAdmin)

class AdminitrateurModelAdmin(admin.ModelAdmin):
    list_display = ('id','nom','prenoms', 'telephone', 'image', 'IdUtilisateur')
admin.site.register(Adminitrateur, AdminitrateurModelAdmin)

class UtilisateurModelAdmin(admin.ModelAdmin):
    list_display = ('id','email','password', 'roles')
admin.site.register(Utilisateur, UtilisateurModelAdmin)

class VendeurModelAdmin(admin.ModelAdmin):
    list_display = ('id','nom', 'prenoms', 'ville', 'telephone', 'image', 'IdUtilisateur')
admin.site.register(Vendeur, VendeurModelAdmin)

class CategorieProduitdModelAdmin(admin.ModelAdmin):
    list_display = ('id','nom')
admin.site.register(CategorieProduit, CategorieProduitdModelAdmin)