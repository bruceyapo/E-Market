from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views.decorators.http import require_POST
from .forms import AdminForm, StockUpdateForm, UploadFileForm, VendeurForm,ClientForm,LoginForm, VenteForm
from .models import Adminitrateur, Notification, Utilisateur, Vendeur, client, CategorieProduit, Produit, Vente, Stock
from django.contrib.auth import authenticate, login, logout
# from django.http import HttpResponseRedirect
from django.urls import reverse
# from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
import csv
from django.db.models import QuerySet
import pandas as pd
from django.forms import inlineformset_factory
# from .forms import UploadFileForm, ClientForm, ProduitFormSet
from django.utils import timezone



@login_required(login_url='connexion')
def accueiladmin(request):
    user = request.user
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)

    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    administrateur = get_object_or_404(Adminitrateur, IdUtilisateur=utilisateur)
    # Passer les données à un template pour affichage
    # Récupérer le rôle de l'utilisateur connecté
    # role = request.user.roles  # Supposons que le rôle de l'utilisateur est stocké dans un champ 'roles' de votre modèle Utilisateur

    # context = {
    #     'role': role,
    # }
    context = {
        'utilisateur': utilisateur,
        'administrateur': administrateur,
    }
    print(context)
    
    return render(request, 'app/accueiladmin.html',locals())

@login_required(login_url='connexion')
def accueilvendeur(request):
    user = request.user
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)

    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    vendeur = get_object_or_404(Vendeur, IdUtilisateur=utilisateur)

    context = {
        'utilisateur': utilisateur,
        'vendeur': vendeur,
    }
    print(context)
    return render(request, 'app/accueilvendeur.html',locals())

# Fonction de vue de connexion

