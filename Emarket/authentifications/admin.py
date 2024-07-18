from django.contrib import admin

from authentifications.models import UserProfile, Utilisateur,client,Vendeur,GesteionnaireStock,Adminitrateur
from django.utils.html import format_html

class UtilisateurModelAdmin(admin.ModelAdmin):
    list_display = ('id','email','password', 'roles', 'username', 'is_active')
admin.site.register(Utilisateur, UtilisateurModelAdmin)

class clientModelAdmin(admin.ModelAdmin):
    list_display = ('id','nom', 'prenoms','genre', 'ville', 'telephone', 'IdUtilisateur')
admin.site.register(client, clientModelAdmin)


class VendeurModelAdmin(admin.ModelAdmin):
    list_display = ('id','nom', 'prenoms', 'ville', 'telephone', 'image', 'IdUtilisateur')
admin.site.register(Vendeur, VendeurModelAdmin)


admin.site.register(GesteionnaireStock)

class AdminitrateurModelAdmin(admin.ModelAdmin):
    list_display = ('id','nom','prenoms', 'telephone', 'image', 'IdUtilisateur')
admin.site.register(Adminitrateur, AdminitrateurModelAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,Object):
        return format_html('<img src="{}" width="30" style= "border-raduis: 50%;" />'.format(Object.profile_picture.url))
    thumbnail.short_description = 'Profile picture'
    list_display = ('user', 'city', 'state', 'country')
    # list_filter = ('city', 'state', 'country')
    # search_fields = ('user__email', 'user__first_name', 'user__last_name')
    # ordering = ('user__email',)

admin.site.register(UserProfile, UserProfileAdmin)
# Register your models here.
