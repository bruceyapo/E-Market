from django.contrib import admin

from myapp.models import Notification, Recu, Vente

# from myapp.models import CategorieProduit, Utilisateur, Vendeur, client, Adminitrateur

# # Register your models here.








# class CategorieProduitdModelAdmin(admin.ModelAdmin):
#     list_display = ('id','nom')
admin.site.register(Vente)
admin.site.register(Notification)
admin.site.register(Recu)