from django.contrib import admin

from categorie.models import CategorieProduit

# Register your models here.
class CategorieModelAdmin(admin.ModelAdmin):
    prepopulated_fields ={'slug': ('nom',)}
    list_display_links = ('slug','nom')
    list_display = ('id','nom', 'slug','cat_image')
admin.site.register(CategorieProduit, CategorieModelAdmin)
