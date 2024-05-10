from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path("", views.accueiladmin, name='accueiladmin' ),
    path("accueilvendeur/", views.accueilvendeur, name='accueilvendeur' ),
    path("accueilGestionnaireStock/", views.accueilGestionnaireStock, name='accueilGestionnaireStock' ),
    path("visuels/", views.visuels, name='visuels'),
    path("calendier_admin/", views.calendier_admin, name='calendier_admin'),
    path("calendier_vendeur/", views.calendier_vendeur, name='calendier_vendeur'),
    path("calendier_gestionnaireStock/", views.calendier_gestionnaireStock, name='calendier_gestionnaireStock'),
    path("ventes/", views.ventes, name='ventes'),
    path('stocks/', views.liste_stock, name='liste_stock'),
    path('liste_vendeur/', views.liste_vendeur, name='liste_vendeur'),
    path('liste_client/', views.liste_client, name='liste_client'),
    path('liste_produit_categorie/', views.liste_produit_categorie, name='liste_produit_categorie'),
    path('AjoutCategoriet/', views.AjoutCategoriet, name='AjoutCategoriet'),
    path('AjoutProduit/', views.AjoutProduit, name='AjoutProduit'),
    path('liste_geststock/', views.liste_geststock, name='liste_geststock'),
    # path('modif_stock/<int:produit_id>/', views.modif_stock, name='modif_stock'),
    path('modif_stock/', views.modif_stock, name='modif_stock'),
    path('get_quantite/<int:produitId>/', views.get_quantite, name='get_quantite'),
    # path('get-all-products/', views.get_all_products, name='get_all_products'),
    
    path('get-client-details/<int:client_id>/', views.get_client_details, name='get_client_details'),
    path('get-product-details/<int:product_id>/', views. get_product_details, name=' get-product-details'),
    
    path('details_vente/<int:recu_id>/', views.details_vente, name='details_vente'),
    path('list_recu/', views.list_recu, name='list_recu'),
    
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('vente/create/', views.ajout_vente, name='ajout_vente'),
    path('imprimer_recu/<int:client_id>/', views.recu_vente, name='recu_vente'),
    path('supprimer_vente/<int:vente_id>/', views.supprimer_vente, name='supprimer_vente'),
    path('supprimer_categorie/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('supprimer_vendeur/<int:vendeur_id>/', views.supprimer_vendeur, name='supprimer_vendeur'),
    path('supprimer_produit/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),
    path('supprimer_geststock/<int:geststock_id>/', views.supprimer_geststock, name='supprimer_geststock'),
    path('categorie/<int:categorie_id>/modifier/', views.modif_categorie, name='modif_categorie'),
    path('produit/<int:produit_id>/modifier/', views.modif_produit, name='modif_produit'),
    path('vendeur/<int:vendeur_id>/modifier/', views.modif_vendeur, name='modif_vendeur'),
    path('geststock/<int:geststock_id>/modifier/', views.modif_geststock, name='modif_geststock'),
    
    
    # authentification
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path("inscription/Vendeur", views.inscription_vendeur, name='inscription_vendeur'),
    path("inscription/Admin", views.inscription_admin, name='inscription_admin'),
    path("inscription/GestionnaireStock", views.inscription_GestionnaireStock, name='inscription_GestionnaireStock'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)