@csrf_exempt
def connexion(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                
                 # Redirection en fonction du rôle de l'utilisateur
                
                if user.roles == 'Administratuer':
                    next_url = request.GET.get('next', reverse('accueiladmin'))  # 'home' est le nom de l'URL de la page d'accueil
                    return redirect(next_url)
                    # return redirect('')  # Redirigez vers la page d'accueil après la connexion
                elif user.roles == 'Vendeur':
                    next_url = request.GET.get('next', reverse('accueilvendeur'))  # 'home' est le nom de l'URL de la page d'accueil
                    return redirect(next_url)
                    # return redirect('ventes')  # Remplacez 'seller_dashboard' par le nom de l'URL de votre tableau de bord Vendeur
            else:
                form.add_error(None, "Adresse email ou mot de passe incorrect")
    else:
        form = LoginForm()
    return render(request, 'app/authentification/connexion.html', {'form': form})

# Vue de déconnexion
def deconnexion(request):
    logout(request)
    return redirect('connexion')  # Redirige vers la page de connexion après la déconnexion

@login_required(login_url='connexion')
def inscription_vendeur(request):
    # if request.method == 'POST':
    form = VendeurForm(request.POST, request.FILES)
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']
        # Vérification de l'existence de l'email
        if password and confirm_password and password != confirm_password:
            messages.warning(request,"Les mots de passe ne correspondent pas.")
        elif Utilisateur.objects.filter(email=email).exists():
            messages.warning(request, "Un utilisateur avec cet email existe déjà.")
    
        elif form.is_valid():
            form.save()
            messages.success(request,"Vendeur enregistré avec success")
            form = VendeurForm()
        # Redirection ou autres actions
        # else:
        #     messages.warning(request,"Données d'entrée invalides")
            # form = VendeurForm()
    return render(request, 'app/authentification/inscription_vendeur.html', {'form': form})

# @login_required(login_url='connexion')
def inscription_admin(request):
    form = AdminForm(request.POST, request.FILES)
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']
        # Vérification de l'existence de l'email
        if password and confirm_password and password != confirm_password:
            messages.warning(request,"Les mots de passe ne correspondent pas.")
        elif Utilisateur.objects.filter(email=email).exists():
            messages.warning(request, "Un utilisateur avec cet email existe déjà.")
    
        elif form.is_valid():
            form.save()
            messages.success(request,"Adminitrateur enregistré avec success")
            form = AdminForm()
    return render(request, 'app/authentification/inscription_admin.html', {'form': form})
@login_required(login_url='connexion')
def visuels(request):
    return render(request, 'app/visuels.html')

# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             file = request.FILES['file']

#             # Vérifier si le fichier est un CSV ou Excel
#             if file.name.endswith('.csv'):
#                 # Lire le fichier CSV
#                 data = pd.read_csv(file)
#                 # Convertir le DataFrame en liste de dictionnaires
#                 data_dict = data.to_dict('records')

#                 # Créer des objets Vente à partir des données
#                 for item in data_dict:
#                     Vente.objects.create(
#                         Idvendeur_id=item['Idvendeur'],
#                         Idclient_id=item['Idclient'],
#                         Idproduit_id=item['Idproduit'],
#                         quantiteVendu=item['quantiteVendu'],
#                         MontantTotalVendu=item['MontantTotalVendu'],
#                         date_de_la_vente=item['date_de_la_vente']
#                     )
#             elif file.name.endswith('.xlsx'):
#                 # Lire le fichier Excel
#                 data = pd.read_excel(file)
#                 # Convertir le DataFrame en liste de dictionnaires
#                 data_dict = data.to_dict('records')

#                 # Créer des objets Vente à partir des données
#                 for item in data_dict:
#                     Vente.objects.create(
#                         Idvendeur_id=item['Idvendeur'],
#                         Idclient_id=item['Idclient'],
#                         Idproduit_id=item['Idproduit'],
#                         quantiteVendu=item['quantiteVendu'],
#                         MontantTotalVendu=item['MontantTotalVendu'],
#                         date_de_la_vente=item['date_de_la_vente']
#                     )

#             return redirect('home')  # Rediriger vers la page d'accueil après le téléversement
#     else:
#         form = UploadFileForm()
#     return render(request, 'upload_file.html')

def handle_uploaded_file(file, user_id):
    # IdVendeur=request.user.id
    if file.name.endswith('.csv'):
        data = pd.read_csv(file, sep=";")
    elif file.name.endswith('.xlsx'):
        data = pd.read_excel(file)
    else:
        raise ValueError("Le fichier n'est pas un format supporté. Seuls CSV et Excel sont acceptés.")
    
    df=data.copy()
    # dfName= df[['Name','Gender']]
    # dfName[['prenoms', 'nom']] = dfName['Name'].str.split(' ', n=1, expand=True)
    # dfName.drop(columns=['Name'], inplace=True)
    # for index, row in dfName.iterrows():
    #     # Créer ou récupérer le client
    #     prenoms = row['prenoms']
    #     nom = row['nom']
    #     genre = row['Gender']
    #     client_instance, created_client = client.objects.get_or_create(prenoms=prenoms, nom=nom, genre=genre)   
    for index, row in df.iterrows():
        # Créer ou récupérer le client
        # prenoms, nom = row['Name'].split()
        # genre = row['Gender']
        # client_instance, created_client = client.objects.get_or_create(prenoms=prenoms, nom=nom, genre=genre)
        
        # Split le nom pour obtenir prenoms et nom
        name_parts = row['Name'].split(' ', 1)
        prenoms = name_parts[0]
        nom = name_parts[1] if len(name_parts) > 1 else ''  # Gère les noms sans prénom

        # Créer ou récupérer le client
        client_instance, created = client.objects.get_or_create(
            prenoms=prenoms, 
            nom=nom, 
            defaults={'genre': row['Gender']}
        )
        
        vendeur_instance = Vendeur.objects.get(id=user_id)
        # Créer ou récupérer la catégorie de produit
        categorie, _ = CategorieProduit.objects.get_or_create(nom=row['Type'])
        
        # Créer ou récupérer le produit
        produit, created_produit = Produit.objects.get_or_create(
            Nom=row['Produit'],
            PrixUnitaire=row['Prix'],
            IdCategorie=categorie
        )
        stock, created_stock = Stock.objects.get_or_create(
            IdProduit=produit,
            QuantiteStock=250,
        )
        
         # Créer la vente si le produit, le client et la catégorie n'existent pas déjà
        
        Vente.objects.create(
            IdVendeur=vendeur_instance,  # Vous devez définir l'ID du vendeur approprié
            IdClient=client_instance,
            IdProduit=produit,
            QuantiteVendu=1,  # Vous devez définir la quantité vendue appropriée
            MontantTotal=row['Prix'],
            DateVente=row['Date']
        )


@login_required(login_url='connexion')
def ventes(request):
    user = request.user.id
    print(user)
    # form = UploadFileForm(request.POST, request.FILES)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith('.csv'):
                # Traitement du fichier CSV avec Pandas
                handle_uploaded_file(file, user)
                messages.success(request, "Vente enregistrée avec succès.")
                return render(request, 'app/ventes.html', {'form': form})

            elif file.name.endswith(('.xlsx', '.xls')):
                # Traitement du fichier Excel avec Pandas
                handle_uploaded_file(file, user)
                messages.success(request, "Vente enregistrée avec succès.")
                return render(request, 'app/ventes.html', {'form': form})

            else:
                messages.warning(request, 'Le fichier doit être au format CSV ou excel')
    else:
        form = UploadFileForm()
    ventes = Vente.objects.all().select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
    nombre_total_ventes = ventes.count()
    paginator = Paginator(ventes, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    ventes = paginator.get_page(page_number)
    return render(request, 'app/ventes.html', {'form': form, 'ventes':ventes, 'nombre_total_ventes':nombre_total_ventes})



ProduitFormSet = inlineformset_factory(client, Vente, form=VenteForm, extra=1)

def ajout_vente(request):
    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        if client_form.is_valid():
            new_client = client_form.save()
            id_vendeur = request.user.id
            produit_formset = ProduitFormSet(request.POST, instance=new_client)
            if produit_formset.is_valid():
                instances = produit_formset.save(commit=False)
                for instance in instances:
                    produit = instance.IdProduit
                    instance.MontantTotal = produit.PrixUnitaire * instance.QuantiteVendu
                    instance.DateVente = timezone.now()
                    instance.IdVendeur_id = id_vendeur
                    instance.save()
                return redirect('ventes')  # Assurez-vous d'avoir une URL nommée 'ventes_list'
    else:
        client_form = ClientForm()
        produit_formset = ProduitFormSet()
    return render(request, 'app/ajout_vente.html', {'client_form': client_form, 'produit_formset': produit_formset})

def get_product_details(request, product_id):
    product = Produit.objects.get(id=product_id)
    return JsonResponse({
        'id': product.id,
        'category': product.IdCategorie.nom,
        'price': product.PrixUnitaire
    })


def liste_stock(request):
    stocks = Stock.objects.all().select_related('IdProduit', 'IdProduit__IdCategorie')
    notifications = Notification.objects.filter(est_lu=False)
    paginator = Paginator(stocks, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    stocks = paginator.get_page(page_number)
    return render(request, 'app/liste_stock.html', {'stocks': stocks, 'notifications':notifications})



@require_POST
def mark_notification_as_read(request, notification_id):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    notification = get_object_or_404(Notification, id=notification_id)  # Assurez-vous que la notification appartient à l'utilisateur
    notification.est_lu = True
    notification.save()
    
    return JsonResponse({'success': True})

# def modif_stock(request):
#     if request.method == 'POST':
#         form = StockUpdateForm(request.POST)
#         if form.is_valid():
#             # for produit in form.cleaned_data:
#             #     quantity = form.cleaned_data[produit]
#             #     produit_id = produit.split('_')[1]
                
#             #     stock_item = Stock.objects.get(IdProduit=produit_id)
#             #     stock_item.QuantiteStock = quantity
#             form.save()
            
#             return redirect('liste_stock')  # Remplacez 'home' par l'URL de votre page d'accueil
#     else:
#         form = StockUpdateForm()
    
#     return render(request, 'app/modif_stock.html', {'form': form})

# def modif_stock(request, produit_id):
#     produit = get_object_or_404(Produit, id=produit_id)
#     stock = Stock.objects.get(IdProduit=produit)

#     if request.method == "POST":
#         form = StockUpdateForm(request.POST, instance=stock)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Le stock à été mies à jour avec succès.")
#             return redirect('liste_stock')
#     else:
#         form = StockUpdateForm(instance=stock)
#     return render(request, 'app/modif_stock.html', {'form': form})


# StockFormSet = inlineformset_factory( Stock, form=StockUpdateForm, extra=1 )


# def modif_stock(request):
#     # if request.method == 'POST':
#     #     formset = StockFormSet(request.POST)
#     #     if formset.is_valid():
#     #         formset.save()
#     #         messages.success(request, "Le stock à été mies à jour avec succès.")
#     #         # Rediriger vers une page de confirmation ou vers la liste des stocks
#     #         return redirect('liste_stock')  # Assurez-vous d'avoir une URL nommée 'liste_stock'
#     # else:
#     #     formset = StockFormSet()
#     if request.method == "POST":
#         form = StockUpdateForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('liste_stock')
#     else:
#         form = StockUpdateForm()
    
#     # context = {
#     #     'formset': formset,
#     # }
#     return render(request, 'app/modif_stock.html', {'form': form})

def modif_stock(request):
    if request.method == 'POST':
        form_data = request.POST
        produit_keys = [key for key in form_data.keys() if key.startswith('produit_')]
        
        for key in produit_keys:
            produit_id = form_data[key]
            quantite_key = key.replace('produit_', 'quantite_')
            quantite = form_data[quantite_key]
            
            if produit_id and quantite:
                produit = Produit.objects.get(pk=produit_id)
                Stock.objects.update_or_create(
                    IdProduit=produit,
                    defaults={'QuantiteStock': quantite, 'Date': timezone.now()}
                )
        
        return redirect('liste_stock')
    else:
        form = StockUpdateForm()
    return render(request, 'app/modif_stock.html', {'form': form})

def get_quantite(request, produitId):
    try:
        produit = Stock.objects.get(pk=produitId)
        quantite = produit.QuantiteStock
        print("quantite = ",quantite)
        return JsonResponse({'quantite': quantite})
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Produit not found'}, status=404)
    
# def get_all_products(request):
#     products = Produit.objects.all().values('id', 'Nom')
#     return JsonResponse(list(products), safe=False)