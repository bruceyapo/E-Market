from django.urls import path
from . import views
urlpatterns = [
    path("", views.accueiladmin, name='accueiladmin' ),
    path("accueilvendeur/", views.accueilvendeur, name='accueilvendeur' ),
    path("visuels/", views.visuels, name='visuels'),
    path("ventes/", views.ventes, name='ventes'),
    path('stocks/', views.liste_stock, name='liste_stock'),
    # path('modif_stock/<int:produit_id>/', views.modif_stock, name='modif_stock'),
    path('modif_stock/', views.modif_stock, name='modif_stock'),
    path('get_quantite/<int:produitId>/', views.get_quantite, name='get_quantite'),
    # path('get-all-products/', views.get_all_products, name='get_all_products'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('vente/create/', views.ajout_vente, name='ajout_vente'),
    path('get-product-details/<int:product_id>/', views.get_product_details, name='get_product_details'),
    
    # authentification
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path("inscription/Vendeur", views.inscription_vendeur, name='inscription_vendeur'),
    path("inscription/Admin", views.inscription_admin, name='inscription_admin'),
    
]