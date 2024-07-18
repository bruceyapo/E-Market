from django.urls import path

from authentifications import views

urlpatterns = [
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path("inscription/Vendeur", views.inscription_vendeur, name='inscription_vendeur'),
    path("inscription/Admin", views.inscription_admin, name='inscription_admin'),
    path("inscription/GestionnaireStock", views.inscription_GestionnaireStock, name='inscription_GestionnaireStock'),
    path("inscription/Client", views.inscription_Client, name='inscription_Client'),
    
    
    path("accueiladmin/", views.accueiladmin, name='accueiladmin' ),
    path("accueilvendeur/", views.accueilvendeur, name='accueilvendeur' ),
    path("accueilGestionnaireStock/", views.accueilGestionnaireStock, name='accueilGestionnaireStock' ),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    
    path('orders_detail/<int:order_id>', views.orders_detail, name='orders_detail'),
    
    
]