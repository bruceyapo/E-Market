from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib import messages
import requests

from authentifications.models import UserProfile, Utilisateur, client
from boutique.forms import ReviewForm
from boutique.models import Negotiation, Produit, ReviewRating
from categorie.models import CategorieProduit
from commande.models import OrderProduct
from panier.models import CartItem
from panier.views import _cart_id

# Create your views here.
def store(request, category_slug=None):
    
    if request.user.is_authenticated:
    # Récupérer l'utilisateur connecté
        utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
        # Utiliser la clé étrangère pour récupérer le client associé
        clients = get_object_or_404(client, IdUtilisateur=utilisateur)
        categories = None
        products = None
        
        if category_slug!= None:
            categories = get_object_or_404(CategorieProduit, slug= category_slug)
            
            products = Produit.objects.all().filter(IdCategorie=categories, is_available=True)
            paginator = Paginator(products, 12)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()
        else:
            products = Produit.objects.all().filter(is_available=True)
            paginator = Paginator(products, 12)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()
        context ={
            "products": paged_products,
            "product_count": product_count,
            "categories": categories,
            "clients": clients,
            "utilisateur": utilisateur,
            }
        return render(request, 'shopping/store/store.html', context)
    else:
        categories = None
        products = None
        
        if category_slug!= None:
            categories = get_object_or_404(CategorieProduit, slug= category_slug)
            
            products = Produit.objects.all().filter(IdCategorie=categories, is_available=True)
            paginator = Paginator(products, 12)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()
        else:
            products = Produit.objects.all().filter(is_available=True)
            paginator = Paginator(products, 12)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()
        context ={
            "products": paged_products,
            "product_count": product_count,
            "categories": categories,
            }
        return render(request, 'shopping/store/store.html', context)



# def chatbot_negotiation(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Negotiation, id=product_id)
        user_response = request.POST.get('user_response')

        # Logique de négociation
        reduction_steps = [0.05, 0.10, 0.08, 0.12, 0.15]
        initial_price = product.PrixUnitaire
        current_step = int(request.POST.get('current_step', 0))

        if user_response == 'agree':
            product.PrixNegocie = initial_price * (1 - reduction_steps[current_step])
            product.save()
            return JsonResponse({'status': 'agreed', 'negotiated_price': product.PrixNegocie})
        
        if current_step < len(reduction_steps) - 1:
            next_price = initial_price * (1 - reduction_steps[current_step])
            current_step += 1
            return JsonResponse({'status': 'continue', 'next_price': next_price, 'current_step': current_step})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Négociation échouée'})

    return JsonResponse({'error': 'Invalid request method'})

import joblib
# Charger le modèle de recommandation sauvegardé
cosine_sim, indices, products_df = joblib.load('model/product_recommendation_model.pkl')

def get_recommendations(product_id, cosine_sim=cosine_sim):
    idx = indices[product_id]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:13]  # Recommander les 10 produits les plus similaires
    product_indices = [i[0] for i in sim_scores]
    return products_df.iloc[product_indices]

def product_detail(request, category_slug, product_slug):
    if request.user.is_authenticated:
        # Récupérer l'utilisateur connecté
        utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
        # Utiliser la clé étrangère pour récupérer le client associé
        clients = get_object_or_404(client, IdUtilisateur=utilisateur)
        try:
            single_product = Produit.objects.get(IdCategorie__slug=category_slug, slug=product_slug)
            recommended_products = get_recommendations(single_product.id)
            recommended_product_ids = recommended_products['id'].tolist()
            recommended_products = Produit.objects.filter(id__in=recommended_product_ids)
            recommended_products_count = len(recommended_products)
            negotiation = Negotiation.objects.filter(product = single_product, user = utilisateur, PrixUnitaire = 0)
            if negotiation.exists() :
                print("Cette Negotiation est en cour")
            else:
                negotiationproduct = Negotiation()
                negotiationproduct.product = single_product
                negotiationproduct.user = utilisateur
                negotiationproduct.PrixUnitaire = 0
                negotiationproduct.save()
            in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), negotiation__product=single_product).exists()
        except Exception as e:
            raise e
        if request.user.is_authenticated:
            try:
                orderproduct = OrderProduct.objects.filter(user=clients, product_id=single_product.id).exists()
            except OrderProduct.DoesNotExist:
                orderproduct = None
        else:
            orderproduct = None
        
        reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True).order_by('-updated_at')
        # Récupérer ou créer le UserProfile associé au client
        userprofile = UserProfile.objects.get(user=clients) 
        
        context= {
            "single_product": single_product,
            "in_cart": in_cart,
            'orderproduct':orderproduct,
            'reviews':reviews,
            "clients": clients,
            "utilisateur": utilisateur,
            "userprofile": userprofile,
            "recommended_products":recommended_products,
            'recommended_products_count':recommended_products_count
        }
        return render(request, 'shopping/store/product_detail.html', context)
    else:
        
    
        try:
            single_product = Produit.objects.get(IdCategorie__slug=category_slug, slug=product_slug)
            recommended_products = get_recommendations(single_product.id)
            recommended_product_ids = recommended_products['id'].tolist()
            recommended_products = Produit.objects.filter(id__in=recommended_product_ids)
            recommended_products_count = len(recommended_products)
            negotiation = Negotiation.objects.filter(product = single_product, user = request.user.id, PrixUnitaire = 0)
            if negotiation.exists() :
                print("Cette Negotiation est en cour")
            else:
                negotiationproduct = Negotiation()
                negotiationproduct.product = single_product
                negotiationproduct.user = request.user.id
                negotiationproduct.PrixUnitaire = 0
                negotiationproduct.save()
                
            in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), negotiation__product=single_product).exists()
        except Exception as e:
            raise e
        if request.user.is_authenticated:
            try:
                orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
            except OrderProduct.DoesNotExist:
                orderproduct = None
        else:
            orderproduct = None
        
        reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True).order_by('-updated_at')
        # Récupérer ou créer le UserProfile associé au client
        # userprofile = UserProfile.objects.get(user=clients) 
        
        context= {
            "single_product": single_product,
            "in_cart": in_cart,
            'orderproduct':orderproduct,
            'reviews':reviews,
            'recommended_products':recommended_products,
            'recommended_products_count':recommended_products_count
        }
        return render(request, 'shopping/store/product_detail.html', context)


def search(request):
    products = []
    product_count = 0
    paged_products = []
    keyword = request.GET.get('keyword', '')

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Produit.objects.all().filter(
                (Q(description__icontains=keyword) | Q(Nom__icontains=keyword)) & Q(is_available=True)
            ).order_by('-created_date')
            paginator = Paginator(products, 12)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()
        else:
            products = Produit.objects.all().filter(is_available=True)
            product_count = products.count()
            paginator = Paginator(products, 12)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            # return redirect('store')
    else:
        products = Produit.objects.all().filter(is_available=True)
        product_count = products.count()
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
    context = {
        "products": paged_products,
        "product_count": product_count,
        "keyword": keyword
    }
    
    return render(request, 'shopping/store/store.html', context)
    

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer le client associé
    clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=clients.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'The review has been submitted')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id 
                data.user_id = clients.id
                data.save()
                messages.success(request, 'Your review has been submitted successfully')
                return redirect(url)
            else:
                messages.error(request, 'The review could not be submitted')
                return redirect(url)
    return redirect('store')
        
