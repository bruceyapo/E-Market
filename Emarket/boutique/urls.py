
from django.urls import path
from . import views


urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='product_by_category'),
    path('category/<slug:category_slug>/product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>', views.submit_review, name='submit_review'),
    # path('purchase/<int:product_id>/', views.purchase_page, name='purchase_page'),
    # path('negocier/<int:product_id>/', views.chatbot_negotiation, name='chatbot_negotiation'),
    
]
